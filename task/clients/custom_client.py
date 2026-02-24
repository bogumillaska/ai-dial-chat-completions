import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key" : self._api_key,
            "content-type" : "application/json"
        }
        request_data = {
            "messages" : [msg.to_dict() for msg in messages]
        }
        
        response = requests.post(url=self._endpoint,
                      headers=headers,
                      json=request_data)
        
        if response.status_code == 200:
            data = response.json
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                print(content)
                return Message(Role.AI, content)
            raise ValueError("No choices present in the response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key" : self._api_key,
            "content-type" : "application/json"
        }
        request_data = {
            "stream" : True,
            "messages" : [msg.to_dict() for msg in messages]
        }

        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode("utf-8").strip()
                        if line_str.startswith("data:"):
                            if line_str.startswith("data: [DONE]"):
                                print(contents)
                            else:
                                chunk = self._get_content_snippet(line_str[6:].strip())
                                print(chunk, end='')
                                contents.append(chunk)
                else:
                    print(f"{response.status} {response.text}")
    
        return Message(Role.AI, ''.join(contents))

    def _get_content_snippet(self, data: str) -> str:
        json_data = json.loads(data)
        if choices := json_data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", "")
        return ''

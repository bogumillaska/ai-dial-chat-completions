import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def start(stream: bool) -> None:
    client = DialClient("gpt-4o")
    custom_client = CustomDialClient("gpt-4o")
    system_propmt = Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT)

    conversation = Conversation()
    conversation.add_message(system_propmt)
    
    while True:
        user_input = input("User:").strip()

        if user_input == "exit":
            break
        else:
            conversation.add_message(Message(Role.USER, user_input))
            if stream:
                response = await custom_client.stream_completion(conversation.get_messages())
            else:
                response = custom_client.get_completion(conversation.get_messages())
            
            print(response.content)
            conversation.add_message(Message(Role.AI, response.content))
    
asyncio.run(
    start(True)
)

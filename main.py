import asyncio

from twitchAPI.chat import Chat, ChatMessage, EventData, JoinedEvent
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent

from commands import EventRegisters
from config import Config
from menu import Menu

APP_ID = Config.get_configs()["APP_ID"]
APP_SECRET = Config.get_configs()["APP_SECRET"]
USER_SCOPES = [
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT,
    AuthScope.USER_READ_EMAIL,
    AuthScope.MODERATOR_MANAGE_BANNED_USERS,
]


async def on_ready(ready_event: EventData) -> None:
    print("Bot is running.")
    await ready_event.chat.join_room(Config.get_configs()["TARGET_CHANNEL"])


async def on_message(msg: ChatMessage) -> None:
    pass
    print(f"{msg.user.name}: {msg.text}")


async def on_joined(join_event: JoinedEvent) -> None:
    print(f"Joined {join_event.room_name}'s room")


async def startbot() -> None:
    Config.check()

    twitch: Twitch = await Twitch(APP_ID, APP_SECRET)

    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPES)
    await helper.bind()

    chat: Chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_event(ChatEvent.JOINED, on_joined)
    EventRegisters.register_custom_events(chat)

    chat.start()
    await Menu.startup(twitch=twitch, chat=chat)


if __name__ == "__main__":
    asyncio.run(startbot())

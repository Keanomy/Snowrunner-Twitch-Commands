"""
NEEDED ENVIRONMENT VARIABLES:
"TWITCH_APP_ID"
"TWITCH_APP_SECRET"
"OBS_WS_PASS"
"""

import asyncio
import logging
import os

from twitchAPI.chat import Chat, ChatMessage, EventData, JoinedEvent
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent

from commandRegister import EventRegisters
from config import Config
from obs import OBS
from ui import GUI

APP_ID, APP_SECRET = os.environ.get("TWITCH_APP_ID"), os.environ.get("TWITCH_APP_SECRET")

USER_SCOPES = [
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT,
    AuthScope.USER_READ_EMAIL,
    AuthScope.MODERATOR_MANAGE_BANNED_USERS,
]


async def on_ready(ready_event: EventData) -> None:
    print("Bot is running.")
    await ready_event.chat.join_room(Config.get_config()["TARGET_CHANNEL"])


async def on_message(msg: ChatMessage) -> None:
    logger = logging.getLogger("ChatLog")
    print(f"{msg.user.display_name}: {msg.text}")
    logger.info(f"{msg.user.display_name}: {msg.text}")


async def on_joined(join_event: JoinedEvent) -> None:
    print(f"Joined {join_event.room_name}'s room")


async def startbot() -> None:
    print("\033[33mStarting ...\033[0m")
    Config.setup_logger()
    Config.check()

    obs: OBS = OBS()
    obs.connect()

    twitch: Twitch = await Twitch(APP_ID, APP_SECRET)

    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPES)
    await helper.bind()

    chat: Chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_event(ChatEvent.JOINED, on_joined)
    EventRegisters.register_custom_events(chat, obs)

    chat.start()
    GUI()
    await obs.close()
    await twitch.close()
    chat.stop()


if __name__ == "__main__":
    asyncio.run(startbot())

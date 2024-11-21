import os

from twitchAPI.chat import Chat
from twitchAPI.twitch import Twitch

from config import Config


class Menu:
    async def startup(twitch: Twitch, chat: Chat):
        try:
            user_input = input(
                """
------------------------
Press ENTER to exit
------------------------
"""  # Type MENU for user menu
            )
            if user_input:
                menu_input = await Menu.menu()
                menu_input = menu_input.lower()
                match menu_input:
                    case 1:
                        pass
                        # start_config()
                    case _:
                        pass
        finally:
            Config.save_config()
            chat.stop()
            await twitch.close()

    async def menu() -> str:
        return input(
            r"""
---- MENU ----
NOT YET IMPLEMENTED, EDIT "config.json"
[1] Enter Setup
[9] Quit
--------------
"""
        )

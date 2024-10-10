from random import Random

from twitchAPI.chat import ChatMessage
from twitchAPI.twitch import TwitchUser

from config import Config


class MiscCommands:
    @staticmethod
    async def random_timeout(msg: ChatMessage) -> None:
        rnd: Random = Random()
        target_name: str = msg.text.split()[1]
        async for user in msg.chat.twitch.get_users(
            logins=[msg.room.name, msg.chat.username, target_name]
        ):
            current_user = user.display_name.lower()
            if current_user == msg.user.name.lower():
                sender: TwitchUser = current_user
                print("Sender: ", user.to_dict())
            elif current_user == Config.get_config_key("MOD_ACCOUNT").lower():
                mod: TwitchUser = current_user
                print("Mod:", user.to_dict())
            elif current_user == msg.room.name.lower():
                broadcaster: TwitchUser = current_user
                print("Mod:", user.to_dict())
            elif current_user == target_name.lower():
                target: TwitchUser = current_user
                print("Target: ", user.to_dict())

        random_number: int = rnd.randint(1, 100)
        if random_number <= 2:
            await msg.chat.twitch.ban_user(
                broadcaster.id, mod.id, target.id, f"$Blame {sender.display_name}.", 120
            )
        elif random_number > 80:
            await msg.chat.twitch.ban_user(
                broadcaster.id, mod.id, sender.id, "Stop playing with mod tools.", 120
            )
            msg.reply(f"Do shit, eat shit. Kappa")

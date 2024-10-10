import math
from datetime import datetime
from typing import Awaitable, Callable, Optional

from twitchAPI.chat import ChatCommand
from twitchAPI.chat.middleware import BaseCommandMiddleware

from snowrunner import SRHack


class UserCooldown(BaseCommandMiddleware):
    _last_execution: dict[str, dict[str, datetime]] = {}

    def __init__(self, cooldown_seconds):
        self.cooldown = cooldown_seconds

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if self._last_execution.get(cmd.name) is None:
            return True
        user_last_execution = self._last_execution[cmd.name].get(cmd.user.id)
        if user_last_execution is None:
            return True
        since = (datetime.now() - user_last_execution).total_seconds()
        if since < self.cooldown:
            time_left: float = round(self.cooldown - since)
            if time_left <= 60:
                await cmd.reply(f"Still on cooldown, {round(self.cooldown - since)} seconds left.")
            else:
                sec = round((self.cooldown - since) % 60)
                min = math.floor((self.cooldown - since) / 60)
                await cmd.reply(f"Still on cooldown, {min} min & {sec} sec  left.")

        return since >= self.cooldown

    async def was_executed(self, cmd: ChatCommand) -> None:
        if self._last_execution.get(cmd.name) is None:
            self._last_execution[cmd.name] = {}
            self._last_execution[cmd.name][cmd.user.id] = datetime.now()
            return
        self._last_execution[cmd.name][cmd.user.id] = datetime.now()


class SnowrunnerActive(BaseCommandMiddleware):
    def __init__(
        self, execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None
    ):
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if cmd.name == "fuel":
            return SRHack.Fuel.validate_pointer()
        elif cmd.name == "loadcost":
            return SRHack.Money.validate_pointer()
        else:
            return SRHack.SRUtility.hook_snowrunner()

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass

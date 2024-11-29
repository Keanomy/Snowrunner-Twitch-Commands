import math
from datetime import datetime
from logging import getLogger

from twitchAPI.chat import ChatCommand
from twitchAPI.chat.middleware import BaseCommandMiddleware

import snowrunner.SRHack as SRHack

logger = getLogger("Middleware")


class UserCooldown(BaseCommandMiddleware):
    _last_execution: dict[str, dict[str, datetime]] = {}

    def __init__(self, cooldown_seconds, command):
        self.cooldown = cooldown_seconds
        self.command = command

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if cmd.room.name == cmd.user.name:
            return True
        if self._last_execution.get(self.command) is None:
            return True
        user_last_execution = self._last_execution[self.command].get(cmd.user.id)
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
        if self._last_execution.get(self.command) is None:
            self._last_execution[self.command] = {}
            self._last_execution[self.command][cmd.user.id] = datetime.now()
            return
        self._last_execution[self.command][cmd.user.id] = datetime.now()


class GlobalCooldown(BaseCommandMiddleware):
    _last_execution: dict[str, dict[str, datetime]] = {}

    def __init__(self, cooldown_seconds: int, command: str):
        self.cooldown = cooldown_seconds
        self.command = command

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if cmd.room.name == cmd.user.name:
            return True
        if self._last_execution.get(self.command) is None:
            return True
        last_execution: datetime = self._last_execution.get(self.command)
        since: datetime = (datetime.now() - last_execution).total_seconds()
        return since >= self.cooldown

    async def was_executed(self, cmd: ChatCommand) -> None:
        if self._last_execution.get(self.command) is None:
            self._last_execution[self.command] = datetime.now()
            return
        self._last_execution[self.command] = datetime.now()


class IsRunningSnowrunner(BaseCommandMiddleware):
    def __init__(self, command):
        self.command = command

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if cmd.name == "fuel" and SRHack.SRUtility.hook_snowrunner():
            return (
                SRHack.Fuel.validate_fuel_pointer()
                and SRHack.SRUtility.mem
                and SRHack.Fuel.validate_tank_pointer()
            )
        elif cmd.name == "loadcost" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.LoadCost.validate_pointer() 
        elif self.command == "handbrake" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.Handbrake.validate_pointer() 
        elif self.command == "speed" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.Power.validate_pointer()
        else:
            logger.debug(msg="Snowrunner not running.")
            return SRHack.SRUtility.hook_snowrunner() and SRHack.SRUtility.mem

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass


class IsActiveSnowrunner(BaseCommandMiddleware):
    def __init__(self, execute_blocked_handler, command):
        self.execute_blocked_handler = execute_blocked_handler
        self.command = command

    async def can_execute(self, cmd: ChatCommand) -> bool:
        if self.command == "fuel" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.Fuel.validate_fuel_pointer() and SRHack.SRUtility.mem
        elif self.command == "loadcost" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.LoadCost.validate_pointer() and SRHack.SRUtility.mem
        elif self.command == "handbrake" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.Handbrake.validate_pointer() and SRHack.SRUtility.mem
        elif self.command == "speed" and SRHack.SRUtility.hook_snowrunner():
            return SRHack.Power.validate_pointer() and SRHack.SRUtility.mem
        else:
            logger.debug(msg="Snowrunner not running.")
            return SRHack.SRUtility.hook_snowrunner() and SRHack.SRUtility.mem

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass

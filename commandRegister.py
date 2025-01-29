from functools import partial
from typing import Any, List

from twitchAPI.chat import Chat

import snowrunner.SRCommands as SR
from config import Config
from custommiddleware import *
from obs import OBS
from snowrunner.SRSaveData import post_money, post_save_data


class EventRegisters:
    def register_custom_events(chat: Chat, obs: OBS):
        # Winch
        EventRegisters.winch_command(chat)
        # Speed
        EventRegisters.speed_command(chat, obs)
        # HandBreak
        EventRegisters.handbrake_command(chat)
        # Horn
        EventRegisters.horn_command(chat)
        # Lights
        EventRegisters.lights_command(chat)
        # Post Money
        EventRegisters.postmoney_command(chat)
        # Generic Save
        EventRegisters.genericsave_command(chat)
        # Fuel Roulette
        EventRegisters.sr_fuel_roulette(chat, obs)
        # Fuel Roulette Stats
        EventRegisters.sr_fuel_roulette_stats(chat)

    def genericsave_command(chat: Chat) -> None:
        if Config.get_config()["COMMANDS"]["GenericSave"]:
            chat.register_command(
                "srsave",
                post_save_data,
            )

    def postmoney_command(chat: Chat) -> None:
        if Config.get_config()["COMMANDS"]["PostMoney"]:
            chat.register_command("money", post_money)
            chat.register_command("cash", post_money)

    def lights_command(chat: Chat) -> None:
        basic_cooldown: List[Any] = [IsInControl()]
        if Config.get_config()["COMMANDS"]["Lights"]:
            chat.register_command("lights", SR.lights, basic_cooldown)
            chat.register_command("light", SR.lights, basic_cooldown)

    def horn_command(chat: Chat) -> None:
        basic_cooldown: List[Any] = [IsInControl()]

        if Config.get_config()["COMMANDS"]["Horn"]:
            chat.register_command("horn", SR.horn, basic_cooldown)
            chat.register_command("honk", SR.horn, basic_cooldown)
            chat.register_command("beep", SR.horn, basic_cooldown)
            chat.register_command("hupe", SR.horn, basic_cooldown)
            chat.register_command("tut", SR.horn, basic_cooldown)
            chat.register_command("tööt", SR.horn, basic_cooldown)
            chat.register_command("töötti", SR.horn, basic_cooldown)
            chat.register_command("awooga", SR.horn, basic_cooldown)
            chat.register_command("meep", SR.horn, basic_cooldown)

    def speed_command(chat: Chat, obs: OBS) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(5, "speed"),
            UserCooldown(300, "speed"),
            IsRunningSnowrunner("speed"),
            IsInControl(),
        ]
        if Config.get_config()["COMMANDS"]["Speed"]:
            chat.register_command("speed", partial(SR.speed, obs=obs), basic_cooldown)
            chat.register_command("boost", partial(SR.speed, obs=obs), basic_cooldown)

    def handbrake_command(chat: Chat) -> None:
        basic_cooldown: List[Any] = [
            IsRunningSnowrunner("handbrake"),
        ]
        if Config.get_config()["COMMANDS"]["HandBreak"]:
            chat.register_command("brake", SR.handbrake, basic_cooldown)
            chat.register_command("ebrake", SR.handbrake, basic_cooldown)
            chat.register_command("stop", SR.handbrake, basic_cooldown)
            chat.register_command("handbrake", SR.handbrake, basic_cooldown)

    def winch_command(chat: Chat) -> None:
        basic_cooldown: List[Any] = [
            IsInControl(),
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "winch"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "winch"),
        ]
        if Config.command_is_active("Winch"):
            chat.register_command("winch", SR.winch, basic_cooldown)

    def sr_fuel_roulette(chat: Chat, obs: OBS) -> None:
        if Config.command_is_active("Fuel_Roulette"):
            command_name = "fuel"
            chat.register_command(
                name="fuel",
                handler=partial(SR.fuel_roulette, obs=obs),
                command_middleware=[
                    IsRunningSnowrunner(command_name),
                    GlobalCooldown(10, command_name),
                    UserCooldown(600, command_name),
                ],
            )

    def sr_fuel_roulette_stats(chat: Chat):
        if Config.command_is_active("Fuel_Roulette_Stats"):
            command_name = "fuelstats"
            chat.register_command(
                name="fuelstats",
                handler=SR.fuel_roulette_stats,
                command_middleware=[
                    IsRunningSnowrunner(command_name),
                ],
            )
            chat.register_command(
                name="fs",
                handler=SR.fuel_roulette_stats,
                command_middleware=[
                    IsRunningSnowrunner(command_name),
                ],
            )

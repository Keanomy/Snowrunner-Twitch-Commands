from typing import Any, List

from twitchAPI.chat import Chat

import snowrunner.SRCommands as SR
from config import Config
from custommiddleware import *
from MiscCommands import MiscCommands
from snowrunner.SRSaveData import post_money, post_save_data


class EventRegisters:
    def register_custom_events(chat: Chat):
        # Winch
        EventRegisters.winch_command(chat)
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
        # Timeout Roulette
        EventRegisters.timeout_roulette(chat)
        # Fuel Roulette
        EventRegisters.sr_fuel_roulette(chat)
        # Fuel Roulette Stats
        EventRegisters.sr_fuel_roulette_stats(chat)

    def genericsave_command(chat: Chat) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "srsave"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "srsave"),
        ]
        if Config.get_config()["COMMANDS"]["GenericSave"]:
            chat.register_command("srsave", post_save_data, basic_cooldown)

    def postmoney_command(
        chat: Chat,
    ) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "money"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "money"),
        ]
        if Config.get_config()["COMMANDS"]["PostMoney"]:
            chat.register_command("money", post_money, basic_cooldown)
            chat.register_command("cash", post_money, basic_cooldown)

    def lights_command(
        chat: Chat,
    ) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "lights"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "lights"),
        ]
        if Config.get_config()["COMMANDS"]["Lights"]:
            chat.register_command("lights", SR.lights, basic_cooldown)
            chat.register_command("light", SR.lights, basic_cooldown)

    def horn_command(
        chat: Chat,
    ) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "horn"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "horn"),
        ]

        if Config.get_config()["COMMANDS"]["Horn"]:
            chat.register_command("horn", SR.horn, basic_cooldown)
            chat.register_command("honk", SR.horn, basic_cooldown)
            chat.register_command("beep", SR.horn, basic_cooldown)
            chat.register_command("hupe", SR.horn, basic_cooldown)
            chat.register_command("tut", SR.horn, basic_cooldown)
            chat.register_command("tööt", SR.horn, basic_cooldown)
            chat.register_command("töötti", SR.horn, basic_cooldown)

    def handbrake_command(
        chat: Chat,
    ) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "brake"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "brake"),
        ]

        if Config.get_config()["COMMANDS"]["HandBreak"]:
            chat.register_command("brake", SR.handbrake, basic_cooldown)
            chat.register_command("ebrake", SR.handbrake, basic_cooldown)
            chat.register_command("stop", SR.handbrake, basic_cooldown)
            chat.register_command("handbrake", SR.handbrake, basic_cooldown)

    def winch_command(
        chat: Chat,
    ) -> None:
        basic_cooldown: List[Any] = [
            GlobalCooldown(Config.get_config()["CHANNEL_COOLDOWN"], "winch"),
            UserCooldown(Config.get_config()["USER_COOLDOWN"], "winch"),
        ]
        if Config.command_is_active("Winch"):
            chat.register_command("winch", SR.winch, basic_cooldown)

    def timeout_roulette(chat: Chat) -> None:
        if Config.command_is_active("Timeout_Roulette"):
            chat.register_command("timeout", MiscCommands.random_timeout)
            chat.register_command("ban", MiscCommands.random_timeout)

    def sr_fuel_roulette(chat: Chat) -> None:
        if Config.command_is_active("Fuel_Roulette"):
            chat.register_command(
                name="fuel",
                handler=SR.fuel_roulette,
                command_middleware=[
                    UserCooldown(600, "fuel"),
                    IsRunningSnowrunner(),
                ],
            )

    def sr_fuel_roulette_stats(chat: Chat):
        if Config.command_is_active("Fuel_Roulette_Stats"):

            chat.register_command(
                name="fuelstats",
                handler=SR.fuel_roulette_stats,
                command_middleware=[
                    IsRunningSnowrunner(),
                ],
            )
            chat.register_command(
                name="fs",
                handler=SR.fuel_roulette_stats,
                command_middleware=[
                    IsRunningSnowrunner(),
                ],
            )

from twitchAPI.chat import Chat
from twitchAPI.chat.middleware import ChannelCommandCooldown, ChannelUserCommandCooldown

import snowrunner.SRCommands as SR
from config import Config
from custommiddleware import *
from MiscCommands import MiscCommands
from snowrunner.SRSaveData import post_money, post_save_data


class EventRegisters:
    def register_custom_events(chat: Chat):
        basic_cooldown = [
            ChannelCommandCooldown(Config.get_configs()["CHANNEL_COOLDOWN"]),
            UserCooldown(Config.get_configs()["USER_COOLDOWN"]),
        ]
        # Winch
        EventRegisters.winch_command(chat, basic_cooldown)

        # HandBreak
        EventRegisters.handbrake_command(chat, basic_cooldown)

        # Horn
        EventRegisters.horn_command(chat, basic_cooldown)

        # Lights
        EventRegisters.lights_command(chat, basic_cooldown)

        # Post Money
        EventRegisters.postmoney_command(chat, basic_cooldown)

        # Generic Save
        EventRegisters.genericsave_command(chat, basic_cooldown)

        # Timeout Roulette
        EventRegisters.timeout_roulette(chat)

        # Fuel Roulette
        EventRegisters.sr_fuel_roulette(chat)

    def genericsave_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
        if Config.get_configs()["COMMANDS"]["GenericSave"]:
            chat.register_command("srsave", post_save_data, basic_cooldown)

    def postmoney_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
        if Config.get_configs()["COMMANDS"]["PostMoney"]:
            chat.register_command("money", post_money, basic_cooldown)
            chat.register_command("cash", post_money, basic_cooldown)

    def lights_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
        if Config.get_configs()["COMMANDS"]["Lights"]:
            chat.register_command("lights", SR.lights, basic_cooldown)

    def horn_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
        if Config.get_configs()["COMMANDS"]["Horn"]:
            chat.register_command("horn", SR.handbrake, basic_cooldown)
            chat.register_command("honk", SR.handbrake, basic_cooldown)
            chat.register_command("beep", SR.handbrake, basic_cooldown)

    def handbrake_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
        if Config.get_configs()["COMMANDS"]["HandBreak"]:
            chat.register_command("brake", SR.handbrake, basic_cooldown)
            chat.register_command("ebrake", SR.handbrake, basic_cooldown)
            chat.register_command("stop", SR.handbrake, basic_cooldown)
            chat.register_command("handbrake", SR.handbrake, basic_cooldown)

    def winch_command(
        chat: Chat,
        basic_cooldown: list[ChannelCommandCooldown | ChannelUserCommandCooldown],
    ) -> None:
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
                    UserCooldown(600),
                    SnowrunnerActive(),
                ],
            )

import os
import subprocess
from logging import Logger, getLogger
from random import Random

from pygetwindow import getActiveWindowTitle
from twitchAPI.chat import ChatCommand
from twitchAPI.helper import first
from twitchAPI.twitch import TwitchUser

import snowrunner.SRHack as SRHack

# fuel_stats: dict[str, dict[str, float]] = {
#     "90476414": {"take": 300.0, "give": 425.0},
#     "47592275": {"take": 101.0, "give": 52.0},
#     "695428901": {"take": 0, "give": 41.0},
#     "117914050": {"take": 250.0, "give": 250.0},
#     "69563919": {"take": 0, "give": 28.0},
#     "772056584": {"take": 179.0, "give": 231.0},
#     "40455306": {"take": 39.0, "give": 38.0},
#     "106802668": {"take": 0, "give": 28.0},pip
# }


fuel_stats: dict[str, dict[str, float]] = {}
logger: Logger = getLogger("SnowRunner.Commands")
ahk_exe: str = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"


async def winch(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        script: str = os.path.abspath(r"ahk\Winch.ahk")
        subprocess.call([ahk_exe, script])
        print(f"Activated winch.")


async def handbrake(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        script: str = os.path.abspath(r"ahk\Break.ahk")
        subprocess.call([ahk_exe, script])
        print(f"Activated handbrake.")


async def lights(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        script: str = os.path.abspath(r"ahk\Light.ahk")
        subprocess.call([ahk_exe, script])
        print(f"Toggled lights.")


async def horn(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        script: str = os.path.abspath(r"ahk\Horn.ahk")
        subprocess.call([ahk_exe, script])
        print(f"Activated horn.")


async def fuel_roulette(cmd: ChatCommand) -> None:
    max_fuel: float = 50  # MAX FUEL ALLOWED

    if len(cmd.text.split()) > 1 and cmd.text.split()[1].isnumeric():
        fuel: float = float(cmd.text.split()[1])  # CHECK IF SECOND VARIABLE IS A NUMBER
        if abs(fuel) > max_fuel:  # IF FUEL IS ABOVE 50, SET TO 50
            fuel: float = max_fuel
    else:  # NO FUEL, DRAW RANDOM AMOUNT
        fuel: float = float(Random().randint(25, 50))

    # CHECK IF FUEL TANK IS > 140 AND FUEL IS ABOVE 25 IF SO DIVIDE BY 2
    if SRHack.Fuel.get_tank_size() < 140 and abs(fuel) > 25:
        fuel /= 2

    fuel: float = Random().choice([fuel, -fuel])  # RANDOMIZE ADDING OR REMOVING
    current_fuel: float | None = SRHack.Fuel.get_current_fuel()  # GET CURRENT FUEL
    if current_fuel == None:
        print("fuck.")  # WE FUCKED UP
        return

    act_fuel: float = current_fuel - fuel
    if act_fuel < 0:
        act_fuel: float = 0

    SRHack.Fuel.set_current_fuel(float(act_fuel))
    print(f"Original fuel: {current_fuel}, New: {act_fuel} added/removed: {-fuel}.")
    logger.debug(
        f"USER: {cmd.user.id} - Original fuel: {current_fuel}, New: {act_fuel} added/removed: {-fuel}."
    )

    if fuel_stats.get(cmd.user.id) is None:
        fuel_stats[cmd.user.id] = {"take": 0, "give": 0}

    if fuel > 0:
        await cmd.reply(f"{cmd.user.display_name} stole {round(abs(fuel))} fuel. FeelsGoodMan")
        fuel_stats.get(cmd.user.id)["take"] += abs(fuel)
    elif fuel < 0:
        await cmd.reply(f"{cmd.user.display_name} gave {round(abs(fuel))} fuel. Kappa")
        fuel_stats.get(cmd.user.id)["give"] += abs(fuel)
        logger.info(f"{cmd.user.id}:{cmd.user.name} Fuel: {round(abs(fuel))}")
    else:
        await cmd.reply(
            f"{cmd.user.display_name} wasted the cooldown, gambling {fuel} fuel for nothing. NotLikeThis"
        )


async def fuel_roulette_stats(cmd: ChatCommand):
    id: str = cmd.user.id
    param: str = cmd.parameter.split(" ", 1)[0].removeprefix("@")
    if param != "":
        if param.lower() == "all":
            await total_fuel_roulette_stats(cmd)
            return
        print(param)
        target: TwitchUser = await first(cmd.chat.twitch.get_users(logins=[param]))
        if target == None:
            await cmd.reply(f"{cmd.user.display_name}, that user doesn't exist.")
            return
        else:
            id = target.id
    else:
        target = cmd.user
    stats: dict[str, float] = fuel_stats.get(id)
    if target.display_name != cmd.user.display_name:
        if stats:
            message = f"{target.display_name} has contributed {round(stats.get("give"))}L & stolen {round(stats.get("take"))}L, Total: {round(stats.get("give")-stats.get("take"))}L not bad!"
        else:
            message = f"{target.display_name} hasn't used the !fuel command yet."
    else:
        if stats:
            message = f"You've given {round(stats.get("give"))}L & stolen {round(stats.get("take"))}L, Total: {round(stats.get("give")-stats.get("take"))}L not bad!"
        else:
            message = f"You've have not used the !fuel command yet."
    await cmd.reply(str(message))


async def total_fuel_roulette_stats(cmd: ChatCommand):
    give: float = 0.0
    take: float = 0.0

    for value in fuel_stats.values():
        give += value["give"]
        take += value["take"]
    if give < take:
        message = f"Total: {abs(give) - abs(take)}L, collectively we lost {abs(take)}L and gained {abs(give)}L fuel. SPARE ME!! BigSad"
    else:
        message = f"Total: +{abs(give) - abs(take)}L, collectively we gained {abs(give)}L and lost {abs(take)}L fuel. Thank you! TwitchConHYPE"
    await cmd.reply(message)

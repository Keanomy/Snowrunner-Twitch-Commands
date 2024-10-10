from random import Random

from pygetwindow import getActiveWindowTitle
from twitchAPI.chat import ChatCommand

import snowrunner.SRHack as SRHack


async def winch(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        # Winch command here
        print(f"Activated winch.")


async def handbrake(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        # keyboard.tap(Key.space)
        print(f"Activated handbrake.")


async def lights(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        # keyboard.tap("l")
        print(f"Toggeled lights.")


async def horn(cmd: ChatCommand) -> None:
    if "snowrunner" in str.lower(getActiveWindowTitle()):
        # keyboard.tap("g")
        print(f"Activated horn.")


async def fuel_roulette(cmd: ChatCommand) -> None:
    max_fuel: float = 50
    if len(cmd.text.split()) > 1 and cmd.text.split()[1].isnumeric():

        fuel: float = float(cmd.text.split()[1])
        if abs(fuel) > max_fuel:
            fuel: float = max_fuel
    else:
        fuel: float = float(Random().randint(25, 50))
    fuel: int = Random().choice([fuel, -fuel])
    current_fuel: float | None = SRHack.Fuel.get_current_fuel()
    if current_fuel == None:
        print("fuck.")
        return
    act_fuel: float = current_fuel - fuel

    if act_fuel < 0:
        act_fuel: float = 0
    SRHack.Fuel.set_current_fuel(float(act_fuel))
    print(f"Original fuel: {current_fuel}, New: {act_fuel} added/removed: {fuel}.")
    if fuel > 0:
        await cmd.reply(f"{cmd.user.display_name} stole {round(abs(fuel))} fuel. FeelsGoodMan")
    elif fuel < 0:
        await cmd.reply(f"{cmd.user.display_name} gave {round(abs(fuel))} fuel. Kappa")
    else:
        await cmd.reply(
            f"{cmd.user.display_name} wasted the cooldown, gambling {fuel} fuel for nothing. NotLikeThis"
        )

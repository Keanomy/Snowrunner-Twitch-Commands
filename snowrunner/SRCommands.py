import asyncio
from logging import Logger, getLogger
from random import Random

import keyboard
from twitchAPI.chat import ChatCommand
from twitchAPI.helper import first
from twitchAPI.twitch import TwitchUser

import snowrunner.SRHack as SRHack
from obs import OBS

fuel_stats: dict[str, dict[str, float]] = {}
# fuel_stats: dict[str, dict[str, float]] = {"117914050": {"take": 100.0, "give": 0}, "1049805589": {"take": 0, "give": 26.420806884765625}}

logger: Logger = getLogger("SnowRunner.Commands")


async def winch(cmd: ChatCommand) -> None:
    SRHack.TruckControl.set_control(True)
    keyboard.press_and_release("shift")
    await asyncio.sleep(0.05)
    keyboard.press_and_release("f")
    SRHack.TruckControl.set_control(False)
    print(f"Activated winch.")


async def handbrake(cmd: ChatCommand) -> None:
    SRHack.Handbrake.toggle()
    print(f"Activated handbrake.")


async def lights(cmd: ChatCommand) -> None:
    SRHack.TruckControl.set_control(True)
    await asyncio.sleep(0.05)
    keyboard.press_and_release("shift")
    keyboard.press_and_release("l")
    SRHack.TruckControl.set_control(False)
    print(f"Toggled lights.")


async def horn(cmd: ChatCommand) -> None:
    SRHack.TruckControl.set_control(True)
    keyboard.press_and_release("shift")
    await asyncio.sleep(0.05)
    keyboard.press_and_release("g")
    SRHack.TruckControl.set_control(False)
    print(f"Activated horn.")


async def speed(cmd: ChatCommand, obs: OBS) -> None:
    base_power = SRHack.Power.get_power()
    power_multiplier = 20
    if not base_power:
        logger.debug("Aborted power command, missing base_engine power.")
        return
    if SRHack.TruckControl.is_in_control():
        obs.SetSourceFilterEnabled("Activate Speed", "Screen")
    power = base_power * power_multiplier
    logger.debug(f"Speed command triggered - Base:{base_power} | New:{power} ")
    SRHack.Power.set_power(power)
    await asyncio.sleep(3)
    SRHack.Power.set_power(base_power)
    print("Speed triggered.")


async def fuel_roulette(cmd: ChatCommand, obs: OBS) -> None:
    max_fuel: float = 50
    tank_size: float = SRHack.Fuel.get_tank_size()
    current_fuel: float | None = SRHack.Fuel.get_current_fuel()
    message_parts: list[str] = cmd.text.split()

    if len(message_parts) > 1 and message_parts[1].isnumeric():
        fuel: float = float(message_parts[1])
        fuel = min(abs(fuel), max_fuel)
    else:
        fuel: float = float(Random().randint(25, 50))
    if tank_size < 140 and abs(fuel) > 25:
        fuel /= 2

    fuel *= Random().choice([1, -1])

    if current_fuel == None:
        print("fuck.")
        return

    act_fuel: float = current_fuel + fuel

    print(f"Original fuel: {current_fuel}, New: {act_fuel} added/removed: {fuel}.")
    logger.debug(f"USER: {cmd.user.id} - Original fuel: {current_fuel}, New: {act_fuel} added/removed: {fuel}.")

    if fuel_stats.get(cmd.user.id) is None:
        fuel_stats[cmd.user.id] = {"take": 0, "give": 0}

    if fuel > 0:
        await cmd.reply(f"{cmd.user.display_name} gave {round(abs(fuel))} fuel. Kappa")
        overflow: float = max(0, act_fuel - tank_size)
        fuel_stats[cmd.user.id]["give"] += max(0, fuel - overflow)
        logger.info(f"{cmd.user.id}:{cmd.user.name} gave {round(abs(fuel))} fuel.")
    elif fuel < 0:
        await cmd.reply(f"{cmd.user.display_name} stole {round(abs(fuel))} fuel. FeelsGoodMan")
        overflow: float = max(0, abs(fuel) - max(0, current_fuel))
        fuel_stats[cmd.user.id]["take"] += abs(fuel) - overflow
    else:
        await cmd.reply(f"{cmd.user.display_name} wasted the cooldown, gambling 0 fuel for nothing. NotLikeThis")
        return

    step = 1 if fuel > 0 else -1
    Activate_overlay = SRHack.TruckControl.is_in_control()
    arrow = "Fuel Up" if step == 1 else "Fuel Down"
    if Activate_overlay:
        obs.SetSceneItemEnabled("Game capture", arrow, True)
    for _ in range(abs(int(fuel))):
        current_fuel += step
        SRHack.Fuel.set_current_fuel(current_fuel)
        await asyncio.sleep(0.2)
    if Activate_overlay:
        obs.SetSceneItemEnabled("Game capture", arrow, False)


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
        message = (
            f"Total: {round(abs(give) - abs(take))}L, collectively we lost {round(abs(take))}L and gained {round(abs(give))}L fuel. SPARE ME!! BigSad"
        )
    else:
        message = f"Total: +{round(abs(give) - abs(take))}L, collectively we gained {round(abs(give))}L and lost {round(abs(take))}L fuel. Thank you! TwitchConHYPE"
    await cmd.reply(message)

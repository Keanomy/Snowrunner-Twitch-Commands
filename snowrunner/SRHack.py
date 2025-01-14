from dataclasses import dataclass
from logging import Logger, getLogger
from typing import ClassVar

from pymem import Pymem
from pymem.exception import *

logger: Logger = getLogger("SRHack")


@dataclass
class SRUtility:
    controls_base = 0x29AF898
    truck_base = 0x29AF888
    exe_name: str = "SnowRunner.exe"
    try:
        mem: Pymem | None = Pymem(exe_name)
    except (ProcessNotFound, TypeError):
        logger.debug("Snowrunner not running.")
        mem, truck_base, controls_base = None, None, None

    @classmethod
    def hook_snowrunner(cls) -> bool:
        try:
            logger.debug("Attempting to hook snowrunner...")
            cls.mem: Pymem | None = Pymem(cls.exe_name)
        except ProcessError:
            logger.debug("Snowrunner not running.")
            return False
        return True


def test_pointers() -> tuple[dict[str, bool], dict[str, bool], bool]:
    success, fail = {}, {}
    if SRUtility.hook_snowrunner():
        sr_running = True
        outcome = {
            "Snowrunner": SRUtility.hook_snowrunner(),
            "Control": TruckControl.validate_pointer(),
            "Fuel": Fuel.validate_fuel_pointer(),
            "Fuel Tank": Fuel.validate_tank_pointer(),
            "HandBrake": Handbrake.validate_pointer(),
            "Power": Power.validate_pointer(),
        }

        for mempoint, result in outcome.items():
            if result:
                success.setdefault(mempoint, result)
            else:
                fail.setdefault(mempoint, result)
    else:
        sr_running = False
    return success, fail, sr_running


@dataclass
class TruckControl:
    pointer: int | None = None
    offset: ClassVar[list[int]] = [0x2C]

    @classmethod
    def is_in_control(cls) -> bool:
        if not cls.pointer:
            cls.validate_pointer()
        value: bool = SRUtility.mem.read_bool(cls.pointer)
        logger.debug(f"Truck control value from memory: {value}.")
        return not value

    @classmethod
    def set_control(cls, state: bool) -> None:
        if not cls.pointer:
            cls.validate_pointer()
        logger.debug(f"Setting truck control value to: {state}.")
        SRUtility.mem.write_bool(cls.pointer, state)

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            if not SRUtility.mem:
                SRUtility.hook_snowrunner()
            cls.pointer = SRUtility.mem.resolve_offsets(SRUtility.controls_base, cls.offset)
            SRUtility.mem.read_float(cls.pointer)
            logger.debug(f"Reading Pointer: {cls.pointer} {cls.__name__} successful.")
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError, TypeError):
            logger.debug(f"Validate issue: Unable to access truck control memory address.")
            return False
        except ProcessError:
            logger.debug(f"Snowrunner not running.")
            SRUtility.mem = None
            return False


@dataclass
class Fuel:
    fuel_pointer: float = None
    fuel_offset: ClassVar[list[int]] = [0x20, 0x78, 0x598]

    tank_pointer: float = None
    tank_offset: ClassVar[list[int]] = [0x20, 0x78, 0x5A0]

    ###################### FUEL #########################
    @classmethod
    def get_current_fuel(cls) -> float | None:
        try:
            if not cls.fuel_pointer:
                cls.validate_fuel_pointer()
            fuel = SRUtility.mem.read_float(cls.fuel_pointer)
            logger.debug(f"Fuel amount from memory: {fuel}L.")

            return fuel
        except MemoryReadError:
            logger.debug(f"Unable to read Snowrunner fuel pointer. ")
            return None
        except TypeError:
            logger.debug(f"Fuel pointer is not valid.")
            return None

    @classmethod
    def set_current_fuel(cls, fuel: float) -> bool:
        try:
            if not cls.fuel_pointer:
                cls.validate_fuel_pointer()

            SRUtility.mem.write_float(cls.fuel_pointer, fuel)
            return True

        except MemoryWriteError:
            logger.debug(f'Unable to write: "{fuel}" to fuel pointer. ')
            return False
        except TypeError:
            logger.debug(f'Unable to write: "{fuel}" to fuel pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_fuel_pointer(cls) -> bool:
        try:
            if not SRUtility.mem:
                logger.debug("Missing base address for fuel command.")
                SRUtility.hook_snowrunner()
            cls.fuel_pointer = SRUtility.mem.resolve_offsets(SRUtility.truck_base, cls.fuel_offset)
            SRUtility.mem.read_float(cls.fuel_pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            logger.debug(f"Validate issue: Unable to access fuel memory address.")
            return False

    ###################### FUEL TANK #########################
    @classmethod
    def get_tank_size(cls) -> float:
        try:
            if not cls.tank_pointer:
                cls.validate_tank_pointer()
            tank_size = SRUtility.mem.read_float(cls.tank_pointer)
            logger.debug(f"Fuel tank size from memory {tank_size}L.")
            return tank_size
        except MemoryReadError:
            logger.debug(f"Unable to read Snowrunner fuel tank pointer. ")
            return None
        except TypeError:
            logger.debug(f"Fuel tank pointer is not valid.")
            return None

    @classmethod
    def validate_tank_pointer(cls) -> bool:
        try:
            if not SRUtility.mem:
                SRUtility.hook_snowrunner()
            if not cls.tank_pointer:
                logger.debug(f"Adding memory pointer for {cls.__name__} tank.".title())
            cls.tank_pointer = SRUtility.mem.resolve_offsets(SRUtility.truck_base, cls.tank_offset)
            SRUtility.mem.read_float(cls.tank_pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError, TypeError):
            logger.debug(f"Validate issue: Unable to access fuel tank memory address.")
            return False


# @dataclass
# class LoadCost:
#     pointer: float = None
#     base: int = 0x2A0A980
#     offset: ClassVar[list[int]] = [0xA0, 0x168, 0x60, 0x460]

#     @classmethod
#     def get_current_loadcost(cls) -> int | None:
#         try:
#             cost = SRUtility.mem.read_int(cls.pointer)
#             return cost
#         except MemoryReadError:
#             logger.debug(f"Unable to read Snowrunner loadcost pointer. ")
#             return None
#         except TypeError:
#             logger.debug(f"Loadcost pointer is not valid.")
#             return None

#     @classmethod
#     def set_current_loadcost(cls, cost: int) -> bool:
#         try:
#             SRUtility.mem.write_int(cls.pointer, cost)
#             return True

#         except MemoryWriteError:
#             logger.debug(f'Unable to logger.debug: "{cost}" for loadcost pointer. ')
#             return False
#         except TypeError:
#             logger.debug(f'Unable to logger.debug: "{cost}" for loadcost pointer.\nInvalid Type. ')
#             return False

#     @classmethod
#     def validate_pointer(cls) -> bool:
#         try:
#             if not SRUtility.truck_base or not SRUtility.mem:
#                 SRUtility.hook_snowrunner()
#             if not cls.tank_pointer:
#                 logger.debug(f"Adding memory pointer for {cls.__name__} (Fuel Tank).")
#                 cls.tank_pointer = SRUtility.mem.resolve_offsets(SRUtility.truck_base, cls.offset)
#             SRUtility.mem.read_float(cls.pointer)
#             return True
#         except (MemoryReadError, MemoryWriteError, AttributeError):
#             logger.debug(f"Validate issue: Unable to access loadcost memory address.")
#             return False


@dataclass
class Handbrake:
    pointer: float = None
    offset: ClassVar[list[int]] = [0x20, 0x80, 0x48]

    @classmethod
    def toggle(cls) -> None:
        if cls.is_active():
            cls.set_state(False)
        else:
            cls.set_state(True)

    @classmethod
    def is_active(cls) -> bool | None:
        try:
            if not cls.pointer:
                cls.validate_pointer()
            state = SRUtility.mem.read_bool(cls.pointer)
            return state
        except MemoryReadError:
            logger.debug(f"Unable to read Snowrunner Handbrake pointer. ")
            return None
        except TypeError:
            logger.debug(f"Loadcost pointer is not valid.")
            return None

    @classmethod
    def set_state(cls, state: bool) -> bool:
        try:
            if not cls.pointer:
                cls.validate_pointer()

            SRUtility.mem.write_bool(cls.pointer, state)
            return True

        except MemoryWriteError:
            logger.debug(f'Unable to write: "{state}" to Handbrake pointer. ')
            return False
        except TypeError:
            logger.debug(f'Unable to write: "{state}" to Handbrake pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            if not SRUtility.mem:
                SRUtility.hook_snowrunner()

            cls.pointer = SRUtility.mem.resolve_offsets(SRUtility.truck_base, cls.offset)
            SRUtility.mem.read_bool(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError, TypeError) as E:
            logger.debug(f"Validate issue: Unable to access Handbrake memory address. {E}")
            return False


@dataclass
class Power:
    pointer: int = None
    offset: ClassVar[list[int]] = [0x20, 0x80, 0x50]

    @classmethod
    def get_power(cls) -> float | None:
        try:
            power = SRUtility.mem.read_float(cls.pointer)
            return power
        except MemoryReadError:
            logger.debug(f"Unable to read Snowrunner acceleration pointer. ")
            return None
        except TypeError:
            logger.debug(f"Loadcost pointer is not valid.")
            return None

    @classmethod
    def set_power(cls, power: float) -> bool:
        try:
            SRUtility.mem.write_float(cls.pointer, power)
            return True

        except MemoryWriteError:
            logger.debug(f'Unable to write: "{power}" to acceleration pointer. ')
            return False
        except TypeError:
            logger.debug(f'Unable to write: "{power}" to acceleration pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            if not SRUtility.mem:
                SRUtility.hook_snowrunner()
            cls.pointer = SRUtility.mem.resolve_offsets(SRUtility.truck_base, cls.offset)
            SRUtility.mem.read_float(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError, TypeError) as E:
            logger.debug(f"Validate issue: Unable to access acceleration memory address. {E}")
            return False


if __name__ == "__main__":
    SRUtility.hook_snowrunner()

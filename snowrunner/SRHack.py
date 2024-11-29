from dataclasses import dataclass
from logging import Logger, getLogger
from random import getstate
from typing import ClassVar

from pymem import Pymem
from pymem.exception import *

logger: Logger = getLogger("SR.MemUtility")


@dataclass
class SRUtility:
    mem: Pymem = None
    exe_name: str = "SnowRunner.exe"

    def hook_snowrunner() -> bool:
        try:
            SRUtility.mem = Pymem(SRUtility.exe_name)
            SRUtility.mem.base_address
        except ProcessError:
            return False
        return True

    @staticmethod
    def _GetPtrAddr(base, offset) -> int | None:
        addr = SRUtility.mem.read_longlong(base)
        for i in offset:
            if i != offset[-1]:
                addr = SRUtility.mem.read_longlong(addr + i)
        return addr + offset[-1]

    @classmethod
    def is_in_game(cls) -> bool:
        if not cls.mem:
            cls.hook_snowrunner()
        base_address: int = 0x29AF898
        offset: list[int] = [0x2C]
        pointer: float = cls.mem.resolve_offsets(base_address, offset)
        return not cls.mem.read_bool(pointer)


@dataclass
class Fuel:
    base: int = 0x029AF888

    fuel_pointer: float = None
    fuel_offset: ClassVar[list[int]] = [0x20, 0x78, 0x598]

    tank_pointer: float = None
    tank_offset: ClassVar[list[int]] = [0x20, 0x78, 0x5A0]

    ###################### FUEL #########################
    @classmethod
    def get_current_fuel(cls) -> float | None:
        try:
            fuel = SRUtility.mem.read_float(cls.fuel_pointer)
            return fuel
        except MemoryReadError:
            print(f"Unable to read Snowrunner fuel pointer. ")
            return None
        except TypeError:
            print(f"Fuel pointer is not valid.")
            return None

    @classmethod
    def set_current_fuel(cls, fuel: float) -> bool:
        try:
            SRUtility.mem.write_float(cls.fuel_pointer, fuel)
            return True

        except MemoryWriteError:
            print(f'Unable to print: "{fuel}" for fuel pointer. ')
            return False
        except TypeError:
            print(f'Unable to print: "{fuel}" for fuel pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_fuel_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.fuel_pointer = SRUtility.mem.resolve_offsets(cls.base, cls.fuel_offset)
            SRUtility.mem.read_float(cls.fuel_pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Validate issue: Unable to access fuel memory address.")
            return False

    ###################### FUEL TANK #########################
    @classmethod
    def get_tank_size(cls) -> float:
        try:
            tank_size = SRUtility.mem.read_float(cls.tank_pointer)
            return tank_size
        except MemoryReadError:
            print(f"Unable to read Snowrunner fuel tank pointer. ")
            return None
        except TypeError:
            print(f"Fuel tank pointer is not valid.")
            return None

    @classmethod
    def validate_tank_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.tank_pointer = SRUtility.mem.resolve_offsets(cls.base, cls.tank_offset)
            SRUtility.mem.read_float(cls.tank_pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Validate issue: Unable to access fuel tank memory address.")
            return False


@dataclass
class LoadCost:
    pointer: float = None
    base: int = 0x2A0A980
    offset: ClassVar[list[int]] = [0xA0, 0x168, 0x60, 0x460]

    @classmethod
    def get_current_loadcost(cls) -> int | None:
        try:
            cost = SRUtility.mem.read_int(cls.pointer)
            return cost
        except MemoryReadError:
            print(f"Unable to read Snowrunner loadcost pointer. ")
            return None
        except TypeError:
            print(f"Loadcost pointer is not valid.")
            return None

    @classmethod
    def set_current_loadcost(cls, cost: int) -> bool:
        try:
            SRUtility.mem.write_int(cls.pointer, cost)
            return True

        except MemoryWriteError:
            print(f'Unable to print: "{cost}" for loadcost pointer. ')
            return False
        except TypeError:
            print(f'Unable to print: "{cost}" for loadcost pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.tank_pointer = SRUtility.mem.resolve_offsets(cls.base, cls.offset)
            SRUtility.mem.read_float(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Validate issue: Unable to access loadcost memory address.")
            return False


@dataclass
class Handbrake:
    pointer: float = None
    base: int = 0x029AF888
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
            state = SRUtility.mem.read_bool(cls.pointer)
            return state
        except MemoryReadError:
            print(f"Unable to read Snowrunner Handbrake pointer. ")
            return None
        except TypeError:
            print(f"Loadcost pointer is not valid.")
            return None

    @classmethod
    def set_state(cls, state: bool) -> bool:
        try:
            SRUtility.mem.write_bool(cls.pointer, state)
            return True

        except MemoryWriteError:
            print(f'Unable to print: "{state}" for Handbrake pointer. ')
            return False
        except TypeError:
            print(f'Unable to print: "{state}" for Handbrake pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.pointer = SRUtility.mem.resolve_offsets(cls.base, cls.offset)
            SRUtility.mem.read_bool(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError) as E:
            print(f"Validate issue: Unable to access Handbrake memory address. {E}")
            return False


@dataclass
class Power:
    pointer: int = None
    base: int = 0x029AF888
    offset: ClassVar[list[int]] = [0x20, 0x80, 0x50]

    @classmethod
    def get_power(cls) -> float | None:
        try:
            power = SRUtility.mem.read_float(cls.pointer)
            return power
        except MemoryReadError:
            print(f"Unable to read Snowrunner acceleration pointer. ")
            return None
        except TypeError:
            print(f"Loadcost pointer is not valid.")
            return None

    @classmethod
    def set_power(cls, power: float) -> bool:
        try:
            SRUtility.mem.write_float(cls.pointer, power)
            return True

        except MemoryWriteError:
            print(f'Unable to print: "{power}" for acceleration pointer. ')
            return False
        except TypeError:
            print(f'Unable to print: "{power}" for acceleration pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.pointer = SRUtility.mem.resolve_offsets(cls.base, cls.offset)
            value = SRUtility.mem.read_float(cls.pointer)
            logger.debug(f"Reading Pointer: {cls.pointer} Value: {value} ")
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError) as E:
            logger.debug(f"Validate issue: Unable to access acceleration memory address. {E}")
            return False


class Lights:
    pointer: float = None
    base: int = 0x2A0A980
    offset: ClassVar[list[int]] = [0xA0, 0x168, 0x60, 0x460]

    @classmethod
    def get_state(cls) -> int | None:
        try:
            cost = SRUtility.mem.read_int(cls.pointer)
            return cost
        except MemoryReadError:
            print(f"Unable to read Snowrunner light state pointer. ")
            return None
        except TypeError:
            print(f"Light state pointer is not valid.")
            return None

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.tank_pointer = SRUtility.mem.resolve_offsets(cls.base, cls.offset)
            SRUtility.mem.read_float(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Validate issue: Unable to access light state memory address.")
            return False


if __name__ == "__main__":
    SRUtility.hook_snowrunner()

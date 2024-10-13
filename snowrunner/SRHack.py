from dataclasses import dataclass
from typing import ClassVar

from pymem import Pymem
from pymem.exception import *


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


@dataclass
class Fuel:
    pointer: float = None
    base: int = 0x29AB148
    offset: ClassVar[list[int]] = [0x20, 0x78, 0x598]

    @classmethod
    def get_current_fuel(cls) -> float | None:
        try:
            cls.validate_pointer()
            fuel = SRUtility.mem.read_float(cls.pointer)
            # print(f"Fuel: {fuel}  | Pointer: {cls.pointer}")
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
            cls.validate_pointer()
            SRUtility.mem.write_float(cls.pointer, fuel)
            #    print(f"Fuel: {fuel}  | Pointer: {cls.pointer}")
            return True

        except MemoryWriteError:
            print(f'Unable to print: "{fuel}" for fuel pointer. ')
            return False
        except TypeError:
            print(f'Unable to print: "{fuel}" for fuel pointer.\nInvalid Type. ')
            return False

    @classmethod
    def validate_pointer(cls) -> bool:
        try:
            SRUtility.hook_snowrunner()
            cls.pointer = SRUtility._GetPtrAddr(
                base=SRUtility.mem.base_address + cls.base, offset=cls.offset
            )
            SRUtility.mem.read_float(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Unable to access fuel memory address.")
            return False


@dataclass
class LoadCost:
    pointer: float = None
    base: int = 0x2A0A980
    offset: ClassVar[list[int]] = [0xA0, 0x168, 0x60, 0x460]

    @classmethod
    def get_current_loadcost(cls) -> int | None:
        try:
            cls.validate_pointer()
            cost = SRUtility.mem.read_int(cls.pointer)
            #    print(f"Loadcost: {cost}  | Pointer: {cls.pointer}")
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
            cls.validate_pointer()
            SRUtility.mem.write_int(cls.pointer, cost)
            #     print(f"Loadcost: {cost}  | Pointer: {cls.pointer}")
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
            cls.pointer = SRUtility._GetPtrAddr(
                base=SRUtility.mem.base_address + cls.base, offset=cls.offset
            )
            SRUtility.mem.read_float(cls.pointer)
            return True
        except (MemoryReadError, MemoryWriteError, AttributeError):
            print(f"Unable to access loadcost memory address.")
            return False


if __name__ == "__main__":
    SRUtility.hook_snowrunner()

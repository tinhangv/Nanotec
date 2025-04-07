"""Module defining an interface to a Modbus component.

It is a facade to the pymodbus library. It exposes a simplified Modbus
communication.

Typical usage example:

component = ModbusComponent()
value = component.read_register(address=1234)
"""

import struct

from pymodbus.client import ModbusTcpClient

from alibrary.electronics.ethernet import EthernetComponent
from alibrary.logger import logger


class ModbusError(Exception):
    """Exception raised by the Modbus interface when an error occurs."""


class ModbusComponent(EthernetComponent):
    """An interface to a Modbus component.

    It uses the Facade design pattern to simplify the usage of pymodbus.

    It is generic enough to allow communication to multiple PLC.
    By default, it will create a connection on port 502 with a timeout of 2
    seconds.
    """

    def __init__(self,
                 ip: str,
                 port: int = 502,
                 timeout: int = 2,
                 offline: bool = False) -> None:
        super().__init__(ip, port, timeout, offline)

        if not self.offline:
            self.client = self.__connect()

    def __connect(self) -> ModbusTcpClient:
        """Creates and returns a TCP Modbus client.

        It creates a ModbusTcpClient object and tries to connect to the PLC.
        If it succeeds, it returns the client. Otherwise, it raises an error.

        Returns:
            A ModbusTcpClient object connected to a Modbus component.
            This connection must be closed by the caller.

        Raises:
            ModbusError: The connection to the Modbus component failed.
        """
        client = ModbusTcpClient(host=self.ip,
                                 port=self.port,
                                 timeout=self.timeout)
        if client.connect():
            logger.debug(
                "(Modbus) Connection to the Modbus component "
                "(%s:%d) succeeded.", self.ip, self.port)
            return client
        raise ModbusError("Connection to the Modbus component "
                          f"({self.ip}:{self.port}) failed.")

    def read_coil(self, address: int) -> bool:
        """Reads and returns the value stored inside the coil at the given
        address.

        Args:
            address: The Modbus address of the coil to read

        Returns:
            The boolean value of the coil

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.read_coils(address)
            if response.isError():
                raise ModbusError(
                    f"(Modbus) Error while reading coil at {address}")

            value = response.bits[0]
        else:
            value = False

        logger.debug("(Modbus) Read %s in coil at address %d", value, address)

        return value

    def read_coils(self, address: int) -> list[bool]:
        """Reads and returns the values stored inside the coils at th given
        address.

        Args:
            address: The Modbus address of the coils to read

        Returns:
            The list of boolean values of the coils

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.read_coils(address)
            if response.isError():
                raise ModbusError(
                    f"(Modbus) Error while reading coils at {address}")

            values = response.bits
        else:
            values = []

        logger.debug("(Modbus) Read %s in coils at address %d", values,
                     address)

        return values

    def read_register(self, address: int) -> int:
        """Reads the register at the given address and returns this value.

        Args:
            address: The Modbus address of the register to read

        Returns:
            The value read in the register

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.read_input_registers(address)
            if response.isError():
                raise ModbusError("(Modbus) Error while reading register "
                                  "at {address}: {response}")

            value = response.registers[0]
        else:
            value = 0

        logger.debug("(Modbus) Read %s in register at address %d", value,
                     address)

        return value

    def read_registers(self, address: int) -> int:
        """Reads two consecutive registers and returns the value they represent.

        32 bits numbers are stored inside two consecutive Modbus registers.
        This method allows to retrieved such numbers.

        Args:
            address: the Modbus address of the first register. It will be
            incremented by one for the second.

        Returns:
            The value stored in the two registers

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.read_input_registers(address, count=2)
            if response.isError():
                raise ModbusError("(Modbus) Error while reading registers "
                                  f"at {address}(+1): {response}")

            msb_word = response.registers[0]
            lsb_word = response.registers[1]

            value = struct.unpack(">i", struct.pack(">HH", msb_word,
                                                    lsb_word))[0]
        else:
            value = 0

        logger.debug("(Modbus) Read %s in registers at addresses %d(+1)",
                     value, address)

        return value

    def write_coil(self, address: int, value: bool) -> None:
        """Writes a value inside the coil at the given address.

        Args:
            address: The Modbus address of the coil to write to.
            value: The value to write

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.write_coil(address, value)
            if response.isError():
                raise ModbusError(
                    f"(Modbus) Error while writing coil at {address}")

        logger.debug("(Modbus) Written %s in coil at address %d", value,
                     address)

    def write_coils(self, address: int, values: list[bool]) -> None:
        """Writes values inside the coils at the given address.

        Args:
            address: The Modbus address of the coils to write to.
            values: The list of values to write

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if len(values) > 16:
            raise ModbusError(
                "Cannot write more than 16 coils at the same address")

        if not self.offline:
            response = self.client.write_coils(address, values)
            if response.isError():
                raise ModbusError(
                    f"(Modbus) Error while writing coils at {address}")

        logger.debug("(Modbus) Written %s in coils at address %d", values,
                     address)

    def write_register(self, address: int, value: int) -> None:
        """Writes a value inside the register at the given address.

        Args:
            address: The address of the register to write to
            value: The value to write

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            response = self.client.write_registers(address, value)
            if response.isError():
                raise ModbusError(f"(Modbus) Error while writing register "
                                  f"at {address}: {response}")

        logger.debug("(Modbus) Written %s in register at address %d", value,
                     address)

    def write_registers(self, address: int, value: int) -> None:
        """Writes a value into two consecutive registers.

        32 bits numbers are stored inside two consecutive Modbus registers.
        This method allows to write such numbers.

        Args:
            address: The modbus address of the first register. It will be
            incremented by one for the second.
            value: The value to write

        Raises:
            ModbusError: An error occurs in the Modbus communication
        """
        if not self.offline:
            msb_word, lsb_word = struct.unpack(">HH", struct.pack(">i", value))

            response = self.client.write_registers(address,
                                                   [msb_word, lsb_word])
            if response.isError():
                raise ModbusError(f"(Modbus) Error while writing registers "
                                  f"at {address}(+1)")

        logger.debug("(Modbus) Written %s in registers at address %d(+1)",
                     value, address)

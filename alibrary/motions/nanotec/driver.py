"""Module describing a generic Nanotec motor driver.

This will be specialized to adjust to every kind of motor we use with a Nanotec
driver.
"""
# import struct
import time

from alibrary.electronics.modbus import ModbusComponent, ModbusError
from alibrary.logger import logger
from alibrary.motions.abstract.motor import Motor
from alibrary.motions.nanotec.state import NanotecDriverState
from alibrary.server import InternalServerError


class NanotecDriver(ModbusComponent, Motor):
    """Generic Nanotec driver

    Interface for any Nanotec driver used by Aerosint. It implements both
    ModbusComponent and Motor classes.
    """
    # Statusword of the Nanotec driver (6041)
    STATUS_WORD_ADDRESS = 5000

    # Controlword of the Nanotec driver (6040)
    CONTROL_WORD_ADDRESS = 6000

    # Modes of Operation of the Nanotec driver (6060)
    OPERATION_MODE_READ_ADDRESS = 5001

    # Modes of Operation Display of the Nanotec driver (6061)
    OPERATION_MODE_WRITE_ADDRESS = 6001

    def __init__(self,
                 ip: str,
                 port: int = 502,
                 timeout: int = 2,
                 offline: bool = False) -> None:
        super().__init__(ip, port, timeout, offline)

        try:
            # Initialization sequence of the driver
            if not self.offline:
                if self.__is_fault():
                    self.__reset_fault()

                if self.__set_state_switch_on_disabled():
                    if self.__set_state_ready_to_switch_on():
                        if self.__set_state_switched_on():
                            logger.info(
                                "Nanotec driver (%s:%d) successfully started",
                                self.ip, self.port)
        except InternalServerError as error:
            logger.error("Could not initialize Nanotec driver: %s", error)

    def _get_state(self) -> NanotecDriverState:
        """Retrieves the current state of the Nanotec driver.

        Returns:
            A NanotecDriverState object

        Raises:
            InternalServerError: An error occurs during the reading of the
            status word.
        """
        if self.offline:
            return NanotecDriverState.SWITCHED_ON
        try:
            status_word = self.read_registers(self.STATUS_WORD_ADDRESS)
            state = NanotecDriverState.from_status_word(status_word=status_word)
            logger.debug("(Nanotec driver) Read status %s", state)
            return state
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def __is_fault(self) -> bool:
        """Checks if the driver is in FAULT state.

        Returns:
            A boolean indicating if the driver is in FAULT state or not

        Raises:
            InternalServerError: An error occurs while getting the state.
        """
        return self._get_state() == NanotecDriverState.FAULT

    def _set_control_word(self, value: int):
        """Sets the control word of the Nanotec driver.

        Args:
            value: The value to set as the control word

        Raises:
            InternalServerError: An error occurs during the writing of the
            control word.
        """
        try:
            # value = struct.unpack("<h", struct.pack(">h", value))[0]
            self.write_registers(self.CONTROL_WORD_ADDRESS, value)
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def __reset_fault(self):
        """Resets the FAULT state of the driver

        Raises:
            InternalServerError: An error occurs while resetting fault.
        """
        self._set_control_word(0x80)

        while self._get_state() != NanotecDriverState.SWITCH_ON_DISABLED:
            time.sleep(0.1)

        self._set_control_word(0x0)

    def __wait_for_state(self, state: NanotecDriverState):
        """Waits until the given state is the current state of the driver.

        Args:
            state: The state to wait

        Raises:
            InternalServerError: An error occurs while waiting the state.
        """
        cnt = 0
        while self._get_state() != state:
            cnt += 1

            if cnt > 100:
                logger.error("Timeout waiting state %s", state)
                raise InternalServerError(f"Timeout waiting state {state}")
            time.sleep(0.01)

    def __set_state_switch_on_disabled(self) -> bool:
        """Sets the driver's state to SWITCH ON DISABLED.

        Raises:
            InternalServerError: An error occurs while setting the state.
        """
        current_state = self._get_state()

        if current_state == NanotecDriverState.SWITCH_ON_DISABLED:
            return True

        if current_state == NanotecDriverState.FAULT_REACTION_ACTIVE:
            return False

        if current_state == NanotecDriverState.FAULT:
            self.__reset_fault()
            return True

        self._set_control_word(0x00)

        self.__wait_for_state(NanotecDriverState.SWITCH_ON_DISABLED)
        return True

    def __set_state_ready_to_switch_on(self) -> bool:
        """Sets the driver's state to READY TO SWITCH ON.

        Raises:
            InternalServerError: An error occurs while setting the state.
        """
        current_state = self._get_state()

        if current_state == NanotecDriverState.READY_TO_SWITCH_ON:
            return True

        if current_state in (NanotecDriverState.SWITCH_ON_DISABLED,
                             NanotecDriverState.SWITCHED_ON,
                             NanotecDriverState.OPERATION_ENABLED):
            self._set_control_word(0x06)
            self.__wait_for_state(NanotecDriverState.READY_TO_SWITCH_ON)
            return True

        return False

    def __set_state_switched_on(self) -> bool:
        """Sets the driver's state to SWITCHED ON.

        Raises:
            InternalServerError: An error occurs while setting the state.
        """
        current_state = self._get_state()

        if current_state == NanotecDriverState.SWITCHED_ON:
            return True

        if current_state in (NanotecDriverState.READY_TO_SWITCH_ON,
                             NanotecDriverState.OPERATION_ENABLED):
            self._set_control_word(0x07)
            self.__wait_for_state(NanotecDriverState.SWITCHED_ON)
            return True

        return False

    def __wait_for_operation_mode(self, mode: int):
        """Waits for the operation mode to change to the specified value."""
        cnt = 0
        while self.read_registers(self.OPERATION_MODE_READ_ADDRESS) != mode:
            cnt += 1

            if cnt > 100:
                logger.error("Timeout waiting operation mode %d", mode)
                raise InternalServerError(
                    f"Timeout waiting operation mode {mode}")
            time.sleep(0.01)

    def _set_operation_mode(self, mode: int):
        """Sets the operation mode of the driver.

        Args:
            mode: An integer representing the mode of operation

        Raises:
            InternalServerError: An error occurs while setting the operation
            mode.
        """
        try:
            if not self.offline:
                self.write_registers(self.OPERATION_MODE_WRITE_ADDRESS, mode)
                self.__wait_for_operation_mode(mode)
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def _check_bit_of_status_word(self, bit_index: int) -> bool:
        """Checks one bit of the Nanotec driver status word.

        Args:
            bit_index: The index of the bit to check, starting at zero

        Raises:
            InternalServerError: An error occurs while checking bit of status
            word.
        """
        if self.offline:
            return True

        try:
            status_word = self.read_registers(self.STATUS_WORD_ADDRESS)
            return int(status_word / 2**bit_index) % 2 == 1
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

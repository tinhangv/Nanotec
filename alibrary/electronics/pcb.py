"""Module defining an interface to the pressure sensors and steppers PCB.
"""
import socket
from threading import Lock

from alibrary.electronics.ethernet import EthernetComponent
from alibrary.logger import logger


class PssPCBError(Exception):
    """Exception raised when an error occurs in the communication with the PCB.
    """


class PssPCB(EthernetComponent):
    """An interface to the pressure sensors and steppers PCB.
    """

    def __init__(
        self,
        n_sensors: int,
        ip: str,
        port: int,
        timeout: int = 2,
        offline: bool = False,
    ) -> None:
        super().__init__(ip, port, timeout, offline)

        self.n_sensors = n_sensors
        self.lock = Lock()

        self._cache = [0 for _ in range(self.n_sensors)]
        self._cache_timestamp = 0

        if not self.offline:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            try:
                self.socket.connect((self.ip, self.port))

            except socket.timeout as error:
                logger.error("(PssPCB) Connection timeout while reading (%s)",
                             error)
                raise PssPCBError(str(error)) from error
            except socket.error as error:
                logger.error("(PssPCB) Error while reading (%s)", error)
                raise PssPCBError(str(error)) from error

    def __read(self, n_bytes: int = 1, signed: bool = False) -> int:
        """Reads and returns an integer from the PCB.

        It reads `n_bytes` bytes and then converts them into an integer.

        Args:
            n_bytes: The number of bytes to read
            signed: A flag indicating if the two's complement should be used in
            the conversion
        """
        assert self.offline is False

        data = b""
        for _ in range(n_bytes):
            data += self.socket.recv(1)

        return int.from_bytes(data, byteorder="big", signed=signed)

    def __send(self, value: int, n_bytes: int = 1, signed: bool = False):
        """Sends the given integer to the PCB.

        It converts the given int to bytes using the given number of bytes and
        the signed flag. It then sends all bytes to the PCB through a socket.

        Args:
            value: The integer to send
            n_bytes: The number of bytes the integer should be converted to
            signed: A flag indicating if the two's complement should be used in
            the conversion

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        assert self.offline is False

        data = value.to_bytes(n_bytes, byteorder="big", signed=signed)
        self.socket.sendall(data)

    def get_raw_pressures(self) -> list[int]:
        """Returns all the measured pressures.

        Returns:
            A list of float representing the pressures

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        pressures = [0 for _ in range(self.n_sensors)]

        if not self.offline:
            with self.lock:
                self.__send(1)

                # Reading
                for i in range(self.n_sensors):
                    data = self.__read(2)
                    pressures[i] = data

        logger.debug("(PCB) Reading raw pressures %s", pressures)
        return pressures

    def perform_homing(self, index: int):
        """Performs the homing of the requested component.

        Args:
            index: An index selecting the component on which to perform the
            homing

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Performing homing of %s", bin(index))
        if not self.offline:
            with self.lock:
                self.__send(2)
                self.__send(index)

    def check_homing_done(self) -> int:
        """Checks on all component if the homing has been performed.

        It returns a binary number where a 1 at a given position means that
        the corresponding component has been homed.

        Example:
            0000 1001: The first and fourth components have been homed,
            the others not

        Returns:
            A binary number

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Checking homing")
        if not self.offline:
            with self.lock:
                self.__send(3)
                return self.__read(2)
        return 65535

    def perform_distance_motion(self, stepper_index: int, target: int):
        """Start an absolute distance motion on the specified stepper.

        Args:
            stepper_index: The index of the stepper to control
            target: The absolute target distance to reach

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Performing distance motion to %s on %s", target,
                     stepper_index)
        if not self.offline:
            with self.lock:
                self.__send(4)
                self.__send(1)
                self.__send(stepper_index)
                self.__send(target, n_bytes=4, signed=True)

    def set_actual_position(self, stepper_index: int, position: int):
        """Sets the actual position of the specified stepper.

        To avoid too many homing on the scraping blades steppers, their current
        position is saved to a file and then restored at each startup. This
        methods allows to signified to a given stepper its actual position.

        Args:
            stepper_index: The index of the stepper to calibrate
            position: The position to set in the stepper

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Setting actual position to %s on stepper %s",
                     position, stepper_index)
        if not self.offline:
            with self.lock:
                self.__send(5)
                self.__send(stepper_index)
                self.__send(position, n_bytes=4, signed=True)

    def start_pressure_control(self, control_index: int, data: int):
        """Starts the pressure control to maintain the requested pressure in
        the given component.

        The index allows to choose the destination of this command.

        Args:
            control_index: The destination of this command
            data: The raw pressure to set

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Starting pressure control of %s for %s", data,
                     control_index)
        if not self.offline:
            with self.lock:
                self.__send(6)
                self.__send(control_index)
                self.__send(data, n_bytes=2)

    def stop_pressure_control(self, control_index: int):
        """Stops the pressure control of the given component

        Args:
            control_index: The destination of this command

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Stopping pressure control for %s", control_index)
        if not self.offline:
            with self.lock:
                self.__send(7)
                self.__send(control_index)

    # def check_driver_communication(self):
    #     self.__send(8)
    #     communication_429 = self.__read()
    #     communication_2130 = self.__read(2)
    #     logger.warning(communication_429)
    #     logger.warning(communication_2130)

    def get_actual_position(self, stepper_index: int) -> int:
        """Returns the actual position of the specified stepper.

        Args:

        Returns:
        """
        if not self.offline:
            self.__send(9)
            self.__send(stepper_index)
            return self.__read(4, signed=True)
        return 0

    def check_busy(self) -> int:
        """Checks on all steppers if they are running or not.

        It returns a binary number where a 1 at a given position means that
        the corresponding stepper is busy.

        Example:
            0000 1001: The first and fourth steppers are busy, the others not

        Returns:
            A binary number

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        logger.debug("(PCB) Checking busy")
        if not self.offline:
            with self.lock:
                self.__send(10)
                return self.__read(2)
        return 65535

    def set_integral_gain(self, control_index, gain):
        """Sets the integral gain of the given controlled valve.

        Args:
        """
        if not self.offline:
            with self.lock:
                self.__send(11)
                self.__send(control_index)
                self.__send(gain, n_bytes=4, signed=True)

    def set_proportional_gain(self, control_index, gain):
        """Sets the proportional gain of the given controlled valve.

        Args:
        """
        if not self.offline:
            with self.lock:
                self.__send(12)
                self.__send(control_index)
                self.__send(gain, n_bytes=4, signed=True)

    # 250
    def set_rms_position(self, current):
        """Sets the RMS current when the valve makes a position motion.

        Args:

        """
        if not self.offline:
            with self.lock:
                self.__send(14)
                self.__send(current, n_bytes=2)

    # 200
    def set_rms_control(self, control_index, current):
        """Sets the RMS current when the given valve is regulating.

        Args:

        """
        if not self.offline:
            with self.lock:
                self.__send(15)
                self.__send(control_index)
                self.__send(current, n_bytes=2)

    def set_regulating_valve(self, index):
        """Sets if the leveler pressure is regulated using the leveler valve or
        the hood valve.

        Args:

        """
        if not self.offline:
            with self.lock:
                self.__send(16)
                self.__send(index)

    def perform_distance_motion_new(self, stepper_index, position):
        """Send values and then check if the ones read are the same."""
        logger.warning(self.check_actual_position(stepper_index))
        if not self.offline:
            with self.lock:
                self.__send(19)
                self.__send(stepper_index)
                self.__send(position, n_bytes=4, signed=True)

                pcb_stepper_index = self.__read()
                pcb_position = self.__read(n_bytes=4, signed=True)

                if (pcb_stepper_index != stepper_index or
                        pcb_position != position):
                    logger.warning(
                        "(PCB) Error in communication. Send '%s' and '%s' but\
                            received '%s' and '%s'", stepper_index, position,
                        pcb_stepper_index, pcb_position)
                else:
                    logger.debug("Communication checked")
        logger.warning(self.check_actual_position(stepper_index))

    def check_actual_position(self, stepper_index):
        if not self.offline:
            with self.lock:
                self.__send(20)
                self.__send(stepper_index)
                position = self.__read(n_bytes=4, signed=True)
                return position
        return 0.0

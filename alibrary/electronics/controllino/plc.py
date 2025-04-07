"""Module defining an interface to a physical Controllino PLC."""
import socket

from alibrary.electronics.controllino.packet import ControllinoPacket
from alibrary.electronics.controllino.register import ControllinoRegister
from alibrary.electronics.ethernet import EthernetComponent
from alibrary.logger import logger


class ControllinoError(Exception):
    """Exception raised when an error occurs in the communication with the
    Controllino.
    """


class ControllinoPLC(EthernetComponent):
    """Interface to a physical Controllino PLC."""

    def __init__(
        self,
        ip: str,
        port: int,
        timeout: int = 2,
        offline: bool = False,
    ) -> None:
        super().__init__(ip, port, timeout, offline)

        self.__packet_socket: socket.socket = None
        self.__test_socket: socket.socket = None

    def send_parameter(self, register: ControllinoRegister, value: int):
        """Sends `value` to the `register`.

        Args:
            register:
            value:
        """
        error_cnt = 0
        status = 5
        if not self.offline:
            while error_cnt < 5 and status != 0:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                    try:
                        soc.connect((self.ip, self.port))

                        soc.sendall(self.__to_bytes(0x01))
                        soc.sendall(self.__to_bytes(register.register_id))
                        soc.sendall(
                            self.__to_bytes(value, n_bytes=register.n_bytes))

                        if register.ack:
                            status = int.from_bytes(soc.recv(1),
                                                    byteorder="big")
                        else:
                            status = 0

                        if register.ack:
                            self.__check_ack(status)

                    except socket.timeout as error:
                        logger.error(
                            "(Controllino) Timeout while sending a parameter")
                        raise ControllinoError(str(error)) from error
                    except socket.error as error:
                        logger.error(
                            "(Controllino) Error while sending a parameter")
                        raise ControllinoError(str(error)) from error

                error_cnt += 1

            if status != 0:
                raise ControllinoError(
                    "Error while setting Controllino parameter")

        logger.debug("(Controllino) Value %d send to register %s", value,
                     register)

    def send_packet(self, packet: ControllinoPacket):
        """Sends a custom packet to the Controllino.

        Args:
            packet: A ControllinoPacket object
        """
        if not self.offline:
            self.__packet_socket = socket.socket(socket.AF_INET,
                                                 socket.SOCK_STREAM)

            try:
                self.__packet_socket.connect((self.ip, self.port))

                # Control byte
                self.__packet_socket.sendall(self.__to_bytes(0x00))

                # Header
                self.__packet_socket.sendall(
                    self.__to_bytes(packet.n_bytes, n_bytes=4))
                self.__packet_socket.sendall(
                    self.__to_bytes(packet.line_duration, n_bytes=4))
                self.__packet_socket.sendall(
                    self.__to_bytes(packet.n_blank_lines, n_bytes=4))

                # Body
                self.__packet_socket.sendall(packet.data)

                # data = self.__packet_socket.recv(4096)
                # value = data.decode("utf-8")

                # print("Data:", data, "Value:", value)
            except socket.timeout as error:
                logger.error(
                    "(Controllino) Connection timeout while sending a matrix")
                raise ControllinoError(str(error)) from error
            except socket.error as error:
                logger.error("(Controllino) Error while sending a matrix")
                raise ControllinoError(str(error)) from error

        logger.debug("(Controllino) Matrix sent to %s", self.ip)

    def set_test_mode(self, test_index: int):
        """Set a test mode in the Controllino"""
        if not self.offline:
            self.__test_socket = socket.socket(socket.AF_INET,
                                                 socket.SOCK_STREAM)

            try:
                self.__test_socket.connect((self.ip, self.port))

                self.__test_socket.sendall(self.__to_bytes(0x04))
                self.__test_socket.sendall(self.__to_bytes(test_index))
            except socket.timeout as error:
                logger.error(
                    "(Controllino) Timeout while sending a parameter")
                raise ControllinoError(str(error)) from error
            except socket.error as error:
                logger.error(
                    "(Controllino) Error while sending a parameter")
                raise ControllinoError(str(error)) from error

    def close_test_socket(self):
        if self.__test_socket is not None:
            self.__test_socket.close()
        self.__test_socket = None

    def wait_end_of_print(self):
        """Waits for the Controllino to signal the end of the pattern."""
        if not self.offline and self.__packet_socket is not None:
            print("Waiting data...")
            self.__packet_socket.recv(32)
            self.__packet_socket = None

    def read_register(self, register: ControllinoRegister) -> bytes:
        """Reads the specified register"""
        if not self.offline:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                try:
                    soc.connect((self.ip, self.port))
                    soc.sendall(self.__to_bytes(0x01))
                    soc.sendall(self.__to_bytes(register.register_id))
                    return soc.recv(register.n_bytes)

                except socket.timeout as error:
                    logger.error("(Controllino) Timeout while reading a register")
                    raise ControllinoError(str(error)) from error
                except socket.error as error:
                    logger.error("(Controllino) Error while reading a register")
                    raise ControllinoError(str(error)) from error
        else:
            return b"\x01"

    def cancel_print(self):
        """Cancels the current print job"""
        if not self.offline and self.__packet_socket is not None:
            logger.debug("Closing connection to the COntrollino")
            self.__packet_socket.shutdown(socket.SHUT_RDWR)
            self.__packet_socket = None

    @staticmethod
    def __to_bytes(value: int | bool, n_bytes: int = 1) -> bytes:
        """Converts the given value into its bytes representation.

        It will return n bytes in big endian order that represent the give
        integer.

        Args:
            value: The integer to convert
            n_bytes: The number of bytes in the result

        Returns:
            A bytes object representing the value
        """
        return value.to_bytes(n_bytes, byteorder="big")

    @staticmethod
    def __check_ack(status: int):
        """Logs the state of the communication with the Controllino depending
        on the given status code.
        """
        if status == 0:
            logger.debug("(Controllino) Set parameters: Success")
        elif status == 1:
            logger.error(
                "(Controllino) Set parameters: Length to long for buffer")
        elif status == 2:
            logger.error(
                "(Controllino) Set parameters: Address send, NACK received")
        elif status == 3:
            logger.error(
                "(Controllino) Set parameters: Receive NACK on transmit of data"
            )
        elif status == 4:
            logger.error("(Controllino) Set parameters: Other error")
        elif status == 5:
            logger.error("(Controllino) Set parameters: Timeout")

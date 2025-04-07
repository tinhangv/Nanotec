"""Module defining an interface to a Controllino PLC.

It allows to send the powder deposition matrices to the PLC into a custom
format.
"""
from alibrary.electronics.controllino.packet import ControllinoPacket
from alibrary.electronics.controllino.parameters import ControllinoParameters
from alibrary.electronics.controllino.plc import ControllinoPLC
from alibrary.electronics.controllino.register import (
    EJECTION_REGISTERS,
    ELECTRICAL_BRIDGE_BREAKERS,
    POWDER_COLLECTORS_REGISTERS,
    ControllinoRegisters,
)

CtrlnParams = ControllinoParameters


class Controllino:
    """An interface above a set of Controllino to abstract their numbers.
    """

    # Safety status byte
    SAFETY_STATUS_READ_REGISTER = 0

    def __init__(self,
                 n_drums: int,
                 plcs: list[ControllinoPLC],
                 cyclone_level: int = 50,
                 pneumatic_bridge_breakers: bool = False) -> None:
        self.__n_drums = n_drums
        self.__plcs = plcs
        self.pneumatic_bridge_breakers = pneumatic_bridge_breakers
        self.__cyclone_level = cyclone_level

        self.__parameters: CtrlnParams = CtrlnParams.from_n_drums(n_drums)

        self.__cyclone_activation = 0

    @property
    def plcs(self):
        return self.__plcs

    def get_cyclone_level(self) -> int:
        return self.__cyclone_level

    def set_cyclone_level(self, level: int):
        self.set_vfd(level)
        self.__cyclone_level = level

    def get_ejection(self, drum_id: int) -> float:
        """Returns the stored ejection pressure of the given drum.

        Args:
            drum_id: The index of the drum from which to return the ejection

        Returns:
            A float representing the ejection pressure
        """
        return self.__parameters.ejection_pressures[drum_id]

    def set_ejection(self, drum_id: int, pressure: float):
        """Sets the ejection pressure of a given drum.

        It will store the value internally and then send every parameters to
        the Controllino.

        Args:
            drum_id: The index of the drum whose ejection need to be set
            pressure: The ejection pressure to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.ejection_pressures[drum_id] = pressure
        register = EJECTION_REGISTERS[drum_id]

        self.__plcs[register.controllino_id].send_parameter(register=register,
                                                            value=int(pressure))

    def activate_cyclone(self, index: int):
        """Activates the cyclone at 50% of its full capacity.

        It also registers who triggers the activation to allow to properly
        deactivate the cyclone.

        Args:
            index: An index identifying the element requesting the activation

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        if self.__cyclone_activation == 0:
            self.set_vfd(int(self.__cyclone_level / 100 * 4095))

        self.__cyclone_activation |= 2**index

    def deactivate_cyclone(self, index: int):
        """Deactivates the cyclone if all registered components have deactivate
        it.

        Args:
            index: An index identifying the element requesting the deactivation

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__cyclone_activation &= ~2**index

        if self.__cyclone_activation == 0:
            self.set_vfd(0)

    def set_vfd(self, value: int):
        """Sets the value of the variable frequency drive.

        It will store the value internally and then send every parameters to
        the Controllino.

        Args:
            value: The vfd value to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.variable_frequency_drive = value
        register = ControllinoRegisters.FREQUENCY_VARIATOR

        self.__plcs[register.controllino_id].send_parameter(register=register,
                                                            value=value)

    def get_bridge_breakers_state(self) -> bool:
        """Returns the stored state of the bridge breakers.

        Returns:
            A bool representing the state of the bridge breakers
        """
        return self.__parameters.bridge_breakers_state

    def set_bridge_breakers_state(self, state: bool):
        """Sets the state of the bridge breakers.

        It will store the state internally and then send every parameters to
        the Controllino.

        Args:
            state: The bridge breakers state to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.bridge_breakers_state = state

        if self.pneumatic_bridge_breakers:
            register = ControllinoRegisters.PNEUMATIC_BRIDGE_BREAKER
            self.__plcs[register.controllino_id].send_parameter(
                register=register, value=state)
        else:
            value = 1843 if state else 0
            for drum_id in range(self.__n_drums):
                register = ELECTRICAL_BRIDGE_BREAKERS[drum_id]
                self.__plcs[register.controllino_id].send_parameter(
                    register=register, value=value)

    def get_shovels_state(self) -> int:
        """Returns the stored state of the shovels.

        Returns:
            A bool representing the state of the shovels
        """
        return self.__parameters.shovels_state

    def set_shovels_state(self, state: int):
        """Sets the state of the shovels.

        It will store the state internally and then send every parameters to
        the Controllino.

        Args:
            state: The shovels state to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.shovels_state = state
        register = ControllinoRegisters.SHOVELS

        self.__plcs[register.controllino_id].send_parameter(register=register,
                                                            value=state)

    def get_collectors(self, drum_id: int) -> bool:
        """Returns the state of the powder collector of the given drum.

        Args:
            drum_id: The index of the drum from which to return the state

        Returns:
            A bool representing the state of the powder collector
        """
        return self.__parameters.powder_collectors_state[drum_id]

    def set_collectors(self, drum_id: int, state: bool):
        """Sets the state of the powder collector of a given drum.

        It will store the value internally and then send every parameters to
        the Controllino.

        Args:
            drum_id: The index of the drum whose powder collector need to be set
            state: The state of the powder collector to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.powder_collectors_state[drum_id] = state
        register = POWDER_COLLECTORS_REGISTERS[drum_id]

        self.__plcs[register.controllino_id].send_parameter(register=register,
                                                            value=state)

    def get_gripper_state(self) -> bool:
        """Returns the Z gripper state.

        Returns:
            A bool representing the state
        """
        return self.__parameters.gripper_state

    def set_gripper_state(self, state: bool):
        """Sets the state of the Z gripper.

        It will store the state internally and then send the parameter to
        the Controllino.

        Args:
            state: The gripper state to set

        Raises:
            ControllinoError: An error occurs in th communication with the
            Controllino.
        """
        self.__parameters.gripper_state = state
        register = ControllinoRegisters.GRIPPER_Z

        self.__plcs[register.controllino_id].send_parameter(register=register,
                                                            value=state)

    def send_packet(self, index: int, packet: ControllinoPacket):
        """Sends a custom packet to the Controllino.

        Args:
            packet: A ControllinoPacket object
        """
        self.__plcs[index].send_packet(packet)

    def wait_end_of_print(self):
        """Waits for the Controllino to signal the end of the pattern."""
        for plc in self.__plcs:
            plc.wait_end_of_print()

    def cancel_print(self):
        """Cancels the current print job"""
        for plc in self.__plcs:
            plc.cancel_print()

    def is_reset_activated(self) -> bool:
        register = ControllinoRegisters.SAFETY_STATUS
        value = self.__plcs[register.controllino_id].read_register(register)
        return bool(value[0] & 1)

    # TODO: Revamp those
    # def test_one_valve(self, number_valve: int):
    #     soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     soc.connect((self.ip, self.port))
    #     soc.sendall(0x04.to_bytes(1, byteorder="big"))
    #     soc.sendall(0x00.to_bytes(1, byteorder="big"))
    #     soc.sendall(number_valve.to_bytes(2, byteorder="big"))
    #     soc.shutdown(socket.SHUT_RDWR)

    # def test_valves(self, min_nb_valve: int, max_nb_valve: int):
    #     soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     soc.connect((self.ip, self.port))
    #     soc.sendall(0x04.to_bytes(1, byteorder="big"))
    #     soc.sendall(0x04.to_bytes(1, byteorder="big"))
    #     soc.sendall(min_nb_valve.to_bytes(2, byteorder="big"))
    #     soc.sendall(max_nb_valve.to_bytes(2, byteorder="big"))
    #     soc.shutdown(socket.SHUT_RDWR)

    # def set_mode(self, number_test: int):
    #     if not number_test in (1, 2, 3):
    #         logger.error("Wrong debug mode number")
    #         return
    #     soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     soc.connect((self.ip, self.port))
    #     soc.sendall(0x04.to_bytes(1, byteorder="big"))
    #     soc.sendall(number_test.to_bytes(1, byteorder="big"))
    #     soc.shutdown(socket.SHUT_RDWR)

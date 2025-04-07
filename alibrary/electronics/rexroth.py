"""Module defining a Rexroth driver class using the DLL and .NET framework."""
from alibrary.electronics.ethernet import EthernetComponent
from alibrary.logger import logger


class RexrothError(Exception):
    """Exception raised when an error occurs with the Rexroth driver.
    """


class RexrothDotNetDriver(EthernetComponent):
    """Interface to a Rexroth driver."""

    ACCELERATION = 50
    JERK = 0

    def __init__(
        self,
        ip: str,
        port: int,
        timeout: int = 2,
        offline: bool = False,
    ) -> None:
        super().__init__(ip, port, timeout, offline)
        self.connection = None

    def connect(self):
        """Connects to the Rexroth driver"""
        # pylint: disable=C0415
        import clr

        # pylint: disable=E1101
        clr.AddReference("../lib/EAL")
        # pylint: disable=E0401, C0413
        import EAL  # type: ignore

        if not self.offline:
            self.connection = EAL.EALConnection.EALConnection()
            self.connection.Connect(self.ip)
            axis = self.connection.Motion.Axes[0]
            axis.SetCondition(EAL.Enums.AxisCondition.AXIS_CONDITION_ACTIVE)
            axis.Movement.Power(True)

    def get_position(self) -> float:
        """Returns the current position registered inside the Rexroth driver."""
        # pylint: disable=E0602
        if not self.offline:
            self.connect()
            try:
                position = self.connection.Parameter.ReadData("S-0-0051.0.0")
            except EAL.Exceptions.EALException as error:  # type: ignore
                raise RexrothError(str(error)) from error
            self.close()
        else:
            position = 0

        logger.debug("(Rexroth) Current position retrieved, position = %s",
                     position)

        return position

    def perform_relative_motion(self, distance: float, speed: float):
        """Performs a relative motion"""
        # pylint: disable=E0602
        if not self.offline:
            self.connect()
            try:
                axis = self.connection.Motion.Axes[0]
                axis.Movement.MoveAdditive(distance, speed * 60,
                                           self.ACCELERATION, self.ACCELERATION,
                                           self.JERK)
                axis.Movement.Wait(100000)
            except EAL.Exceptions.EALException as error:  # type: ignore
                raise RexrothError(str(error)) from error
            self.close()

        logger.debug("(Rexroth) Perform relative motion to %s at %s mm/s",
                     distance, speed)

    def perform_absolute_motion(self, distance: float, speed: float):
        """Performs a absolute motion"""
        # pylint: disable=E0602
        if not self.offline:
            self.connect()
            try:
                axis = self.connection.Motion.Axes[0]
                axis.Movement.MoveAbsolute(distance, speed * 60,
                                           self.ACCELERATION, self.ACCELERATION,
                                           self.JERK)
                axis.Movement.Wait(100000)
            except EAL.Exceptions.EALException as error:  # type: ignore
                raise RexrothError(str(error)) from error
            self.close()

        logger.debug("(Rexroth) Perform relative motion to %s at %s mm/s",
                     distance, speed)

    def check_busy(self) -> bool:
        """Checks if the axis is busy or not."""
        # pylint: disable=E0602
        if not self.offline:
            self.connect()
            try:
                state = self.connection.Parameter.ReadData("S-0-0331.0.0")
                state = not bool(state)
            except EAL.Exceptions.EALException as error:  # type: ignore
                raise RexrothError(str(error)) from error
            self.close()
        else:
            state = False

        logger.debug("(Rexroth) Busy state retrieved, state = %s", state)

        return state

    def close(self):
        """Closes the connection with the Rexroth driver."""
        axis = self.connection.Motion.Axes[0]
        axis.Movement.Power(False)
        self.connection.Disconnect()

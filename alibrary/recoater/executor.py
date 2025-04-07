"""Module defining an executor class that can start and stop a procedure.

This is used for the deposition procedure and the printing procedure.

It uses the multiprocessing package to start a subprocess with the procedure.
"""
from multiprocessing import Process, Queue
from collections.abc import Callable

from alibrary.logger import logger


class ProcedureExecutor:
    """Class that can execute and cancel its given procedure.

    Attributes:
        procedure: The procedure to run in a subprocess
        cancel_procedure: The procedure to run when cancelling
    """

    def __init__(
        self,
        name: str,
        procedure: Callable[[Queue], None],
        cancel_procedure: Callable[[], None],
    ) -> None:
        self.name = name
        self.process: Process = None
        self.exception_queue = Queue()

        self.procedure = procedure
        self.cancel_procedure = cancel_procedure

    def start(self):
        """Starts the procedure in a subprocess."""
        logger.info("%s procedure started", self.name)

        self.process = Process(target=self.procedure,
                               args=(self.exception_queue,))
        self.process.start()

    def stop(self):
        """Stops the procedure."""
        if self.process is not None and self.process.is_alive():
            self.process.kill()
            self.process = None

        self.cancel_procedure()

        logger.info("%s procedure cancelled", self.name)

    def is_running(self) -> bool:
        """Checks if the procedure is running.

        Returns:
            A boolean flag indicating if the procedure is running or not
        """
        if self.process is None:
            return False

        return self.process.is_alive()

    def has_errors(self) -> bool:
        """Checks if the subprocess has encountered errors.

        Returns:
            A boolean flag indicating if the subprocess had errors
        """
        return not self.exception_queue.empty()

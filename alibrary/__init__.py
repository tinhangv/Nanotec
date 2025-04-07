"""Modules defining the business logic classes used in the Aerosint backends.
"""
from importlib.metadata import version

from alibrary.logger import init_logger, logger

#__version__ = version("alibrary")

__all__ = ["init_logger", "logger"]

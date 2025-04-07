"""Module defining a class for the electronics components that are reach via
Ethernet.

This allows to isolate Ethernet specific properties.
"""
from abc import ABC
from dataclasses import dataclass


@dataclass
class EthernetComponent(ABC):
    """Electronics component accessed by the server via Ethernet."""
    ip: str
    port: int
    timeout: int = 2
    offline: bool = False

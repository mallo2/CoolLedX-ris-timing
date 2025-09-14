"""Handle messages returned from the device."""

from __future__ import annotations

import abc


class MessageHandler(abc.ABC):
    """Abstract class for message handler."""

    @abc.abstractmethod
    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""


class CoolLEDXMessageHandler(MessageHandler):
    """Message handler for CoolLEDX devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")

"""Unit tests for quiz-admin message receiving."""

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pytest

from quiz_admin.__main__ import receive_messages

if TYPE_CHECKING:
    from websockets.asyncio.client import ClientConnection


class StopReceivingError(Exception):
    """Stop the infinite receiving loop after the prepared message."""


@dataclass
class FakeWebSocket:
    """Return one server message and then stop the receiving loop."""

    response: str
    received: bool = False

    async def recv(self) -> str:
        """Return the prepared response once."""
        if not self.received:
            self.received = True
            return self.response
        raise StopReceivingError


def test_receive_messages_prints_correct_answer(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print the correct answer from a question result message."""
    websocket = FakeWebSocket(
        '{"type": "question_result", "correct_answer": "a"}',
    )

    with pytest.raises(StopReceivingError):
        asyncio.run(receive_messages(cast("ClientConnection", websocket)))

    assert capsys.readouterr().out == "Correct answer: a\n"

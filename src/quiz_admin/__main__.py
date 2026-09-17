"""
Main entry point for the quiz admin client.

This module allows an admin to send a quiz to the server and interactively
control the quiz session via a websocket connection.
"""

import asyncio
import json
import string
import sys
from pathlib import Path
from typing import Any

import aioconsole
from quiz_common.models import Question, Quiz
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


async def send_receive_messages(uri: str, quiz_data: dict[str, Any]) -> None:
    """
    Establish a websocket connection to the server.

    Send the quiz data and concurrently handle sending and receiving messages.
    """
    async with connect(uri) as ws:
        # Initial sending the whole quiz data to the server
        await ws.send(json.dumps(quiz_data))
        quiz = Quiz(**quiz_data)
        await asyncio.gather(send_messages(ws), receive_messages(ws, quiz))


async def send_messages(ws: ClientConnection) -> None:
    """Prompt the user for input and send messages to the server over the websocket."""
    while True:
        user_input = await aioconsole.ainput("Send 'y' for the next question\n")
        if user_input:
            await ws.send(user_input)


async def receive_messages(ws: ClientConnection, quiz: Quiz) -> None:
    """Receive messages from the server and print them to the console."""
    game_log = GameLog(quiz)
    while True:
        response = await ws.recv()
        try:
            message = json.loads(response)
            match message.get("type"):
                case "answer":
                    game_log.record_answer(message)
                case "quiz_finished":
                    final_results = game_log.final_results(message.get("players", []))
                    print_final_scores(final_results["scores"])
                    await ws.send(
                        json.dumps(
                            {
                                "type": "final_results",
                                **final_results,
                            }
                        )
                    )
                case "final_scores":
                    print_final_scores(message["scores"])
                case _:
                    print_question(message)
        except (TypeError, json.JSONDecodeError):
            print(response)


def print_final_scores(scores: list[dict]) -> None:
    """Print final player scores ordered from highest to lowest."""
    print("Let's check the final scores!")
    for score in scores:
        print(f"{score['player']}: {score['correct_count']}")


def correct_answer(question: Question) -> str:
    """Extract the correct answer letters from a question."""
    correct_answer_string = ""
    for letter, opt in zip(string.ascii_letters, question.options, strict=False):
        if opt.correct:
            correct_answer_string += letter
    return correct_answer_string


class GameLog:
    """Keep accepted answers and scores for one quiz run."""

    def __init__(self, quiz: Quiz) -> None:
        """Initialize an empty log for the given quiz."""
        self.quiz = quiz
        self._results: dict[tuple[str, int], dict] = {}

    def record_answer(self, event: dict) -> None:
        """Evaluate and store an accepted answer event from the server."""
        question_number = event["question_number"]
        correct = set(event["answer"].lower().strip()) == set(
            correct_answer(self.quiz.questions[question_number])
        )
        self._results[(event["player"], question_number)] = {
            "answer": event["answer"],
            "correct": correct,
            "points": int(correct),
        }

    def final_results(self, player_names: list[str]) -> dict:
        """Return final scores and per-player results."""
        results_by_player = {
            player_name: self.for_player(player_name) for player_name in player_names
        }
        scores = [
            {
                "player": player_name,
                "correct_count": sum(
                    result["points"] for result in results_by_player[player_name]
                ),
            }
            for player_name in player_names
        ]

        return {
            "scores": sorted(
                scores,
                key=lambda score: (-score["correct_count"], score["player"]),
            ),
            "results": results_by_player,
        }

    def for_player(self, player_name: str) -> list[dict]:
        """Return all recorded results for one player."""
        return [
            {
                "question_number": number,
                **result,
            }
            for (player, number), result in self._results.items()
            if player == player_name
        ]


def print_question(question: dict[str, list | str]) -> None:
    """Nicely print text of the question with possible answers."""
    print(f"Question: {question['text']}")
    for letter, opt in zip(string.ascii_letters, question["options"], strict=False):
        print(f"\t{letter}) {opt}")


def main() -> None:
    """
    Script entry point.

    Parse arguments, load the quiz YAML file, validate it, and start the websocket
    communication with the server.
    """
    if len(sys.argv) != 3:  # noqa: PLR2004
        sys.exit(f"Usage: {sys.argv[0]} <url> <quiz file>")

    server_url = f"ws://{sys.argv[1]}/admin"

    try:
        quiz_file = sys.argv[2]

        with Path(quiz_file).open(encoding="utf-8") as file:
            quiz_data = YAML(typ="safe").load(file)

        validated_quiz = Quiz(**quiz_data)

    except (OSError, YAMLError) as e:
        sys.exit(str(e))
    except TypeError as e:
        sys.exit(f"TODO: better error handling\n{e}")

    try:
        asyncio.run(send_receive_messages(server_url, validated_quiz.model_dump()))
    except OSError as e:
        sys.exit(f"Admin: cannot reach server\n{e}")
    except ConnectionClosedOK as e:
        print(e.reason)
    except ConnectionClosedError as e:
        sys.exit(f"Admin: server disconected\n{e}")
    except KeyboardInterrupt:
        sys.exit("\nAdmin: exit")

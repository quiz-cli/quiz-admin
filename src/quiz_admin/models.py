"""Domain model for tracking quiz answers and scores used by the admin client."""

import string

from quiz_common.models import Question, Quiz


class GameLog:
    """Keep accepted answers and scores for one quiz run."""

    def __init__(self, quiz: Quiz) -> None:
        """Initialize an empty log for the given quiz."""
        self.quiz = quiz
        self._results: list[dict] = []

    def record_answer(self, event: dict) -> None:
        """Evaluate and store an accepted answer event from the server."""
        question_number = event["question_number"]
        correct = set(event["answer"].lower().strip()) == set(
            correct_answer(self.quiz.questions[question_number])
        )
        self._results.append(
            {
                "player": event["player"],
                "question_number": event["question_number"],
                "answer": event["answer"],
                "correct": correct,
                "points": int(correct),
            }
        )

    def final_results(self, player_names: list[str]) -> dict:
        """Return final scores and per-player results."""
        results_by_player = {
            player_name: self.results_for_player(player_name)
            for player_name in player_names
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

    def results_for_player(self, player_name: str) -> list[dict]:
        """Return all recorded results for one player."""
        return [result for result in self._results if result["player"] == player_name]


def correct_answer(question: Question) -> str:
    """Extract the correct answer letters from a question."""
    correct_answer_string = ""
    for letter, opt in zip(string.ascii_letters, question.options, strict=False):
        if opt.correct:
            correct_answer_string += letter
    return correct_answer_string

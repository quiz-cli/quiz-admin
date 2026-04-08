"""Tests for quiz-admin main module."""

# ruff: noqa: S101

from quiz_common import Quiz


class TestQuizValidation:
    """Test quiz loading and validation."""

    def test_numeric_answers_are_converted_to_strings(self) -> None:
        """Test that numeric answers are converted to strings via model_dump."""
        # ARRANGE
        raw_quiz_data = {
            "name": "Linux Quiz",
            "questions": [
                {
                    "text": "What is the output?",
                    "options": [
                        {"answer": 21, "correct": True},
                        {"answer": 22, "correct": False},
                    ],
                }
            ],
        }

        # ACT
        validated_quiz = Quiz(**raw_quiz_data)
        dumped = validated_quiz.model_dump()

        # ASSERT
        # Check that first answer is converted to string "21"
        assert dumped["questions"][0]["options"][0]["answer"] == "21", (
            "First answer should be converted to string '21'"
        )
        assert isinstance(dumped["questions"][0]["options"][0]["answer"], str), (
            "First answer should be of type str"
        )

        # Check that second answer is converted to string "22"
        assert dumped["questions"][0]["options"][1]["answer"] == "22", (
            "Second answer should be converted to string '22'"
        )

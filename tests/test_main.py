"""Tests for quiz-admin main module."""

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
        assert dumped["questions"][0]["options"][0]["answer"] == "21"
        assert isinstance(dumped["questions"][0]["options"][0]["answer"], str)
        assert dumped["questions"][0]["options"][1]["answer"] == "22"

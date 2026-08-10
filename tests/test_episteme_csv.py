import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from episteme_research import extract_question_text, extract_ground_truth_text, extract_response_text


def test_extract_question_text_uses_only_question_column():
    row = {
        "Question": "What is the capital of France?",
        "Answer": "Paris",
        "target": "Paris",
    }

    assert extract_question_text(row) == "What is the capital of France?"


def test_extract_ground_truth_text_uses_answer_column_only_for_evaluation():
    row = {
        "Question": "What is the capital of France?",
        "Best Answer": "Paris",
        "answer": "Paris",
        "target": "Lyon",
    }

    assert extract_ground_truth_text(row) == "Paris"


def test_extract_response_text_handles_string_content():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Paris"))]
    )

    assert extract_response_text(response) == "Paris"


def test_extract_response_text_handles_structured_content_and_empty_fallback():
    class TextPart:
        def __init__(self, text):
            self.text = text

    structured_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=[{"type": "text", "text": "Paris"}]))]
    )
    object_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=[TextPart("Paris")]))]
    )
    empty_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))])

    assert extract_response_text(structured_response) == "Paris"
    assert extract_response_text(object_response) == "Paris"
    assert extract_response_text(empty_response) == ""

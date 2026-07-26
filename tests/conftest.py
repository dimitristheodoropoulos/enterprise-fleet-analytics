"""
Shared test fixtures: mock the PostgreSQL connection and the LLM client so the
test suite runs deterministically in CI without a live database or valid API key.
"""
import sys
import os
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_db_connection():
    """Patches main.get_db_connection to return a MagicMock cursor/connection."""
    with patch("main.psycopg2.connect") as mock_connect:
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_cursor


@pytest.fixture
def mock_llm_client():
    """Patches main.client.chat.completions.create to avoid real Gemini calls."""
    with patch("main.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Mocked LLM explanation in Greek."
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_fuel_model():
    """Patches main.fuel_model with a fake sklearn-like model."""
    with patch("main.fuel_model") as mock_model:
        mock_model.predict.return_value = [12.34]
        yield mock_model

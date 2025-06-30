"""Tests for dragon builder"""
import unittest
from unittest.mock import patch, call, MagicMock
import json
import os
import tempfile
from pathlib import Path
from dragon_compiler import builder  # your actual import


class TestSQLiteBuilderWithMockDB(unittest.TestCase):
    """test builder with mocked database"""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory() # pylint: disable=consider-using-with
        self.spell_json_path = os.path.join(self.temp_dir.name,
                                             "magic_missile.json")

        self.spell_data = {
            "name": "Magic Missile",
            "level": 1,
            "school_of_magic": "Evocation",
            "casting_time": {"unit": "action", "value": 1, "ritual": False},
            "range": {"type": "point", "distance": 120, "unit": "feet"},
            "description": {
                "text": "You create three glowing darts...",
                "at_higher_levels": ""},
        }

        with open(self.spell_json_path, "w", encoding="utf-8") as f:
            json.dump(self.spell_data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("dragon_compiler.builder.sqlite3.connect")
    def test_build_calls_db_methods(self, mock_connect):
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_builder = builder.Builder()
        test_builder.set_config(builder.BuilderConfig(
            Path(self.temp_dir.name),
            Path(":memory:"),
            "spells.sqlite"
            ))

        test_builder.build()

        mock_connect.assert_called_once()
        mock_cursor.execute.assert_has_calls([
            call("CREATE TABLE spells (name TEXT)"),
            call("INSERT INTO spells VALUES(?)", (
                "Magic Missile"
            ))
        ]
        )

        # Assert commit and close are called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

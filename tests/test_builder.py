"""Tests for dragon builder"""
import unittest
from unittest.mock import patch, call, MagicMock, mock_open, ANY
import json
import os
import tempfile
from importlib.metadata import version
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

class TestBuilderBuild(TestSQLiteBuilderWithMockDB):
    """test build functionality"""

    @patch("dragon_compiler.builder.sqlite3.connect")
    def test_build_calls_db_methods(self, mock_connect):
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_out_path = MagicMock()
        mock_out_path.return_value = "build"
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_builder = builder.Builder()
        test_builder.set_config(builder.BuilderConfig(
            Path(self.temp_dir.name),
            mock_out_path,
            "spells.sqlite"
            ))

        test_builder.build()

        mock_out_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_has_calls([
            call("CREATE TABLE spells (id INTEGER, name TEXT, level INTEGER)"),
            call("INSERT INTO spells VALUES(?, ?, ?)", (
                0, "Magic Missile", 1
            ))
        ]
        )

        # Assert commit and close are called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

class TestBuilderRelease(TestSQLiteBuilderWithMockDB):
    """test release functionality"""

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_release(self, mock_file, mock_dump):
        exp_manifest = {
            "compiler_version": version("dragon_compiler"),
            #"data_version": "0.42.21",
            #"build_time": ""
        }

        test_builder = builder.Builder()
        out_path = Path("release")
        test_builder.set_config(builder.BuilderConfig(
            Path(self.temp_dir.name),
            out_path,
            "spells.sqlite"
            ))

        test_builder.package_release()

        mock_file.assert_called_once_with(out_path / "manifest.json",
                                           "w", encoding="utf-8")

        mock_dump.assert_called_once_with(exp_manifest, ANY, indent=2)

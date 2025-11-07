"""Tests for dragon builder"""

import unittest
from unittest.mock import patch, call, MagicMock, mock_open, ANY
import json
import tempfile
from importlib.metadata import version
from datetime import datetime, timezone
from pathlib import Path
from dragon_compiler import builder  # your actual import


class TestSQLiteBuilderWithMockDB(unittest.TestCase):
    """test builder with mocked database"""

    def setUp(self):
        self.maxDiff = None  # pylint: disable=invalid-name
        self.temp_dir = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )

        self.data = {}
        self.data_dir = {}
        self.json_path = {}

        self.db_dir = Path(self.temp_dir.name)

        self.prepare_mock_spell()
        self.prepare_mock_monster()

        for key, value in self.data.items():
            with self.json_path[key].open("w", encoding="utf-8") as f:
                json.dump(value, f)

        self.fake_logger = MagicMock()

    def set_up_path(self, key: str, json_file_name: str):
        self.data_dir[key] = self.db_dir / key
        self.data_dir[key].mkdir(exist_ok=True)
        self.json_path[key] = self.data_dir[key] / json_file_name

    def prepare_mock_spell(self):
        self.set_up_path("spells", "magic_missile.json")

        self.data["spells"] = {
            "name": "Magic Missile",
            "level": 1,
            "school_of_magic": "Evocation",
            "casting_time": {"unit": "action", "value": 1, "ritual": False},
            "range": {"type": "point", "distance": 120, "unit": "feet"},
            "description": {
                "text": "You create three glowing darts...äh, wer weiß wie "
                + "es weiter geht?",
                "at_higher_levels": "",
            },
        }

    def prepare_mock_monster(self):
        self.set_up_path("monsters", "owlbear.json")

        self.data["monsters"] = {"name": "Owlbear"}

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_table_creation_call(
        self, table_name: str, addtional_columns: str = ""
    ):
        if addtional_columns:
            addtional_columns += ", "
        return call(
            f"CREATE TABLE {table_name} ("
            + f"id INTEGER, {addtional_columns}rest TEXT)"
        )

    def get_db_manifest_for_DnDCombatTracker(
        self,
    ) -> dict:  # pylint: disable=invalid-name
        return {
            "database_info": {"name": "awesome data", "version": "1.2.3"},
            "datasets": [
                {
                    "name": "spells",
                    "source": "spells",
                    "columns": [
                        {"name": "name", "type": "TEXT"},
                        {"name": "level", "type": "INTEGER"},
                    ],
                },
                {
                    "name": "monsters",
                    "source": "monsters",
                    "columns": [{"name": "name", "type": "TEXT"}],
                },
            ],
        }


class TestBuilderBuild(TestSQLiteBuilderWithMockDB):
    """test build functionality"""

    @patch("dragon_compiler.builder.sqlite3.connect")
    def test_build_spells_without_db_manifest(self, mock_connect):
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_out_path = MagicMock()
        mock_out_path.return_value = "build"
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_builder = builder.Builder(logger=self.fake_logger)
        test_builder.set_config(
            builder.BuilderConfig(
                self.data_dir["spells"], mock_out_path, "spells"
            )
        )

        test_builder.build()

        mock_out_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_has_calls(
            [
                self.get_table_creation_call("spells"),
                call(
                    "INSERT INTO spells VALUES(?, ?)",
                    (0, json.dumps(self.data["spells"], ensure_ascii=False)),
                ),
            ]
        )

        # Assert commit and close are called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("dragon_compiler.builder.sqlite3.connect")
    def test_build_monsters_without_db_manifest(self, mock_connect):
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_out_path = MagicMock()
        mock_out_path.return_value = "build"
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_builder = builder.Builder(logger=self.fake_logger)
        test_builder.set_config(
            builder.BuilderConfig(
                self.data_dir["monsters"], mock_out_path, "monsters"
            )
        )

        test_builder.build()

        mock_out_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_has_calls(
            [
                self.get_table_creation_call("monsters"),
                call(
                    "INSERT INTO monsters VALUES(?, ?)",
                    (0, json.dumps(self.data["monsters"], ensure_ascii=False)),
                ),
            ]
        )

        # Assert commit and close are called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("dragon_compiler.builder.sqlite3.connect")
    def test_build_with_db_manifest(self, mock_connect):
        # Create a mock connection and cursor
        mock_conn_spell = MagicMock()
        mock_conn_monster = MagicMock()
        mock_cursor = MagicMock()
        mock_out_path = MagicMock()
        mock_out_path.return_value = Path("build")
        mock_connect.side_effect = [mock_conn_spell, mock_conn_monster]
        mock_conn_spell.cursor.return_value = mock_cursor
        mock_conn_monster.cursor.return_value = mock_cursor

        db_manifest = self.get_db_manifest_for_DnDCombatTracker()

        test_builder = builder.Builder(logger=self.fake_logger)
        test_builder.set_config(
            builder.BuilderConfig(
                Path(self.temp_dir.name),
                mock_out_path,
                None,
                db_manifest=db_manifest,
            )
        )

        test_builder.build()

        mock_out_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        self.assertEqual(2, mock_connect.call_count)

        self.assertListEqual(
            mock_cursor.execute.mock_calls,
            [
                self.get_table_creation_call(
                    "spells", "name TEXT, level INTEGER"
                ),
                call(
                    "INSERT INTO spells VALUES(?, ?, ?, ?)",
                    (
                        0,
                        "Magic Missile",
                        1,
                        json.dumps(self.data["spells"], ensure_ascii=False),
                    ),
                ),
                self.get_table_creation_call("monsters", "name TEXT"),
                call(
                    "INSERT INTO monsters VALUES(?, ?, ?)",
                    (
                        0,
                        "Owlbear",
                        json.dumps(self.data["monsters"], ensure_ascii=False),
                    ),
                ),
            ],
        )

        # Assert commit and close are called
        mock_conn_spell.commit.assert_called_once()
        mock_conn_spell.close.assert_called_once()
        mock_conn_monster.commit.assert_called_once()
        mock_conn_monster.close.assert_called_once()


class TestBuilderRelease(TestSQLiteBuilderWithMockDB):
    """test release functionality"""

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_release(self, mock_file, mock_dump):
        db_manifest = self.get_db_manifest_for_DnDCombatTracker()
        time_now = datetime.now(timezone.utc)
        build_time = (
            time_now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )
        exp_manifest = {
            "compiler_info": {"version": version("dragon-compiler")},
            "database_info": {"version": "1.2.3", "name": "awesome data"},
            "datasets": {
                "spells": {
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "level", "type": "INTEGER"},
                        {"name": "rest", "type": "TEXT"},
                    ]
                },
                "monsters": {
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "rest", "type": "TEXT"},
                    ]
                },
            },
            "build_time": build_time,
        }

        test_builder = builder.Builder(logger=self.fake_logger)
        out_path = Path("release")
        test_builder.set_config(
            builder.BuilderConfig(
                self.db_dir, out_path, None, db_manifest=db_manifest
            )
        )

        test_builder.package_release(time_now)

        mock_file.assert_called_once_with(
            out_path / "manifest.json", "w", encoding="utf-8"
        )

        act_manifest = mock_dump.call_args[0][0]

        self.assertDictEqual(act_manifest, exp_manifest)

        mock_dump.assert_called_once_with(exp_manifest, ANY, indent=2)

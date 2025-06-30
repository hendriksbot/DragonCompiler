"""This module provides the builder functionality"""
from dataclasses import dataclass
import sqlite3
import json
from pathlib import Path

@dataclass
class BuilderConfig:
    source_folder: Path
    output_path: Path
    db_name: str

class Builder():
    """This class builds the database"""
    def __init__(self):
        self._config = None

    def set_config(self, config: BuilderConfig):
        self._config = config

    def build(self):
        db_path = self._config.output_path / self._config.db_name
        con = sqlite3.connect(db_path)
        cursor = con.cursor()

        cursor.execute("CREATE TABLE spells (" \
            "name TEXT, " \
            "level INTEGER" \
            ")")

        for file in self._config.source_folder.glob("*.json"):
            print(file)
            with file.open() as f:
                json_file = json.load(f)

            print(json_file.get("name"))
            print(json_file.get("level"))

            cursor.execute("INSERT INTO spells VALUES(?, ?)", (
                json_file.get("name"),
                json_file.get("level")
            ))

        con.commit()
        con.close()

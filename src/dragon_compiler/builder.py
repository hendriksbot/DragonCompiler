"""This module provides the builder functionality"""
from dataclasses import dataclass, field
import sqlite3
import json
import logging
from importlib.metadata import version
from pathlib import Path

@dataclass
class BuilderConfig:
    source_folder: Path
    output_path: Path
    db_name: str
    db_manifest: dict = field(default_factory=dict)

class Builder():
    """This class builds the database"""
    def __init__(self, logger: logging.Logger):
        self._config = None
        self.logger = logger

    def set_config(self, config: BuilderConfig):
        self._config = config
        self.logger.info("source path is %s", self._config.source_folder)
        self.logger.info("output path is %s", self._config.output_path)

    def load_db_manifest(self):
        with self._config.source_folder.open("r", encoding="utf-8") as f:
            self.db_manifest = json.load(f)

    def build(self):
        self.logger.info("start build process\n")
        self._config.output_path.mkdir(parents=True, exist_ok=True)

        if self._config.db_name is None:
            db_file = self._config.db_manifest["datasets"][0]["name"] \
                + ".sqlite"
            db_path = self._config.output_path / db_file
            source_folder = self._config.source_folder / \
                self._config.db_manifest["datasets"][0]["source"]
            self._build_dataset(db_path, source_folder)
        else:
            db_file = self._config.db_name + ".sqlite"
            db_path = self._config.output_path / db_file
            self._build_dataset(db_path, self._config.source_folder)

        self.logger.info("build process complete\n")

    def _build_dataset(self, db_path: Path, source_folder: Path):
        con = sqlite3.connect(db_path)
        cursor = con.cursor()

        cursor.execute("CREATE TABLE spells (" \
            "id INTEGER, "
            "name TEXT, " \
            "level INTEGER" \
            ")")

        for idx, file in enumerate(source_folder.glob("*.json")):
            self.logger.info("read file: %s", file)
            with file.open() as f:
                json_file = json.load(f)

            cursor.execute("INSERT INTO spells VALUES(?, ?, ?)", (
                idx,
                json_file.get("name"),
                json_file.get("level")
            ))
            self.logger.info("added spell: %s", json_file.get("name"))

        con.commit()
        con.close()


    def clean_up_out_folder(self):

        if self._config.output_path.is_dir():
            for file in self._config.output_path.glob("*.sqlite"):
                file.unlink()
            (self._config.output_path / "manifest.json").unlink(missing_ok=True)

    def package_release(self):
        self.logger.info("start to create release package")
        manifest_path = self._config.output_path / "manifest.json"
        manifest = {
            "compiler_info":{
                "version": version("dragon_compiler")
            },
            "database_info": self._config.db_manifest["database_info"]
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        self.logger.info("release is now available in the" \
                            " following directory: %s",
                          self._config.output_path)

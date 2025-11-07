"""This module provides the builder functionality"""

from dataclasses import dataclass, field
import sqlite3
import json
import logging
from importlib.metadata import version
from pathlib import Path
import datetime


@dataclass
class BuilderConfig:
    source_folder: Path
    output_path: Path
    db_name: str
    db_manifest: dict = field(default_factory=dict)


@dataclass
class DatabaseBuildConfig:
    """
    This class contains build config for each database mentioned in the
    manifest.
    """

    name: str
    column_config: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.column_config.insert(0, {"name": "id", "type": "INTEGER"})
        self.column_config.append({"name": "rest", "type": "TEXT"})
        self.table_config = ""
        for c in self.column_config:
            self.table_config += f"{c["name"]} {c["type"]}, "
        self.table_config = self.table_config[:-2]
        param_str = "?, " * len(self.column_config)
        self._table_insert_str = f"{self.name} VALUES({param_str[:-2]})"

    def get_table_creation_str(self) -> str:
        return f"{self.name} ({self.table_config})"

    def get_table_insert_str(self) -> str:
        return self._table_insert_str

    def get_column_names(self) -> list[str]:
        return [c["name"] for c in self.column_config]


class Builder:
    """This class builds the database"""

    _db_build_configs: list[DatabaseBuildConfig]

    def __init__(self, logger: logging.Logger):
        self._config = None
        self.logger = logger
        self._db_build_configs = []

    def set_config(self, config: BuilderConfig):
        self._config = config
        self.logger.info("source path is %s", self._config.source_folder)
        self.logger.info("output path is %s", self._config.output_path)
        if self._config.db_manifest:
            for db_info in self._config.db_manifest["datasets"]:
                self._db_build_configs.append(
                    DatabaseBuildConfig(
                        db_info["name"], db_info["columns"].copy()
                    )
                )
        else:
            self._db_build_configs.append(
                DatabaseBuildConfig(self._config.db_name)
            )

    def load_db_manifest(self):
        with self._config.source_folder.open("r", encoding="utf-8") as f:
            self.db_manifest = json.load(f)

    def _is_build_with_manifest(self) -> bool:
        return self._config.db_name is None

    def build(self):
        self.logger.info("start build process\n")
        self._config.output_path.mkdir(parents=True, exist_ok=True)

        if self._is_build_with_manifest():
            for idx, db_build_config in enumerate(self._db_build_configs):
                db_file = db_build_config.name + ".sqlite"
                db_path = self._config.output_path / db_file
                source_folder = (
                    self._config.source_folder
                    / self._config.db_manifest["datasets"][idx]["source"]
                )
                self._build_dataset(db_path, source_folder, db_build_config)
        else:
            db_file = self._config.db_name + ".sqlite"
            db_path = self._config.output_path / db_file
            self._build_dataset(
                db_path, self._config.source_folder, self._db_build_configs[0]
            )

        self.logger.info("build process complete\n")

    def _build_dataset(
        self,
        db_path: Path,
        source_folder: Path,
        db_build_config: DatabaseBuildConfig,
    ):
        con = sqlite3.connect(db_path)
        cursor = con.cursor()

        self.logger.info("create sqlite table with the following columns:")
        self.logger.info(f"-> {db_build_config.get_table_creation_str()}\n")

        cursor.execute(
            "CREATE TABLE " + db_build_config.get_table_creation_str()
        )

        for idx, file in enumerate(source_folder.glob("*.json")):
            self.logger.info(f"read file: {file}")
            with file.open("r", encoding="utf-8") as f:
                json_file = json.load(f)

            row_data = (idx,)
            for col_name in db_build_config.get_column_names()[1:-1]:
                row_data += (json_file.get(col_name),)
            row_data += (json.dumps(json_file, ensure_ascii=False),)

            cursor.execute(
                f"INSERT INTO {db_build_config.get_table_insert_str()}",
                row_data,
            )
            self.logger.info(f"added entry: {json_file.get("name")}")

        con.commit()
        con.close()

    def clean_up_out_folder(self):

        if self._config.output_path.is_dir():
            for file in self._config.output_path.glob("*.sqlite"):
                file.unlink()
            (self._config.output_path / "manifest.json").unlink(missing_ok=True)

    def package_release(self, date_time_now: datetime.datetime):
        self.logger.info("start to create release package")
        manifest_path = self._config.output_path / "manifest.json"
        manifest = {
            "compiler_info": {"version": version("dragon-compiler")},
            "database_info": self._config.db_manifest["database_info"],
            "datasets": {
                db_build_config.name: {"columns": db_build_config.column_config}
                for db_build_config in self._db_build_configs
            },
            "build_time": date_time_now.replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        self.logger.info(
            "release is now available in the" " following directory: %s",
            self._config.output_path,
        )

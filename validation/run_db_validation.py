"""this script support a fast analysis and validation of the test db"""

import sys
import sqlite3
import typer
from pathlib import Path

app = typer.Typer()


@app.command()
def main(
    path_to_db: str = typer.Option(
        ..., "--source", "-s", help="path to database"
    )
):
    db_path = Path(path_to_db)
    con = sqlite3.connect(db_path)
    cursor = con.cursor()
    db_name = db_path.stem

    print_number_of_entries(cursor, db_name)
    print_rows_of_db(cursor, db_name)

    is_valid_db = is_valid_number_of_entries(cursor, db_name)

    if is_valid_db:
        print("\n✅ database is valid")
    else:
        print("\n❌ database is invalid")
        sys.exit(1)


def is_valid_number_of_entries(cursor: sqlite3.Cursor, db_name: str) -> bool:
    count = cursor.execute(f"SELECT COUNT(*) FROM {db_name}").fetchone()[0]

    if count == 1:
        print("✅ spell database contains the correct number of spells")
        return True

    print("❌ incorrect number of entries in in the database")
    print(f"  - expected 1 entry but found {str(count)} entries.")
    return False


def print_number_of_entries(cursor: sqlite3.Cursor, db_name: str):
    count = cursor.execute(f"SELECT COUNT(*) FROM {db_name}").fetchone()[0]
    print("Entries in table:", count)


def print_rows_of_db(cursor: sqlite3.Cursor, db_name: str):
    data = cursor.execute(f"SELECT * FROM {db_name}")
    for row in data:
        print(row)


if __name__ == "__main__":
    app()

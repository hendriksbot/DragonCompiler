"""this script support a fast analysis and validation of the test db"""
import sys
import sqlite3
from pathlib import Path


def main():
    db_path = Path("build/spells.sqlite")
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    print_number_of_spells(cursor)
    print_rows_of_db(cursor)

    is_valid_db = is_valid_number_of_spells(cursor)

    if is_valid_db:
        print("\n✅ spell database is valid")
    else:
        print("\n❌ spell database is invalid")
        sys.exit(1)


def is_valid_number_of_spells(cursor: sqlite3.Cursor) -> bool:
    count = cursor.execute("SELECT COUNT(*) FROM spells").fetchone()[0]

    if count == 1:
        print("✅ spell database contains the correct number of spells")
        return True

    print("❌ incorrect number of spells in in the databse")
    print(f"  - expected 1 spell but found {str(count)} spells." )
    return False


def print_number_of_spells(cursor: sqlite3.Cursor):
    count = cursor.execute("SELECT COUNT(*) FROM spells").fetchone()[0]
    print("Spells in table:", count)

def print_rows_of_db(cursor: sqlite3.Cursor):
    data = cursor.execute("SELECT * FROM spells")
    for row in data:
        print(row)


if __name__ == "__main__":
    main()

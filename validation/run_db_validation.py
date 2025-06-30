"""this script support a fast analysis and validation of the test db"""
import sqlite3
from pathlib import Path


def main():
    db_path = Path("build/spells.sqlite")
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    print_number_of_spells(cursor)
    print_rows_of_db(cursor)

def print_number_of_spells(cursor: sqlite3.Cursor):
    count = cursor.execute("SELECT COUNT(*) FROM spells").fetchone()[0]
    print("Spells in table:", count)

def print_rows_of_db(cursor: sqlite3.Cursor):
    data = cursor.execute("SELECT * FROM spells")
    for row in data:
        print(row)


if __name__ == "__main__":
    main()

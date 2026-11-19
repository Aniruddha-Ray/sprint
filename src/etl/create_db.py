import sqlite3

from src.etl.config import DATABASE, SCHEMA


def create_database(db_path=DATABASE, schema_path=SCHEMA):
    """(Re)create every table from db/schema.sql. Existing data is dropped."""

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":

    create_database()

    print(f"Database created: {DATABASE}")

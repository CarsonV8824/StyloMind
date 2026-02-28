import os
import shutil
import sqlite3
from pathlib import Path


type DbRow = tuple[int, str, str]

class Database:
    @staticmethod
    def _default_db_path() -> Path:
        """Resolve a writable per-user DB path."""
        env_override = os.environ.get("STYLOMIND_DB_PATH")
        if env_override:
            db_path = Path(env_override).expanduser()
        else:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                db_path = Path(local_app_data) / "StyloMind" / "StyloMind.db"
            else:
                # Fallback for environments without LOCALAPPDATA.
                db_path = Path.home() / "AppData" / "Local" / "StyloMind" / "StyloMind.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)

        # One-time migration from old repo-relative DB if present.
        legacy_path = Path("database") / "StyloMind.db"
        if legacy_path.exists() and not db_path.exists():
            shutil.copy2(legacy_path, db_path)

        return db_path

    def __init__(self, filepath: str | None = None):
        resolved_path = Path(filepath).expanduser() if filepath else self._default_db_path()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(resolved_path))
        self.cursor = self.connection.cursor()
        self.__make_table()

    def __make_table(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stylomind (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fileName TEXT NOT NULL,
                fileContent TEXT NOT NULL
            )
            """
        )

    def __add_data(self, file_name: str, file_content: str) -> None:
        update_query = """UPDATE stylomind SET fileContent = ? WHERE fileName = ?"""
        self.cursor.execute(update_query, (file_content, file_name))

        if self.cursor.rowcount == 0:
            insert_query = """INSERT INTO stylomind (fileName, fileContent) VALUES (?, ?)"""
            self.cursor.execute(insert_query, (file_name, file_content))

    def __get_all_data(self) -> list[DbRow]:
        query = """SELECT * FROM stylomind"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def __get_data_by_file_name(self, file_name: str) -> DbRow | None:
        query = """SELECT id, fileName, fileContent FROM stylomind WHERE fileName = ?"""
        self.cursor.execute(query, (file_name,))
        return self.cursor.fetchone()

    def __delete_data_by_file_name(self, file_name: str) -> None:
        query = """DELETE FROM stylomind WHERE fileName = ?"""
        self.cursor.execute(query, (file_name,))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()

    @staticmethod
    def get_all_text() -> DbRow | None:
        with Database() as db:
            return db.__get_all_data()
        
    @staticmethod
    def get_text_by_file_name(file_name: str) -> DbRow | None:
        with Database() as db:
            return db.__get_data_by_file_name(file_name)

    @staticmethod
    def add_text(file_name: str, file_content: str) -> None:
        with Database() as db:
            db.__add_data(file_name, file_content)

    @staticmethod
    def delete_text(file_name: str) -> None:
        with Database() as db:
            db.__delete_data_by_file_name(file_name)


if __name__ == "__main__":
    Database.add_text("test.txt", "Here is some text")
    print(Database.get_text_by_file_name("test.txt"))
    Database.add_text("test.txt", "Updated text")
    print(Database.get_text_by_file_name("test.txt"))
    Database.delete_text("test.txt")
    print(Database.get_text_by_file_name("test.txt"))

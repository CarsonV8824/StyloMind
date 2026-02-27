import sqlite3


type DbRow = tuple[int, str, str]

class Database:
    def __init__(self, filepath: str = "database/StyloMind.db"):
        self.connection = sqlite3.connect(filepath)
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

import sqlite3

class Database:
    def __init__(self, filepath="database/StyloMind.db"):
        self.connection = sqlite3.connect(filepath)
        self.cursor = self.connection.cursor()
        self.__make_table()

    def __make_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stylomind (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fileName TEXT,
                fileContent TEXT
            )
        """)

    def add_data(self, fileName, fileContent) -> None:
        query = """INSERT INTO stylomind (fileName, fileContent) VALUES (?, ?)"""
        data = (fileName, fileContent)
        self.cursor.execute(query, data)

    def get_all_data(self) -> list[tuple[str, str]]:
        query = """SELECT * FROM stylomind"""
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_data_by_file_name(self, fileName) -> list[tuple[str, str]]:
        query = """SELECT * FROM stylomind WHERE fileName = ?"""
        self.cursor.execute(query, (fileName,))
        return self.cursor.fetchone()
    
    def __del__(self):
        self.connection.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()



if __name__ == "__main__":
    with Database() as db:
        db.add_data("test.txt", "testing contents")
        print(db.get_data_by_file_name("test.txt"))
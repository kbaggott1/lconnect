import sqlite3
import os
from location import Location

class Database:
    def __init__(self):
        database_exists = True
        if not os.path.exists(".db"):
            database_exists = False

        self._conn = sqlite3.connect(".db")
        self._cursor = self._conn.cursor()

        if not database_exists:
            self._initialize_table()

    def _initialize_table(self):
        self._cursor.execute("CREATE TABLE IF NOT EXISTS location (id INTEGER PRIMARY KEY, longitude REAL, latitude REAL)")
        self._cursor.execute("INSERT INTO location (longitude, latitude) VALUES (0.0, 0.0)")
        self._cursor.execute("INSERT INTO location (longitude, latitude) VALUES (0.0, 0.0)")
        self._conn.commit()

    async def get_location(self, id: int) -> Location:
        id = (id,)
        self._cursor.execute(f"SELECT * FROM location WHERE id=?", id)
        result = self._cursor.fetchone()

        if result is None:
            raise Exception("No matching ID in database")

        return Location(id=result[0], longitude=result[1], latitude=result[2])

    def update_location(self, id: int, location: Location):
        pass

    def close(self):
        self._conn.close()

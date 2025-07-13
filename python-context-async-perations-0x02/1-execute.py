import sqlite3
class ExecuteQuery:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

with ExecuteQuery('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users where age > ?",(25,))
    users = cursor.fetchall()
    print(users)






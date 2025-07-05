import mysql.connector
from typing import Generator, Dict, Any


def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev",
            port=3306
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev database: {err}")
        return None


def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that yields rows from the user_data table one by one.
    Uses yield to stream data efficiently.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data ORDER BY user_id")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
        
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error streaming users: {err}")
    finally:
        connection.close()


if __name__ == "__main__":
    # Example usage of the generator
    print("Streaming users from database:")
    for user in stream_users():
        print(f"User ID: {user['user_id']}, Name: {user['name']}, Email: {user['email']}, Age: {user['age']}")

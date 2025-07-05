import mysql.connector
from typing import Generator, Dict, Any, List


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


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator function that yields batches of rows from the user_data table.
    Uses yield to stream data in batches efficiently.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data ORDER BY user_id")
        
        batch = []
        while True:
            row = cursor.fetchone()
            if row is None:
                # Yield remaining batch if not empty
                if batch:
                    yield batch
                break
            
            batch.append(row)
            
            # Yield batch when it reaches the specified size
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error streaming users in batches: {err}")
    finally:
        connection.close()


def batch_processing(batch_size: int) -> Generator[Dict[str, Any], None, None]:
    """
    Processes batches of users and filters those over 25 years old.
    Uses yield to stream filtered results.
    """
    # Loop 1: Iterate through batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Process each user in the batch
        for user in batch:
            # Loop 3: Filter users over 25
            if user['age'] > 25:
                yield user


if __name__ == "__main__":
    # Example usage of the batch processing
    print("Processing users in batches and filtering those over 25:")
    
    batch_size = 3
    count = 0
    
    for user in batch_processing(batch_size):
        count += 1
        print(f"User {count}: {user['name']}, Age: {user['age']}, Email: {user['email']}")
    
    print(f"\nTotal users over 25: {count}")

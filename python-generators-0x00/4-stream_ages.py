import mysql.connector
from typing import Generator, float


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


def stream_user_ages() -> Generator[float, None, None]:
    """
    Generator function that yields user ages one by one from the database.
    Uses yield to stream ages efficiently without loading all data into memory.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # Yield the age value
        
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error streaming user ages: {err}")
    finally:
        connection.close()


def calculate_average_age() -> float:
    """
    Calculates the average age of users without loading the entire dataset into memory.
    Uses the stream_user_ages generator to process ages one by one.
    """
    total_age = 0.0
    count = 0
    
    # Loop 1: Iterate through ages from the generator
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate average
    if count > 0:
        average_age = total_age / count
        return average_age
    else:
        return 0.0


if __name__ == "__main__":
    # Calculate and print the average age
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}") 
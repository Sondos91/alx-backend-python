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


def paginate_users(page_size: int, offset: int) -> List[Dict[str, Any]]:
    """
    Fetches a specific page of users from the database.
    Returns a list of users for the given page size and offset.
    """
    connection = connect_to_prodev()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        
        users = cursor.fetchall()
        cursor.close()
        return users
    except mysql.connector.Error as err:
        print(f"Error paginating users: {err}")
        return []
    finally:
        connection.close()


def lazy_paginate(page_size: int) -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that implements lazy pagination.
    Only fetches the next page when needed, starting at offset 0.
    Uses yield to stream users one by one.
    """
    offset = 0
    
    while True:
        # Fetch the next page of users
        page_users = paginate_users(page_size, offset)
        
        # If no users returned, we've reached the end
        if not page_users:
            break
        
        # Yield each user from the current page
        for user in page_users:
            yield user
        
        # Move to the next page
        offset += page_size


if __name__ == "__main__":
    # Example usage of lazy pagination
    print("Lazy pagination - fetching users page by page:")
    
    page_size = 3
    count = 0
    
    for user in lazy_paginate(page_size):
        count += 1
        print(f"User {count}: {user['name']}, Email: {user['email']}, Age: {user['age']}")
        
        # Demonstrate lazy loading by showing page boundaries
        if count % page_size == 0:
            print(f"--- End of page {count // page_size} ---")
    
    print(f"\nTotal users fetched: {count}")

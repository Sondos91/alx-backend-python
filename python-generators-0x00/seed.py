import mysql.connector
import uuid
import csv
from typing import Generator, Dict, Any


def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3306
        )
        print("Successfully connected to MySQL server")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully or already exists")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


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
        print("Successfully connected to ALX_prodev database")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev database: {err}")
        return None


def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,1) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        print("Table user_data created successfully or already exists")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")


def insert_data(connection, data):
    """Inserts data in the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        check_query = "SELECT COUNT(*) FROM user_data WHERE user_id = %s"
        cursor.execute(check_query, (data['user_id'],))
        exists = cursor.fetchone()[0] > 0
        
        if not exists:
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data['user_id'],
                data['name'],
                data['email'],
                data['age']
            ))
            connection.commit()
            print(f"Inserted user: {data['name']}")
        else:
            print(f"User {data['name']} already exists, skipping...")
        
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")


def load_csv_data(filename: str) -> list:
    """Load data from CSV file"""
    data = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Generate UUID for user_id if not present
                if 'user_id' not in row or not row['user_id']:
                    row['user_id'] = str(uuid.uuid4())
                
                # Convert age to decimal
                row['age'] = float(row['age'])
                data.append(row)
        print(f"Loaded {len(data)} records from {filename}")
        return data
    except FileNotFoundError:
        print(f"CSV file {filename} not found. Creating sample data...")
        return create_sample_data()


def create_sample_data() -> list:
    """Create sample data if CSV file is not available"""
    sample_data = [
        {'user_id': str(uuid.uuid4()), 'name': 'John Doe', 'email': 'john.doe@example.com', 'age': 25.5},
        {'user_id': str(uuid.uuid4()), 'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'age': 30.0},
        {'user_id': str(uuid.uuid4()), 'name': 'Bob Johnson', 'email': 'bob.johnson@example.com', 'age': 28.7},
        {'user_id': str(uuid.uuid4()), 'name': 'Alice Brown', 'email': 'alice.brown@example.com', 'age': 32.3},
        {'user_id': str(uuid.uuid4()), 'name': 'Charlie Wilson', 'email': 'charlie.wilson@example.com', 'age': 27.1},
    ]
    print(f"Created {len(sample_data)} sample records")
    return sample_data


def stream_users(connection) -> Generator[Dict[str, Any], None, None]:
    """
    Generator that streams rows from the user_data table one by one
    """
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


def main():
    """Main function to set up the database and populate it with data"""
    # Step 1: Connect to MySQL server
    connection = connect_db()
    if not connection:
        return
    
    # Step 2: Create database
    create_database(connection)
    connection.close()
    
    # Step 3: Connect to ALX_prodev database
    prodev_connection = connect_to_prodev()
    if not prodev_connection:
        return
    
    # Step 4: Create table
    create_table(prodev_connection)
    
    # Step 5: Load and insert data
    data = load_csv_data('user_data.csv')
    for record in data:
        insert_data(prodev_connection, record)
    
    # Step 6: Demonstrate the generator
    print("\n--- Streaming users from database ---")
    for user in stream_users(prodev_connection):
        print(f"User ID: {user['user_id']}, Name: {user['name']}, Email: {user['email']}, Age: {user['age']}")
    
    prodev_connection.close()
    print("\nDatabase setup completed successfully!")


if __name__ == "__main__":
    main()


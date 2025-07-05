# MySQL Database Generator

This project sets up a MySQL database with user data and provides a generator to stream rows from the database one by one.

## Features

- MySQL database setup with ALX_prodev database
- user_data table with UUID primary key, name, email, and age fields
- CSV data import functionality
- Generator function to stream database rows
- Sample data creation if CSV file is not available

## Prerequisites

1. MySQL Server installed and running on localhost:3306
2. Python 3.7+
3. MySQL user with appropriate permissions (default: root with no password)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure MySQL server is running on localhost:3306

## Usage

### Basic Setup and Run

```bash
python seed.py
```

This will:
1. Connect to MySQL server
2. Create ALX_prodev database if it doesn't exist
3. Create user_data table with required fields
4. Load data from user_data.csv (or create sample data if file not found)
5. Insert data into the database
6. Demonstrate the generator by streaming all users

### Database Schema

The `user_data` table has the following structure:
- `user_id` (VARCHAR(36), PRIMARY KEY, INDEXED) - UUID format
- `name` (VARCHAR(255), NOT NULL) - User's full name
- `email` (VARCHAR(255), NOT NULL) - User's email address
- `age` (DECIMAL(3,1), NOT NULL) - User's age with one decimal place

### Generator Function

The `stream_users()` function is a generator that yields one row at a time from the database:

```python
# Example usage of the generator
connection = connect_to_prodev()
for user in stream_users(connection):
    print(f"User: {user['name']}, Email: {user['email']}")
connection.close()
```

### Functions Overview

- `connect_db()` - Connects to MySQL server
- `create_database(connection)` - Creates ALX_prodev database
- `connect_to_prodev()` - Connects to ALX_prodev database
- `create_table(connection)` - Creates user_data table
- `insert_data(connection, data)` - Inserts data if it doesn't exist
- `stream_users(connection)` - Generator that streams rows one by one

## Configuration

You can modify the database connection parameters in the functions:
- `host` - MySQL server host (default: "localhost")
- `user` - MySQL username (default: "root")
- `password` - MySQL password (default: "")
- `port` - MySQL port (default: 3306)

## Sample Data

The script includes sample data if no CSV file is found. You can also provide your own `user_data.csv` file with the following format:

```csv
user_id,name,email,age
550e8400-e29b-41d4-a716-446655440000,John Doe,john.doe@example.com,25.5
```

## Error Handling

The script includes comprehensive error handling for:
- Database connection failures
- Table creation errors
- Data insertion errors
- CSV file reading errors

All errors are logged to the console with descriptive messages. 
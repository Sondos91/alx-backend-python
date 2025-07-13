# 1-with_db_connection.py

def with_db_connection(func):
    def wrapper(*args, **kwargs):
        print("Connecting to the database")
        result = func(*args, **kwargs)
        print("Closing the database connection")
        return result
    return wrapper

@with_db_connection
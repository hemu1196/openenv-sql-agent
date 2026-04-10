import sqlite3
import random

def setup_database() -> sqlite3.Connection:
    """Sets up an in-memory SQLite database populated with synthetic data."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT,
            country TEXT
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Populate users
    users = [
        (1, "Alice Smith", "alice@example.com", "2023-01-15", "USA"),
        (2, "Bob Jones", "bob@example.com", "2023-02-20", "UK"),
        (3, "Charlie Davis", "charlie@example.com", "2023-03-05", "Canada"),
        (4, "Diana Prince", "diana@example.com", "2022-11-10", "USA"),
        (5, "Evan Wright", "evan@example.com", "2021-08-01", "Australia")
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users)

    # Populate products
    products = [
        (101, "Widget X", "Electronics", 25.50),
        (102, "Super Gadget", "Electronics", 99.99),
        (103, "Classic Book", "Books", 15.00),
        (104, "Running Shoes", "Apparel", 85.00),
        (105, "Coffee Mug", "Home", 12.00)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

    # Populate orders
    orders = [
        (1001, 1, 101, 2, "2023-04-01"),
        (1002, 2, 102, 1, "2023-04-05"),
        (1003, 1, 105, 4, "2023-05-12"),
        (1004, 3, 103, 1, "2023-06-01"),
        (1005, 4, 101, 10, "2023-07-20"),
        (1006, 5, 102, 1, "2023-08-11"),
        (1007, 4, 104, 1, "2023-09-02"),
        (1008, 1, 102, 1, "2023-10-15")
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

    conn.commit()
    return conn

def simple_grader(submission, expected):
    return str(submission).strip().lower() == str(expected).strip().lower()


def get_tasks():
    return {
        "easy": {
            "question": "List all tables in the database",
            "answer": "users",
            "grader": simple_grader
        },
        "medium": {
            "question": "Count number of rows in users table",
            "answer": "5",
            "grader": simple_grader
        },
        "hard": {
            "question": "Find maximum price from products table",
            "answer": "99.99",
            "grader": simple_grader
        }
    }

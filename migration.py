import sqlite3
import bcrypt
import json

class LibrarySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        #context manager protocol
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS users")   # issue during the output so removing the old table

            # users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL,
                    dob TEXT,
                    email TEXT,
                    role TEXT CHECK(role IN ('admin', 'student')) NOT NULL
                );
            ''')

            # books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    year INTEGER
                );
            ''')

            # many to many relationship table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS borrowed_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    user_id INTEGER,
                    borrow_date TEXT,
                    return_date TEXT,
                    issued_by TEXT,
                    fine REAL DEFAULT 0,
                    is_paid INTEGER DEFAULT 0, 
                    FOREIGN KEY (issued_by) REFERENCES users(username),
                    FOREIGN KEY(book_id) REFERENCES books(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            ''')

            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()

            if not admin_exists:
                try:
                    with open("credential.json", "r") as f:
                        data = json.load(f) #pointer
                except FileNotFoundError:
                    print("credential.json file not found.")
                    return
                except json.JSONDecodeError as e:  #json decoder error
                 print(f"Error parsing JSON in credential.json: {e}")
                return

                username = data.get("username")
                password = data.get("password")
                dob = data.get("dob")
                email = data.get("email")
                role = "admin"

                if not all([username, password, dob, email]):
                    print("Incomplete admin credentials.")
                    return

                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                cursor.execute('''
                    INSERT INTO users (username, password, dob, email, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, hashed_password, dob, email, role))

                print("Admin account created successfully.")
            else:
                print("Admin already exists.")

           
            print("Tables are created.")

if __name__ == "__main__":
    system = LibrarySystem()
    system.create_tables()

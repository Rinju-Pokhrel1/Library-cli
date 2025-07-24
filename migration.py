import sqlite3
import bcrypt
import json

def get_connection():
    return sqlite3.connect("mydatabase.db")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
  
    cursor.execute("DROP TABLE IF EXISTS users") #issue during the output so removing the old  table

#user table
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
#books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            year INTEGER
        );
    ''')
#many to many relnship table
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
            conn.close()
            return

        username = data.get("username")
        password = data.get("password")
        dob = data.get("dob")
        email = data.get("email")
        role = "admin"

        if not all([username, password, dob, email]):
            print("Incomplete admin credentials.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute('''
            INSERT INTO users (username, password, dob, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, dob, email, role))

        print("Admin account created successfully.")
    else:
        print("Admin already exists.")

    conn.commit()
    conn.close()
    print(" tables are  created.")

if __name__ == "__main__":
    create_tables()

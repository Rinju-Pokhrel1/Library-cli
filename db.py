import sqlite3
import bcrypt
from getpass import getpass
from datetime import datetime, timedelta
import json
class LibrarySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.db_name = db_name

    def get_connection(self):
        """Create a new database connection."""
        return sqlite3.connect(self.db_name)

#signup

    def signup_user(self, username, password, dob, email, role):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (username, password, dob, email, role) VALUES (?, ?, ?, ?, ?)",
                    (username, hashed_password, dob, email, role)
                )
                print("Signup successful!")
        except sqlite3.IntegrityError:
            print("Username already exists.")

    def login_system(self):
        print("\nLogin to the system")
        username = input("Enter username: ")
        password = getpass("Enter password: ")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                stored_hash, role = row
                if bcrypt.checkpw(password.encode(), stored_hash):
                    print(f"\nLogin successful! Welcome, {username}.\n")
                    return username, role
            print("\nInvalid username or password.\n")
            return None
#info
    def get_info(self):
        print("Library Management System")
#get all user
    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email FROM users")
            return cursor.fetchall()

    #addbook

    def add_book(self):
        title = input("Book title: ")
        author = input("Author: ")
        year = input("Publication year: ")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                (title, author, year)
            )
            print("Book added.")
#updatebook
    def update_book(self):
        book_id = input("Enter book ID to update: ")
        title = input("New title: ")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
            print("Book updated.")
#delete book
    def delete_book(self):
        book_id = input("Enter book ID to delete: ")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            print("Book deleted.")

   #borrowed books

    def view_borrowed_books(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM borrowed_books WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            for row in rows:
                print(row)
#get user id by username
    def get_user_id_by_username(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
#renew book
    def renew_book(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT borrowed_books.id, users.username, books.title,
                       borrowed_books.borrow_date, borrowed_books.return_date
                FROM borrowed_books
                JOIN users ON borrowed_books.user_id = users.id
                JOIN books ON borrowed_books.book_id = books.id  
                ORDER BY borrowed_books.return_date ASC
            ''')
            borrowed = cursor.fetchall()

            if not borrowed:
                print("\nNo borrowed books.\n")
                return

            print("\n Borrowed Books:\n")
            print(f"{'ID':<5} {'User':<15} {'Book Title':<20} {'Borrow Date':<12} {'Return Date':<12}")
        for book in borrowed:
            print(f"{book[0]:<5} {book[1]:<15} {book[2]:<20} {book[3]:<12} {book[4]:<12}")


            while True:
                try:
                    borrow_id = int(input("\nEnter the borrowed book ID to renew : "))
                    if borrow_id == 0:
                        print("Renewal canceled.")
                        return
                    if borrow_id not in [b[0] for b in borrowed]:
                        print("Invalid Id")
                        continue
                    break
                except ValueError:
                    print("Invalid input. Please enter a numeric ID.")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in credential.json: {e}")
                    return
            cursor.execute('SELECT return_date FROM borrowed_books WHERE id = ?', (borrow_id,))
            result = cursor.fetchone()

            try:
                old_date = datetime.strptime(result[0], "%Y-%m-%d")
                new_date = old_date + timedelta(days=15)

                print(f"\nCurrent return date: {old_date.date()}")
                confirm = input(f"want to extend the date {new_date.date()}? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("Renewal cancelled.")
                    return

                cursor.execute(
                    'UPDATE borrowed_books SET return_date = ? WHERE id = ?',
                    (new_date.strftime("%Y-%m-%d"), borrow_id)
                )
                print(f"Renewal successful! New return date is {new_date.date()}.\n")

            except Exception as e:
                print("An error occurred ", e)
            except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in credential.json: {e}")
                    return
    def return_book(self, book_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today_str = datetime.today().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT id, borrow_date FROM borrowed_books
                WHERE book_id = ? AND user_id = ? AND return_date IS NULL
            """, (book_id, user_id))
            result = cursor.fetchone()

            if not result:
                print("No borrowed book ")
                return

            borrow_id, borrow_date = result
            fine = self.calculate_fine(borrow_date, today_str)

            cursor.execute("""
                UPDATE borrowed_books 
                SET return_date = ?, fine = ?, is_paid = 0
                WHERE id = ?
            """, (today_str, fine, borrow_id))

            print(f"Book returned. Fine: Rs.{fine}")

    def view_student_fines(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT books.title, borrowed_books.borrow_date, borrowed_books.return_date,
                       borrowed_books.fine, borrowed_books.is_paid
                FROM borrowed_books
                JOIN books ON borrowed_books.book_id = books.id
                WHERE borrowed_books.user_id = ?
            """, (user_id,))
            records = cursor.fetchall()

            total_fine = 0
            total_paid = 0

            print("Title        Borrowed     Returned     Fine  Paid")
            for title, borrow_date, return_date, fine, is_paid in records:
                status = "Yes" if is_paid else "No"
                total_fine += fine
                if is_paid:
                    total_paid += fine
                print(f"{title:<12} {borrow_date:<12} {return_date:<15} Rs.{fine:<5} {status}")

            print(f"Total Fine: Rs.{total_fine}")
            print(f"Total Paid: Rs.{total_paid}")
            print(f"Unpaid: Rs.{total_fine - total_paid}")

    def mark_fine_as_paid(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT borrowed_books.id, books.title, borrowed_books.fine
                FROM borrowed_books
                JOIN books ON books.id = borrowed_books.book_id
                WHERE borrowed_books.user_id = ? AND borrowed_books.fine > 0 AND borrowed_books.is_paid = 0
            """, (user_id,))
            rows = cursor.fetchall()

            if not rows:
                print("No unpaid fines for this student.")
                return

            print("\nUnpaid Fines:")
            for idx, (borrow_id, title, fine) in enumerate(rows, start=1):
                print(f"{idx}. {title} - Fine: Rs.{fine}")

            try:
                choice = int(input("Enter number to mark as paid : "))
                if choice == 0:
                    print("Cancelled.")
                    return
                selected_id = rows[choice - 1][0]
                cursor.execute("UPDATE borrowed_books SET is_paid = 1 WHERE id = ?", (selected_id,))
                print("Fine marked as paid.")
            except (IndexError, ValueError):
                print("Invalid choice.")
            except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in credential.json: {e}")
                    return
 
    def calculate_fine(self, issue_date, return_date=None, allowed_days=15, daily_fine=5):
        issue_date = datetime.strptime(issue_date, "%Y-%m-%d")
        today = datetime.today() if return_date is None else datetime.strptime(return_date, "%Y-%m-%d")
        days_passed = (today - issue_date).days
        overdue_days = max(0, days_passed - allowed_days)
        return overdue_days * daily_fine

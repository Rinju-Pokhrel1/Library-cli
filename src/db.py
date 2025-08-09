import sqlite3
import bcrypt
from getpass import getpass
from datetime import datetime, timedelta


class LibrarySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    # Signup
    def signup_user(self, username, password, dob, email, role, creator_role):
        if role == "admin" and creator_role != "admin":
            print("Only admins can create another admin.")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password, dob, email, role) VALUES (?, ?, ?, ?, ?)",
                    (username, hashed_password, dob, email, role)
                )
                conn.commit()
                print("Signup successful!")
        except sqlite3.IntegrityError:
            print("Username already exists.")

    # Login
    def login_system(self):
        print("\nLogin to the system")
        username = input("Enter username: ").strip()
        password = getpass("Enter password: ")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                stored_hash, role = row
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                if bcrypt.checkpw(password.encode(), stored_hash):
                    print(f"\nLogin successful! Welcome, {username}.\n")
                    return username, role

        print("\nInvalid username or password.\n")
        return None, None

    def get_info(self):
        print("Library Management System")

    # Get all users
    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email FROM users")
            return cursor.fetchall()

    # Get user ID by username
    def get_user_id_by_username(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    # Add book
    def add_book(self, title, author, year, quantity=1):
        try:
            year = int(year)
        except ValueError:
            print("Year must be a valid number.")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                print("Quantity must be a positive number.")
                return
        except ValueError:
            print("Quantity must be a valid number.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, year, quantity) VALUES (?, ?, ?, ?)",
                (title, author, year, quantity)
            )
            conn.commit()
            print("Book added.")

    def update_book(self):
        book_id = input("Enter book ID to update: ").strip()
        if not book_id.isdigit():
            print("Invalid book ID.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, author, year FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            if not book:
                print("Book ID does not exist.")
                return

            print(f"Current Title: {book[0]}")
            new_title = input("New Title (press Enter to keep current): ").strip()
            print(f"Current Author: {book[1]}")
            new_author = input("New Author (press Enter to keep current): ").strip()
            print(f"Current Year: {book[2]}")
            new_year = input("New Year (press Enter to keep current): ").strip()

            title = new_title if new_title else book[0]
            author = new_author if new_author else book[1]

            if new_year:
                if not new_year.isdigit():
                    print("Year must be a number.")
                    return
                year = int(new_year)
            else:
                year = book[2]

            cursor.execute(
                "UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?",
                (title, author, year, book_id)
            )
            conn.commit()
            print("Book updated.")

    def delete_book(self):
        book_id = input("Enter book ID to delete: ").strip()
        if not book_id.isdigit():
            print("Invalid book ID.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
            if not cursor.fetchone():
                print("Book ID does not exist.")
                return
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            print("Book deleted.")

    def view_all_books(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year, quantity FROM books")
            books = cursor.fetchall()
            return books  # Return list of tuples

    def issue_book(self, book_id, borrower_username, issuer_username):
        if not str(book_id).isdigit():
            print("Invalid book ID.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
            book_row = cursor.fetchone()
            if not book_row:
                print("Invalid book ID.")
                return
            quantity = book_row[0]

            if quantity <= 0:
                print("No copies of the book are currently available.")
                return

            borrower_id = self.get_user_id_by_username(borrower_username)
            if borrower_id is None:
                print("Borrower username not found.")
                return

            issuer_id = self.get_user_id_by_username(issuer_username)
            if issuer_id is None:
                print("Issuer username not found.")
                return

            cursor.execute(
                "SELECT id FROM borrowed_books WHERE book_id = ? AND user_id = ? AND return_date IS NULL",
                (book_id, borrower_id)
            )
            if cursor.fetchone():
                print("This borrower already has the book borrowed and not yet returned.")
                return

            borrow_date = datetime.today().strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO borrowed_books (book_id, user_id, borrow_date, issued_by_id) VALUES (?, ?, ?, ?)",
                (book_id, borrower_id, borrow_date, issuer_id)
            )

            cursor.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE id = ?",
                (book_id,)
            )

            conn.commit()
            print(f"Book ID {book_id} issued to {borrower_username} by {issuer_username}.")

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
                print("No borrowed book found.")
                return

            borrow_id, borrow_date = result
            fine = self.calculate_fine(borrow_date, today_str)

            cursor.execute("""
                UPDATE borrowed_books
                SET return_date = ?, fine = ?, is_paid = 0
                WHERE id = ?
            """, (today_str, fine, borrow_id))

            cursor.execute("""
                UPDATE books SET quantity = quantity + 1 WHERE id = ?
            """, (book_id,))

            conn.commit()
            print(f"Book returned. Fine: Rs.{fine}")

    def calculate_fine(self, issue_date, return_date=None, allowed_days=15, daily_fine=5):
        issue_date = datetime.strptime(issue_date, "%Y-%m-%d")
        today = datetime.today() if return_date is None else datetime.strptime(return_date, "%Y-%m-%d")
        days_passed = (today - issue_date).days
        overdue_days = max(0, days_passed - allowed_days)
        return overdue_days * daily_fine

    # View fines for a student
    def view_student_fines(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT borrowed_books.book_id, borrowed_books.fine, borrowed_books.is_paid
                FROM borrowed_books
                WHERE borrowed_books.user_id = ?
            """, (user_id,))
            return cursor.fetchall()

    # Mark fine as paid
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
                choice = int(input("Enter number to mark as paid (0 to cancel): "))
                if choice == 0:
                    print("Cancelled.")
                    return
                selected_id = rows[choice - 1][0]
                cursor.execute("UPDATE borrowed_books SET is_paid = 1 WHERE id = ?", (selected_id,))
                conn.commit()
                print("Fine marked as paid.")
            except (IndexError, ValueError):
                print("Invalid choice.")

    def get_total_fine_for_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT borrow_date, return_date FROM borrowed_books
                WHERE user_id = ? AND (return_date IS NULL OR fine IS NOT NULL)
            """, (user_id,))
            records = cursor.fetchall()

            total_fine = 0
            for borrow_date, return_date in records:
                fine = self.calculate_fine(borrow_date, return_date)
                total_fine += fine

            return total_fine

    from datetime import datetime, timedelta

    def view_borrowed_books(self, user_id):
         with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT books.id, books.title, borrowed_books.borrow_date
                FROM borrowed_books
                JOIN books ON books.id = borrowed_books.book_id
                WHERE borrowed_books.user_id = ? AND borrowed_books.return_date IS NULL
            """, (user_id,))
            results = cursor.fetchall()

            updated = []
            for book_id, title, borrow_date in results:
                borrow_dt = datetime.strptime(borrow_date, "%Y-%m-%d")
                due_date = borrow_dt + timedelta(days=14)  # 14 days loan period
                updated.append((book_id, title, due_date.strftime("%Y-%m-%d")))

            return updated


    def renew_book(self):
        username = input("Enter student username to renew book for: ").strip()
        user_id = self.get_user_id_by_username(username)
        if user_id is None:
            print("User not found.")
            return

        book_id = input("Enter book ID to renew: ").strip()
        if not book_id.isdigit():
            print("Invalid book ID.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if the book is currently borrowed by this user
            cursor.execute("""
                SELECT id FROM borrowed_books
                WHERE book_id = ? AND user_id = ? AND return_date IS NULL
            """, (book_id, user_id))
            record = cursor.fetchone()

            if not record:
                print("This user has not borrowed this book or has already returned it.")
                return

            borrowed_id = record[0]

            # Update borrow_date to today's date (renewing)
            new_borrow_date = datetime.today().strftime("%Y-%m-%d")
            cursor.execute("""
                UPDATE borrowed_books
                SET borrow_date = ?
                WHERE id = ?
            """, (new_borrow_date, borrowed_id))

            conn.commit()
            print(f"Book ID {book_id} renewed for {username}. New borrow date: {new_borrow_date}")

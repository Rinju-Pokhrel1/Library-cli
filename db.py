import sqlite3
import bcrypt
from getpass import getpass
from datetime import datetime, timedelta
import json

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
#info
    def get_info(self):
        print("Library Management System")
#get all users
    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email FROM users")
            return cursor.fetchall()
#userid by username
    def get_user_id_by_username(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    # add book
    def add_book(self, title, author, year):
        try:
            year = int(year)
        except ValueError:
            print("Year must be a valid number.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                (title, author, year)
            )
            conn.commit()
            print("Book added.")
#update book
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
#delete book
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
#view book
    def view_all_books(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year FROM books")
            books = cursor.fetchall()

            if not books:
                print("No books found.")
                return

            print("\nAll Books in Library:")
            for book in books:
                print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Year: {book[3]}")

    # issue book
    def issue_book(self, book_id, borrower_username, issuer_username):
        if not str(book_id).isdigit():
            print("Invalid book ID.")
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
            if not cursor.fetchone():
                print("Invalid book ID.")
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
                "SELECT id FROM borrowed_books WHERE book_id = ? AND return_date IS NULL",
                (book_id,)
            )
            if cursor.fetchone():
                print("Book is currently borrowed and not yet returned.")
                return

            borrow_date = datetime.today().strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO borrowed_books (book_id, user_id, borrow_date, issued_by_id) VALUES (?, ?, ?, ?)",
                (book_id, borrower_id, borrow_date, issuer_id)
            )
            conn.commit()
            print(f"Book ID {book_id} issued to {borrower_username} by {issuer_username}.")
#view borrowed books
    def view_borrowed_books(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT borrowed_books.id, books.title, borrowed_books.borrow_date, borrowed_books.return_date
                FROM borrowed_books
                JOIN books ON borrowed_books.book_id = books.id
                WHERE borrowed_books.user_id = ? AND borrowed_books.return_date IS NULL
            """, (user_id,))
            rows = cursor.fetchall()

            if not rows:
                print("No borrowed books found.")
                return

            print("\nBorrowed Books:")
            print(f"{'ID':<5} {'Title':<30} {'Borrow Date':<12} {'Return Date':<12}")
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<30} {row[2]:<12} {'Not returned':<12}")

    

      # Renew borrowed book
def renew_book(self):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT borrowed_books.id, users.username, books.title,
                   borrowed_books.borrow_date, borrowed_books.return_date
            FROM borrowed_books
            JOIN users ON borrowed_books.user_id = users.id
            JOIN books ON borrowed_books.book_id = books.id
            WHERE borrowed_books.return_date IS NULL
            ORDER BY borrowed_books.return_date ASC
        ''')
        borrowed = cursor.fetchall()

        if not borrowed:
            print("\nNo borrowed books to renew.\n")
            return

        print("\nBorrowed Books:")
        print("{0:5} {1:15} {2:30} {3:12} {4:12}".format("ID", "User", "Book Title", "Borrow Date", "Return Date"))
        for book in borrowed:
            borrow_date = book[3] if book[3] else "Unknown"
            return_date = book[4] if book[4] else "Not returned"
            print("{0:5} {1:15} {2:30} {3:12} {4:12}".format(book[0], book[1], book[2], borrow_date, return_date))

        while True:
            try:
                borrow_id = int(input("\nEnter the borrowed book ID to renew (0 to cancel): "))
                if borrow_id == 0:
                    print("Renewal canceled.")
                    return
                if borrow_id not in [b[0] for b in borrowed]:
                    print("Invalid ID. Please try again.")
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
            old_date = datetime.strptime(result[0], "%Y-%m-%d") if result[0] else datetime.today()
            new_date = old_date + timedelta(days=15)

            print(f"\nCurrent return date: {old_date.date()}")
            confirm = input(f"Do you want to extend the return date to {new_date.date()}? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Renewal cancelled.")
                return

            cursor.execute('UPDATE borrowed_books SET return_date = ? WHERE id = ?', (new_date.strftime("%Y-%m-%d"), borrow_id))
            conn.commit()
            print(f"Renewal successful! New return date is {new_date.date()}.\n")
        except Exception as e:
            print("An error occurred during renewal:", e)

   
     # Return borrowed book and calculate fine
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
            conn.commit()
            print(f"Book returned. Fine: Rs.{fine}")

      # Calculate fine 
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
                print(f"{title:<12} {borrow_date:<12} {return_date or 'Not returned':<15} Rs.{fine:<5} {status}")

            print(f"Total Fine: Rs.{total_fine}")
            print(f"Total Paid: Rs.{total_paid}")
            print(f"Unpaid: Rs.{total_fine - total_paid}")

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
            except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in credential.json: {e}")
                    return
if __name__ == "__main__":
    system = LibrarySystem()
    system.create_tables()

    
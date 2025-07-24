import sqlite3
import bcrypt
from getpass import getpass

from datetime import datetime, timedelta

def get_connection():
    return sqlite3.connect("mydatabase.db")
#signup function
def signup_user(username, password, dob, email, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password, dob, email, role) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, dob, email, role)
        )
        conn.commit()
        print("Signup successful!")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()
#login function
def login_system():
    print("\nLogin to the system")
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            stored_hash, role = row
            if bcrypt.checkpw(password.encode(), stored_hash):
                print(f"\nLogin successful! Welcome, {username}.\n")
                return username, role
        print("\nInvalid username or password.\n")
        return None
    finally:
        conn.close()
#info part 
def get_info():
    print("Library Management System\nBuilt with Python and SQLite")
# function to get all users from the database
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
#add book function
def add_book():
    conn = get_connection()
    cursor = conn.cursor()
    title = input("Book title: ")
    author = input("Author: ")
    year = input("Publication year: ")
    cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
    conn.commit()
    conn.close()
    print("Book added.")
#update  book function
def update_book():
    conn = get_connection()
    cursor = conn.cursor()
    book_id = input("Enter book ID to update: ")
    title = input("New title: ")
    cursor.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
    conn.commit()
    conn.close()
    print("Book updated.")
#delete book
def delete_book():
    conn = get_connection()
    cursor = conn.cursor()
    book_id = input("Enter book ID to delete: ")
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    print("Book deleted.")
#view borrowed books
def view_borrowed_books(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM borrowed_books WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
# Function to get user ID by username
def get_user_id_by_username(username):   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def renew_book():
    conn = get_connection()
    cursor = conn.cursor()

    # details of borrowed books;  #to display the book id,username ,title,borrow date and return date we used join operator
    cursor.execute('''
        SELECT borrowed_books.id, users.username, books.title, borrowed_books.borrow_date, borrowed_books.return_date
        FROM borrowed_books
        JOIN users ON borrowed_books.user_id = users.id
        JOIN books ON borrowed_books.book_id = books.id  
        ORDER BY borrowed_books.return_date ASC
                   
                
    ''')
    borrowed = cursor.fetchall()
#check if there are any borrowed books or not
    if not borrowed:
        print("\nNo borrowed books.\n")
        conn.close()
        return

    # Display borrowed books
    print("\n Borrowed Books:\n")
    print(f"{'ID'} {'User'} {'Book Title'} {'Borrow Date'} {'Return Date'}")
  #how many books are borrowed
    for book in borrowed:
        print(f"{book[0]} {book[1]} {book[2]} {book[3]} {book[4]}")

    while True:
        try:
            borrow_id = int(input("\nEnter the borrowed book ID to renew : "))
            if borrow_id == 0:
                print("Renewal canceled.")
                conn.close()
                return
            # Check if borrow_id exists in list
            if borrow_id not in [b[0] for b in borrowed]:
                print("Invalid Id")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric ID.")

    # Fetch the current return date
    cursor.execute('SELECT return_date FROM borrowed_books WHERE id = ?', (borrow_id,))
    result = cursor.fetchone()

    from datetime import datetime, timedelta
    try:
        old_date = datetime.strptime(result[0], "%Y-%m-%d")
        new_date = old_date + timedelta(days=15)  # Extend return date by 15 days

        print(f"\nCurrent return date: {old_date.date()}")
        confirm = input(f"you really want to extend the date {new_date.date()}? ").strip().lower()
        if confirm != '1':
            print("Renewal cancelled.")
            conn.close()
            return

        # Update return date in DB
        cursor.execute('UPDATE borrowed_books SET return_date = ? WHERE id = ?', (new_date.strftime("%Y-%m-%d"), borrow_id))
        conn.commit()
        print(f"Renewal successful! New return date is {new_date.date()}.\n")

    except Exception as e:
        print("An error occurred ", e)

    finally:
        conn.close()
        
        
def return_book(book_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    today_str = datetime.today().strftime()

    # borrow record
    cursor.execute("""
        SELECT id, borrow_date FROM borrowed_books
        WHERE book_id = ? AND user_id = ? AND return_date IS NULL
    """, (book_id, user_id))
    result = cursor.fetchone()

    if not result:
        print("No borrowed book ")
        conn.close()
        return

    borrow_id, borrow_date = result
    fine = calculate_fine(borrow_date, today_str)

    cursor.execute("""
        UPDATE borrowed_books 
        SET return_date = ?, fine = ?, is_paid = 0
        WHERE id = ?
    """, (today_str, fine, borrow_id))
    conn.commit()
    conn.close()

    print(f" Book returned. Fine: Rs.{fine}")

def view_student_fines(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT books.title, borrowed_books.borrow_date, borrowed_books.return_date,
               borrowed_books.fine, borrowed_books.is_paid
        FROM borrowed_books
        JOIN books ON borrowed_books.book_id = books.id
        WHERE borrowed_books.user_id = ?
    """, (user_id,))

    records = cursor.fetchall()
    conn.close()

    total_fine = 0
    total_paid = 0

    print("Title Issued  Returned  Fine Paid")

    for title, borrow_date, return_date, fine, is_paid in records:
        status = "Yes" if is_paid else "No"
        total_fine += fine
        if is_paid:
            total_paid += fine
        print(f"title borrow_date return_date fine  status")
 
    print(f"Total Fine: {total_fine}")
    print(f"Total Paid: {total_paid}")
    print(f"Unpaid: {total_fine - total_paid}")
#if fine is paid
def mark_fine_as_paid(user_id):
    conn = get_connection()
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
        conn.close()
        return

    print("\nUnpaid Fines:")
    for idx, (borrow_id, title, fine) in enumerate(rows, start=1):
        print(f"{idx}. {title} - Fine: Rs.{fine}")

    try:
        choice = int(input("Enter number to mark as paid : "))
        if choice == 0:
            print("Cancelled.")
            conn.close()
            return
        selected_id = rows[choice - 1][0]

        cursor.execute("UPDATE borrowed_books SET is_paid = 1 WHERE id = ?", (selected_id,))
        conn.commit()
        print("Fine marked as paid.")
    except (IndexError, ValueError):
        print("Invalid choice.")
    finally:
        conn.close()

        #fine cal.
def calculate_fine(issue_date, return_date=None, allowed_days=15, daily_fine=5):
    issue_date = datetime.strptime(issue_date)
    today = datetime.today() if return_date is None else datetime.strptime(return_date)
    days_passed = (today - issue_date).days
    overdue_days = max(0, days_passed - allowed_days)
    return overdue_days * daily_fine

from getpass import getpass
from db import (
    signup_user, login_system, get_info, get_all_users,
    add_book, update_book, delete_book, view_borrowed_books,
    get_user_id_by_username, renew_book, view_student_fines,
    mark_fine_as_paid, return_book
)
from migration import create_tables

def menu():
    while True:
        print("\nLibrary Management System")
        print("1. Login")
        print("2. Get Info")
        print("3. Sign Up")
        print("4. Exit")

        choice = input("Choose an option: ")
        
        if choice == "1":
            result = login_system()
            if result:
                username, role = result
                if role == "admin":
                    admin_menu()
                else:
                    user_menu(username)
            else:
                print("Login failed.")

        elif choice == "2":
            get_info()

        elif choice == "3":
            print("\nSign Up")
            username = input("Choose username: ")
            password = getpass("Choose password: ")
            dob = input("Enter DOB : ")
            email = input("Enter email: ")
            role = input("Enter role (admin/student): ").strip().lower()
            if role not in ("admin", "student"):
                print("Invalid role.")
                continue
            signup_user(username, password, dob, email, role)

        elif choice == "4":
            print("Exit")
            break
        else:
            print("Invalid choice!")

def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. Add Book")
        print("2. Update Book")
        print("3. Delete Book")
        print("4. Show All Users")
        print("5. Renew a Student's Book")
        print("6. Mark Student Fine as Paid")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            users = get_all_users()
            for user in users:
                print(f"Username: {user[0]}, Email: {user[1]}")
        elif choice == "5":  
            renew_book()
        elif choice == "6":
            student_username = input("Enter student username to mark fine paid: ")
            student_id = get_user_id_by_username(student_username)
            if student_id:
                mark_fine_as_paid(student_id)
            else:
                print("Student username not found.")
        elif choice == "7":
            break
        else:
            print("Invalid choice.")

def user_menu(username):
    user_id = get_user_id_by_username(username)
    while True:
        print("\nUser Menu:")
        print("1. View My Borrowed Books")
        print("2. View My Fines")
        print("3. Renew Book")
        print("4. Return Book")
        print("5. Logout")

        choice = input("Choose option: ")
        if choice == "1":
            if user_id:
                view_borrowed_books(user_id)
        elif choice == "2":
            if user_id:
                view_student_fines(user_id)
        elif choice == "3":
            renew_book()
        elif choice == "4":
            book_id = input("Enter Book ID to return: ")
            return_book(book_id, user_id)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    create_tables()
    menu()

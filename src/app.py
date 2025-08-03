import bcrypt
from getpass import getpass
from migration import LibrarySystem as MigrationSystem
from db import LibrarySystem
from utility import validate_dob, validate_username
from mail import send_email
from tabulate import tabulate  # Added for table formatting


class LibraryApp:
    def __init__(self):
        migration = MigrationSystem()
        migration.create_tables()

        self.system = LibrarySystem()
        self.current_role = None

    def menu(self):
        while True:
            print("\nLibrary Management System")
            print("1. Login")
            print("2. Get Info")
            print("3. Sign Up")
            print("4. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                username, role = self.system.login_system()
                if username and role:
                    self.current_role = role
                    if role == "admin":
                        self.admin_menu(username)
                    elif role == "student":
                        self.user_menu(username)
                else:
                    print("Login failed.")

            elif choice == "2":
                self.system.get_info()

            elif choice == "3":
                print("\nSign Up")
                username = input("Choose username: ").strip()
                if not validate_username(username):
                    print("Username must be at least 3 characters long.")
                    continue
                if self.system.get_user_id_by_username(username):
                    print("Username already exists.")
                    continue

                password = getpass("Choose password: ")

                dob = input("Enter DOB (YYYY-MM-DD): ").strip()
                if not validate_dob(dob):
                    print("Invalid DOB format! Must be YYYY-MM-DD.")
                    continue

                email = input("Enter email: ").strip()

                # default role: student
                role = "student"
                creator_role = "student"
                self.system.signup_user(username, password, dob, email, role, creator_role)

            elif choice == "4":
                print("Exiting the system.")
                break

            else:
                print("Invalid choice! Please try again.")

    def admin_menu(self, admin_username):
        while True:
            print("\nAdmin Menu")
            print("1. Add Book")
            print("2. Update Book")
            print("3. Delete Book")
            print("4. Show All Users")
            print("5. Renew a Student's Book")
            print("6. Mark Student Fine as Paid")
            print("7. View All Books(with stock)")
            print("8. Issue Book to Student")
            print("9. Create User/Admin Account")
            print("10. View Student Fines")
            print("11. Send Email to Student")
            print("12. Logout")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                title = input("Enter book title: ").strip()
                if not title:
                    print("Book title cannot be empty.")
                    continue
                author = input("Enter book author: ").strip()
                if not author:
                    print("Book author cannot be empty.")
                    continue
                year = input("Enter publication year: ").strip()
                self.system.add_book(title, author, year)

            elif choice == "2":
                self.system.update_book()

            elif choice == "3":
                self.system.delete_book()

            elif choice == "4":
                users = self.system.get_all_users()
                if users:
                    table = tabulate(users, headers=["Username", "Email"], tablefmt="pretty")   #table
                    print("\nAll Users:")
                    print(table)
                else:
                    print("No users found.")

            elif choice == "5":
                self.system.renew_book()

            elif choice == "6":
                username = input("Enter student username to mark fine as paid: ").strip()
                user_id = self.system.get_user_id_by_username(username)
                if user_id:
                    self.system.mark_fine_as_paid(user_id)
                else:
                    print("Student not found.")

            elif choice == "7":
                books = self.system.view_all_books()
                if books:
                    table = tabulate(
                        books,
                        headers=["Book ID", "Title", "Author", "Year", "Stock"],
                        tablefmt="pretty"
                    )
                    print("\nAll Books:")
                    print(table)
                else:
                    print("No books available.")

            elif choice == "8":
                book_id = input("Enter book ID to issue: ").strip()
                borrower_username = input("Enter borrower username: ").strip()
                self.system.issue_book(book_id, borrower_username, admin_username)

            elif choice == "9":
                print("\nCreate new user/admin account")
                username = input("Choose username: ").strip()

                if not validate_username(username):
                    print("Username must be at least 3 characters long.")
                    continue

                if self.system.get_user_id_by_username(username):
                    print("This username already exists. Please choose another.")
                    continue
                password = getpass("Choose password: ")

                dob = input("Enter DOB (YYYY-MM-DD): ").strip()
                if not validate_dob(dob):
                    print("Invalid DOB format! Must be YYYY-MM-DD.")
                    continue

                email = input("Enter email: ").strip()
                role = input("Enter role (admin/student): ").strip().lower()
                if role not in ("admin", "student"):
                    print("Invalid role.")
                    continue

                creator_role = "admin"
                self.system.signup_user(username, password, dob, email, role, creator_role)

            elif choice == "10":
                student_username = input("Enter student username to view fines: ").strip()
                student_id = self.system.get_user_id_by_username(student_username)
                if student_id:
                    fines = self.system.view_student_fines(student_id)
                    if fines:
                        table = tabulate(
                            fines,
                            headers=["Book ID", "Amount", "Status"],
                            tablefmt="pretty"
                        )
                        print("\nFines for student:")
                        print(table)
                    else:
                        print("No fines for this student.")
                else:
                    print("Student not found.")

            elif choice == "11":
                receiver = input("Enter recipient email: ").strip()
                subject = input("Enter email subject: ").strip()
                body = input("Enter email body: ").strip()
                send_email(receiver, subject, body)

            elif choice == "12":
                print("Logging out.")
                self.current_role = None
                break

            else:
                print("Invalid choice. Try again.")

    def user_menu(self, username):
        user_id = self.system.get_user_id_by_username(username)
        if user_id is None:
            print("User ID not found. Please relogin.")
            return

        while True:
            print("\nStudent Menu")
            print("1. View Borrowed Books")
            print("2. Return Book")
            print("3. View Fine")
            print("4. Logout")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                borrowed_books = self.system.view_borrowed_books(user_id)
                if borrowed_books:
                    table = tabulate(
                        borrowed_books,
                        headers=["Book ID", "Title", "Due Date"],
                        tablefmt="pretty"
                    )
                    print("\nYour Borrowed Books:")
                    print(table)
                else:
                    print("You have not borrowed any books.")

            elif choice == "2":
                book_id = input("Enter book ID to return: ").strip()
                self.system.return_book(book_id, user_id)

            elif choice == "3":
                fine = self.system.get_total_fine_for_user(user_id)
                print(f"Your total fine is: Rs. {fine}")

            elif choice == "4":
                print("Logging out.")
                self.current_role = None
                break

            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    app = LibraryApp()
    app.menu()

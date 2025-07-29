from getpass import getpass
from migration import LibrarySystem as MigrationSystem
from db import LibrarySystem

class LibraryApp:
    def __init__(self):
        migration = MigrationSystem()
        migration.create_tables()

        self.system = LibrarySystem()
        self.current_role = None  # Track current logged-in user role

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
                password = getpass("Choose password: ")
                dob = input("Enter DOB (YYYY-MM-DD): ").strip()
                email = input("Enter email: ").strip()
                role = input("Enter role (admin/student): ").strip().lower()
                if role not in ("admin", "student"):
                    print("Invalid role.")
                    continue
                creator_role = "admin" if self.current_role == "admin" else "student"
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
            print("7. View All Books")
            print("8. Issue Book to Student")
            print("9. Logout")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                title = input("Enter book title: ").strip()
                author = input("Enter book author: ").strip()
                year = input("Enter publication year: ").strip()
                self.system.add_book(title, author, year)

            elif choice == "2":
                self.system.update_book()

            elif choice == "3":
                self.system.delete_book()

            elif choice == "4":
                users = self.system.get_all_users()
                print("\nAll Users:")
                for user in users:
                    print(f"Username: {user[0]} | Email: {user[1]}")

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
                self.system.view_all_books()

            elif choice == "8":
                book_id = input("Enter book ID to issue: ").strip()
                borrower_username = input("Enter borrower username: ").strip()
                self.system.issue_book(book_id, borrower_username, admin_username)

            elif choice == "9":
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
                self.system.view_borrowed_books(user_id)

            elif choice == "2":
                book_id = input("Enter book ID to return: ").strip()
                self.system.return_book(book_id, user_id)

            elif choice == "3":
                self.system.view_student_fines(user_id)

            elif choice == "4":
                print("Logging out.")
                self.current_role = None
                break

            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    app = LibraryApp()
    app.menu()

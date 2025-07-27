from getpass import getpass
from db import LibrarySystem
from migration import LibrarySystem as MigrationSystem 
class LibraryApp:
    def __init__(self):
        # Initialize DB and tables
        migration = MigrationSystem()
        migration.create_tables()

        
        self.system = LibrarySystem()

    def menu(self):
        while True:
            print("\nLibrary Management System")
            print("1. Login")
            print("2. Get Info")
            print("3. Sign Up")
            print("4. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                result = self.system.login_system()
                if result:
                    username, role = result
                    if role == "admin":
                        self.admin_menu()
                    else:
                        self.user_menu(username)
                else:
                    print("Login failed. ")

            elif choice == "2":
                self.system.get_info()

            elif choice == "3":
                print("\nSign Up")
                username = input("Choose username: ")
                password = getpass("Choose password: ")
                dob = input("Enter DOB (YYYY-MM-DD): ")
                email = input("Enter email: ")
                role = input("Enter role (admin/student): ").strip().lower()
                if role not in ("admin", "student"):
                    print("Invalid role. Try again.")
                    continue
                self.system.signup_user(username, password, dob, email, role)
                print("Signup successful! You can now log in.")

            elif choice == "4":
                print("Exiting the system. ")
                break

            else:
                print("Invalid choice! Please try again.")

    def admin_menu(self):
        while True:
            print("\nAdmin Menu ")
            print("1. Add Book")
            print("2. Update Book")
            print("3. Delete Book")
            print("4. Show All Users")
            print("5. Renew a Student's Book")
            print("6. Mark Student Fine as Paid")
            print("7. Logout")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.system.add_book()

            elif choice == "2":
                self.system.update_book()

            elif choice == "3":
                self.system.delete_book()

            elif choice == "4":
                users = self.system.get_all_users()
                if users:
                    print("\nRegistered Users:")
                    for user in users:
                        print(f"Username: {user[0]}, Email: {user[1]}")
                else:
                    print("No users found.")

            elif choice == "5":
                self.system.renew_book()

            elif choice == "6":
                student_username = input("Enter student username to mark fine paid: ")
                student_id = self.system.get_user_id_by_username(student_username)
                if student_id:
                    self.system.mark_fine_as_paid(student_id)
                else:
                    print("Student username not found.")

            elif choice == "7":
                print("Logging out of admin menu.")
                break

            else:
                print("Invalid choice. Try again.")

    def user_menu(self, username):
        user_id = self.system.get_user_id_by_username(username)
        while True:
            print("\n User Menu ")
            print("1. View My Borrowed Books")
            print("2. View My Fines")
            print("3. Renew Book")
            print("4. Return Book")
            print("5. Logout")

            choice = input("Choose option: ").strip()

            if choice == "1":
                if user_id:
                    self.system.view_borrowed_books(user_id)

            elif choice == "2":
                if user_id:
                    self.system.view_student_fines(user_id)

            elif choice == "3":
                self.system.renew_book()

            elif choice == "4":
                book_id = input("Enter Book ID to return: ")
                if book_id.isdigit():
                    self.system.return_book(book_id, user_id)
                else:
                    print("Invalid Book ID.")

            elif choice == "5":
                print("Logging out.")
                break

            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    app = LibraryApp()
    app.menu()

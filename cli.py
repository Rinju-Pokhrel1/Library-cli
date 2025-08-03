

from getpass import getpass 
from db import LibrarySystem
def menu():
  
     system = LibrarySystem() 
     while True:
        print("\n Library Management System")
        print("1. Login to the portal")
        print("2. Get info")
        print("3. Login to the system")
        print("4. Sign up")
        print("5. Exit")

        choice = input("Choose an option: ")

        match choice:
             case '1':
                print("\nLogin to the portal")
                username, role = system.login_system()  #error 1, 2 soln
                if username:
                    print("Welcome! You are logged in.")
                else:
                    print("Login failed. Please try again.")
                    input("Press any key to return to main menu")


             case '2':
                print("\nGet info")
                system.get_info()
             case '3':
                print("\nLogin to the system")
                system.login_system()
             case '4':
                print("\nSign up")
                username, password, dob, email = signup()

                # Ask for role
                role = input("Enter role (admin/student): ").strip().lower()

                
                creator_role = "admin"

                system.signup_user(username, password, dob, email, role, creator_role)
             case '5':
                print("\nExit")
                break

if __name__ == "__main__":
    menu()
 
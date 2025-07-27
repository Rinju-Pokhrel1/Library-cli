from db import signup_user,  get_info, login_system
from welcome import signup  
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
                username = input("Enter username: ")
                password = getpass("Enter password: ")
                login_system()
                if login_system(username,password):
                    print("welcome you are logged in!")
                else:
                    print("Login failed. Please try again.")
                    record=input("press any key to return main menu")
                    if record:
                        menu()
            case '2':
                print("\nGet info")
                get_info()
            case '3':
                print("\nLogin to the system")
                login_system()
            case '4':
                print("\nSign up")
                username, password, dob, email = signup() 
                signup_user(username, password, dob, email) 
            case '5':
                print("\nExit")
                break
            case _:
                print("\nInvalid choice. Try again.")

if __name__ == "__main__":
    menu()

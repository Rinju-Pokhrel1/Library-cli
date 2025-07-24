from getpass import getpass
def display_screen():
    print("\n welcome to the library management system\n ")

    print("1.Login to the portal\n 2.Get info \n 3.login to the system \n 4.sign up\n 5.exit\n")

def get_info():
    print("\n simple library system where you can:")
    print(" Manage books")
    print("Return books")
    print("Admin/member login")
    print(" borrowed books")

def login():
    print("\nlogin to the system\n")
    username = input("Enter your name:")
    password=getpass("password:")
    print(f"Username: {username}, Password: {password}") 

def signup():
    print("\nSign up to the system\n")
    username = input("Choose username: ")
    dob=input("Enter your date of birth: ")
    email=input("Enter your email:")
    contact_no=input("phone number:")
    password = getpass("Choose password: ")
    
    print(f"Registered user {username} with contact {contact_no}")
    
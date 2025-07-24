# Library Management System (CLI)

A command-line Library Management System built with Python and raw SQL. This project is designed for learning Python and database concepts, supporting multiple user roles (Admin and Students) with fine management and detailed tracking.

---

## Features

### For Admin
- Add, update, delete, and list books
- Register and manage student accounts
- Issue and return books for any student
- View all issued/returned books
- View and manage fines for overdue books
- Search books and students
- View student details, borrowing history, and fines.

### For Students
- View available books
- Search books
- View their own borrowing history
- View and pay their fines

---

## Tech Stack

- **Python 3.x**
- **SQLite** 
- **Raw SQL queries** 
- **CLI interface** 

---


### File/Folder Descriptions

- **src/main.py**: Starts the CLI application and handles user session flow.
- **src/db.py**: Manages database connection, schema creation, and migrations.
- **src/cli.py**: Handles CLI menus, input parsing, and navigation.
- **src/models.py**: Contains SQL queries and functions for CRUD operations.
- **src/auth.py**: Handles login, registration, and user role checks.
- **src/admin.py**: Implements admin features (book management, fines, student management).
- **src/student.py**: Implements student features (view/search books, pay fines).
- **requirements.txt**: Lists required Python packages (e.g., `tabulate`, `bcrypt`).
- **README.md**: Project overview and documentation.

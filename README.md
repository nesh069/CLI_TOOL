# Python Project Management CLI Tool

A command-line interface application for managing users, projects, and tasks with JSON file persistence. Built with Python 3.10+ using object-oriented design principles.

## Features

- **User Management**: Create and list team members
- **Project Management**: Add projects to users with descriptions and due dates
- **Task Management**: Create tasks, assign contributors, mark as complete
- **Data Persistence**: All data saved to local JSON files
- **Search**: Search across users, projects, and tasks
- **Export**: Export data to CSV format
- **Pretty Output**: Colored terminal output using `rich` and table formatting with `tabulate`

## Project Structure

CLI_TOOL/
├── main.py              # CLI entry point with argparse
├── models/              # OOP class definitions
│   ├── init.py
│   ├── person.py        # Base Person class (inheritance)
│   ├── user.py          # User class (extends Person)
│   ├── project.py       # Project class
│   └── task.py          # Task class
├── utils/               # Helper functions and persistence
│   ├── init.py
│   ├── storage.py       # JSON file I/O manager
│   └── formatters.py    # Pretty printing with rich/tabulate
├── tests/               # Unit tests
│   ├── init.py
│   ├── test_models.py   # Model class tests
│   ├── test_cli.py      # CLI command tests
│   └── test_storage.py  # Persistence tests
├── data/                # JSON data files (auto-created)
│   ├── users.json
│   ├── projects.json
│   └── tasks.json
└── requirements.txt     # Python dependencies

---

## Setup

### 1. Clone the repository

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

All commands run through `main.py`:

```bash
python main.py <command> [options]
```

### Users

```bash
# Add a user
python main.py add-user --name "Alex" --email "alex@example.com"

# List all users
python main.py list-users

# Delete a user (--force removes associated projects and tasks)
python main.py delete-user --id 1 --force
```

### Projects

```bash
# Add a project
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a CLI app" --due-date 2025-12-31

# List all projects
python main.py list-projects

# List projects for a specific user
python main.py list-projects --user "Alex"

# Delete a project
python main.py delete-project --id 1
```

### Tasks

```bash
# Add a task
python main.py add-task --project "CLI Tool" --title "Implement add-task command"

# Add a task with assignees
python main.py add-task --project "CLI Tool" --title "Write tests" --assigned Alex Sam

# List all tasks
python main.py list-tasks

# List tasks for a project
python main.py list-tasks --project "CLI Tool"

# List tasks assigned to a user
python main.py list-tasks --user "Alex"

# Mark a task as complete
python main.py complete-task --id 1

# Update a task
python main.py update-task --id 1 --status completed --title "Updated title"

# Delete a task
python main.py delete-task --id 1
```

### Search & Export

```bash
# Search across all entities
python main.py search --query "CLI"

# Export to CSV
python main.py export --entity users
python main.py export --entity projects
python main.py export --entity tasks
```

### Help

```bash
# List all commands
python main.py --help

# Help for a specific command
python main.py add-user --help
```

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Verbose output
pytest -v tests/

# Run a specific test file
pytest tests/test_models.py
pytest tests/test_cli.py
pytest tests/test_storage.py

# Run with coverage
pytest --cov=models --cov=utils --cov=main tests/
```

---

## Design Overview

### Object-Oriented Design

- **Inheritance** — `User` extends the `Person` base class
- **Encapsulation** — Properties with getters/setters and validation
- **Class Methods** — Registry pattern for object retrieval (e.g. `User.get_user_by_id()`)
- **Relationships**
  - One-to-Many: `User` → `Project`
  - One-to-Many: `Project` → `Task`
  - Many-to-Many: `Task` ↔ `User` (via `assigned_to`)

### Data Persistence

- JSON files stored in the `data/` directory (auto-created on first run)
- Saves automatically after every create, update, or delete operation
- Handles missing or malformed files gracefully
- CSV export available for all entity types

---

## Known Limitations

| Area | Detail |
|---|---|
| Data Integrity | `--force` deletes associated data without a confirmation prompt |
| Search | Substring matching only — no fuzzy search |
| Concurrency | File-based storage is not safe for simultaneous access |
| Email Validation | Basic check only (looks for `@`) |
| Date Handling | Due dates stored as strings with no timezone support |

---

## License

MIT License
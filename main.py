#!/usr/bin/env python3
"""Project Management CLI Tool - Main Entry Point.

A command-line interface for managing users, projects, and tasks.
Supports adding, listing, updating, and deleting entities with
JSON file persistence.

Usage:
    python main.py [command] [options]
    
Examples:
    python main.py add-user --name "Alex" --email "alex@example.com"
    python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a CLI"
    python main.py add-task --project "CLI Tool" --title "Implement add-task"
    python main.py list-users
    python main.py list-projects --user "Alex"
    python main.py complete-task --id 1
"""
import argparse
import sys
import os

# Ensure models and utils are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import StorageManager
from utils.formatters import (
    format_table, print_success, print_error, 
    print_warning, print_info, print_header
)


def get_storage() -> StorageManager:
    """Get storage manager instance, loading existing data."""
    storage = StorageManager()
    storage.load_all()
    return storage


def cmd_add_user(args):
    """Handle add-user command."""
    try:
        storage = get_storage()
        user = User(name=args.name, email=args.email or "")
        storage.save_users()
        print_success(f"User '{args.name}' created with ID {user.id}")
    except ValueError as e:
        print_error(str(e))
        return 1
    return 0


def cmd_list_users(args):
    """Handle list-users command."""
    users = User.get_all_users()
    if not users:
        print_info("No users found.")
        return 0
    
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "projects": user.get_project_count()
        })
    
    print_header("Users")
    print(format_table(data))
    return 0


def cmd_add_project(args):
    """Handle add-project command."""
    storage = get_storage()
    
    # Find user by name or ID
    user = None
    if args.user.isdigit():
        user = User.get_user_by_id(int(args.user))
    else:
        for u in User.get_all_users():
            if u.name.lower() == args.user.lower():
                user = u
                break
    
    if not user:
        print_error(f"User '{args.user}' not found. Use list-users to see available users.")
        return 1
    
    try:
        project = Project(
            title=args.title,
            description=args.description or "",
            due_date=args.due_date or "",
            user_id=user.id
        )
        user.add_project(project.id)
        storage.save_all()
        print_success(f"Project '{args.title}' created with ID {project.id} for user '{user.name}'")
    except ValueError as e:
        print_error(str(e))
        return 1
    return 0


def cmd_list_projects(args):
    """Handle list-projects command."""
    storage = get_storage()
    
    if args.user:
        # Filter by user
        user = None
        if args.user.isdigit():
            user = User.get_user_by_id(int(args.user))
        else:
            for u in User.get_all_users():
                if u.name.lower() == args.user.lower():
                    user = u
                    break
        
        if not user:
            print_error(f"User '{args.user}' not found.")
            return 1
        
        projects = Project.get_projects_by_user(user.id)
        print_header(f"Projects for {user.name}")
    else:
        projects = Project.get_all_projects()
        print_header("All Projects")
    
    if not projects:
        print_info("No projects found.")
        return 0
    
    data = []
    for project in projects:
        owner = User.get_user_by_id(project.user_id)
        owner_name = owner.name if owner else "Unknown"
        data.append({
            "id": project.id,
            "title": project.title,
            "description": project.description[:30] + "..." if len(project.description) > 30 else project.description,
            "due_date": project.due_date or "N/A",
            "owner": owner_name,
            "tasks": project.get_task_count(),
            "status": "OVERDUE" if project.is_overdue() else "Active"
        })
    
    print(format_table(data))
    return 0


def cmd_add_task(args):
    """Handle add-task command."""
    storage = get_storage()
    
    # Find project by title or ID
    project = None
    if args.project.isdigit():
        project = Project.get_project_by_id(int(args.project))
    else:
        for p in Project.get_all_projects():
            if p.title.lower() == args.project.lower():
                project = p
                break
    
    if not project:
        print_error(f"Project '{args.project}' not found. Use list-projects to see available projects.")
        return 1
    
    try:
        assigned = []
        if args.assigned:
            for name in args.assigned:
                for u in User.get_all_users():
                    if u.name.lower() == name.lower():
                        assigned.append(u.id)
                        break
        
        task = Task(title=args.title, project_id=project.id, assigned_to=assigned)
        project.add_task(task.id)
        storage.save_all()
        
        assignees = ", ".join(User.get_user_by_id(uid).name for uid in assigned if User.get_user_by_id(uid)) or "Unassigned"
        print_success(f"Task '{args.title}' created with ID {task.id} in project '{project.title}' (Assigned: {assignees})")
    except ValueError as e:
        print_error(str(e))
        return 1
    return 0


def cmd_list_tasks(args):
    """Handle list-tasks command."""
    storage = get_storage()
    
    if args.project:
        project = None
        if args.project.isdigit():
            project = Project.get_project_by_id(int(args.project))
        else:
            for p in Project.get_all_projects():
                if p.title.lower() == args.project.lower():
                    project = p
                    break
        
        if not project:
            print_error(f"Project '{args.project}' not found.")
            return 1
        
        tasks = Task.get_tasks_by_project(project.id)
        print_header(f"Tasks in '{project.title}'")
    elif args.user:
        user = None
        if args.user.isdigit():
            user = User.get_user_by_id(int(args.user))
        else:
            for u in User.get_all_users():
                if u.name.lower() == args.user.lower():
                    user = u
                    break
        
        if not user:
            print_error(f"User '{args.user}' not found.")
            return 1
        
        tasks = Task.get_tasks_by_user(user.id)
        print_header(f"Tasks assigned to '{user.name}'")
    else:
        tasks = Task.get_all_tasks()
        print_header("All Tasks")
    
    if not tasks:
        print_info("No tasks found.")
        return 0
    
    data = []
    for task in tasks:
        project = Project.get_project_by_id(task.project_id)
        project_title = project.title if project else "Unknown"
        assignees = ", ".join(User.get_user_by_id(uid).name for uid in task.assigned_to if User.get_user_by_id(uid)) or "Unassigned"
        
        status_icon = "✓" if task.status == "completed" else "○" if task.status == "pending" else "►"
        data.append({
            "id": task.id,
            "title": task.title,
            "status": f"{status_icon} {task.status}",
            "project": project_title,
            "assigned_to": assignees,
            "created": task.created_at[:10] if task.created_at else "N/A"
        })
    
    print(format_table(data))
    return 0


def cmd_complete_task(args):
    """Handle complete-task command."""
    storage = get_storage()
    
    task = Task.get_task_by_id(args.id)
    if not task:
        print_error(f"Task with ID {args.id} not found.")
        return 1
    
    try:
        task.mark_complete()
        storage.save_tasks()
        print_success(f"Task '{task.title}' (ID: {task.id}) marked as completed")
    except ValueError as e:
        print_error(str(e))
        return 1
    return 0


def cmd_update_task(args):
    """Handle update-task command."""
    storage = get_storage()
    
    task = Task.get_task_by_id(args.id)
    if not task:
        print_error(f"Task with ID {args.id} not found.")
        return 1
    
    try:
        if args.title:
            task.title = args.title
        if args.status:
            task.status = args.status
        if args.assign:
            for name in args.assign:
                found = False
                for u in User.get_all_users():
                    if u.name.lower() == name.lower():
                        task.assign_user(u.id)
                        found = True
                        break
                if not found:
                    print_warning(f"User '{name}' not found, skipping assignment")
        
        storage.save_tasks()
        print_success(f"Task '{task.title}' (ID: {task.id}) updated successfully")
    except ValueError as e:
        print_error(str(e))
        return 1
    return 0


def cmd_delete_user(args):
    """Handle delete-user command."""
    storage = get_storage()
    
    user = User.get_user_by_id(args.id)
    if not user:
        print_error(f"User with ID {args.id} not found.")
        return 1
    
    # Check for associated projects
    projects = Project.get_projects_by_user(user.id)
    if projects and not args.force:
        print_warning(f"User '{user.name}' has {len(projects)} project(s). Use --force to delete anyway.")
        return 1
    
    # Remove user's projects and their tasks
    for project in projects:
        for task_id in project.tasks:
            task = Task.get_task_by_id(task_id)
            if task:
                Task._tasks_registry.pop(task_id, None)
        Project._projects_registry.pop(project.id, None)
    
    User._users_registry.pop(user.id, None)
    storage.save_all()
    print_success(f"User '{user.name}' and associated data deleted")
    return 0


def cmd_delete_project(args):
    """Handle delete-project command."""
    storage = get_storage()
    
    project = Project.get_project_by_id(args.id)
    if not project:
        print_error(f"Project with ID {args.id} not found.")
        return 1
    
    # Remove project from user's list
    user = User.get_user_by_id(project.user_id)
    if user:
        try:
            user.remove_project(project.id)
        except ValueError:
            pass
    
    # Remove associated tasks
    for task_id in project.tasks:
        Task._tasks_registry.pop(task_id, None)
    
    Project._projects_registry.pop(project.id, None)
    storage.save_all()
    print_success(f"Project '{project.title}' and associated tasks deleted")
    return 0


def cmd_delete_task(args):
    """Handle delete-task command."""
    storage = get_storage()
    
    task = Task.get_task_by_id(args.id)
    if not task:
        print_error(f"Task with ID {args.id} not found.")
        return 1
    
    # Remove task from project's list
    project = Project.get_project_by_id(task.project_id)
    if project:
        try:
            project.remove_task(task.id)
        except ValueError:
            pass
    
    Task._tasks_registry.pop(task.id, None)
    storage.save_all()
    print_success(f"Task '{task.title}' deleted")
    return 0


def cmd_search(args):
    """Handle search command."""
    storage = get_storage()
    query = args.query.lower()
    results = []
    
    # Search users
    for user in User.get_all_users():
        if query in user.name.lower() or query in user.email.lower():
            results.append({"type": "User", "id": user.id, "name": user.name, "details": user.email})
    
    # Search projects
    for project in Project.get_all_projects():
        if query in project.title.lower() or query in project.description.lower():
            owner = User.get_user_by_id(project.user_id)
            results.append({
                "type": "Project", "id": project.id, 
                "name": project.title, 
                "details": f"Owner: {owner.name if owner else 'Unknown'}"
            })
    
    # Search tasks
    for task in Task.get_all_tasks():
        if query in task.title.lower():
            project = Project.get_project_by_id(task.project_id)
            results.append({
                "type": "Task", "id": task.id,
                "name": task.title,
                "details": f"Project: {project.title if project else 'Unknown'}, Status: {task.status}"
            })
    
    if not results:
        print_info(f"No results found for '{args.query}'")
        return 0
    
    print_header(f"Search Results for '{args.query}'")
    print(format_table(results))
    return 0


def cmd_export(args):
    """Handle export command."""
    storage = get_storage()
    filename = f"{args.entity}.csv"
    
    if storage.export_to_csv(filename, args.entity):
        print_success(f"{args.entity.title()} exported to data/{filename}")
    else:
        print_error("Export failed")
        return 1
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with subcommands.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="project-mgmt",
        description="Python Project Management CLI Tool - Manage users, projects, and tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add-user --name "Alex" --email "alex@example.com"
  %(prog)s add-project --user "Alex" --title "CLI Tool" --description "Build CLI"
  %(prog)s add-task --project "CLI Tool" --title "Implement feature"
  %(prog)s list-projects --user "Alex"
  %(prog)s complete-task --id 1
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # add-user
    add_user = subparsers.add_parser("add-user", help="Add a new user")
    add_user.add_argument("--name", required=True, help="User's full name")
    add_user.add_argument("--email", default="", help="User's email address")
    add_user.set_defaults(func=cmd_add_user)
    
    # list-users
    list_users = subparsers.add_parser("list-users", help="List all users")
    list_users.set_defaults(func=cmd_list_users)
    
    # add-project
    add_project = subparsers.add_parser("add-project", help="Add a new project to a user")
    add_project.add_argument("--user", required=True, help="User name or ID")
    add_project.add_argument("--title", required=True, help="Project title")
    add_project.add_argument("--description", default="", help="Project description")
    add_project.add_argument("--due-date", default="", help="Due date (YYYY-MM-DD)")
    add_project.set_defaults(func=cmd_add_project)
    
    # list-projects
    list_projects = subparsers.add_parser("list-projects", help="List projects")
    list_projects.add_argument("--user", default="", help="Filter by user name or ID")
    list_projects.set_defaults(func=cmd_list_projects)
    
    # add-task
    add_task = subparsers.add_parser("add-task", help="Add a task to a project")
    add_task.add_argument("--project", required=True, help="Project title or ID")
    add_task.add_argument("--title", required=True, help="Task title")
    add_task.add_argument("--assigned", nargs="+", help="Assign to users by name")
    add_task.set_defaults(func=cmd_add_task)
    
    # list-tasks
    list_tasks = subparsers.add_parser("list-tasks", help="List tasks")
    list_tasks.add_argument("--project", default="", help="Filter by project")
    list_tasks.add_argument("--user", default="", help="Filter by assigned user")
    list_tasks.set_defaults(func=cmd_list_tasks)
    
    # complete-task
    complete_task = subparsers.add_parser("complete-task", help="Mark a task as completed")
    complete_task.add_argument("--id", type=int, required=True, help="Task ID")
    complete_task.set_defaults(func=cmd_complete_task)
    
    # update-task
    update_task = subparsers.add_parser("update-task", help="Update a task")
    update_task.add_argument("--id", type=int, required=True, help="Task ID")
    update_task.add_argument("--title", help="New title")
    update_task.add_argument("--status", choices=["pending", "in_progress", "completed"], help="New status")
    update_task.add_argument("--assign", nargs="+", help="Assign additional users")
    update_task.set_defaults(func=cmd_update_task)
    
    # delete-user
    delete_user = subparsers.add_parser("delete-user", help="Delete a user")
    delete_user.add_argument("--id", type=int, required=True, help="User ID")
    delete_user.add_argument("--force", action="store_true", help="Force delete with associated data")
    delete_user.set_defaults(func=cmd_delete_user)
    
    # delete-project
    delete_project = subparsers.add_parser("delete-project", help="Delete a project")
    delete_project.add_argument("--id", type=int, required=True, help="Project ID")
    delete_project.set_defaults(func=cmd_delete_project)
    
    # delete-task
    delete_task = subparsers.add_parser("delete-task", help="Delete a task")
    delete_task.add_argument("--id", type=int, required=True, help="Task ID")
    delete_task.set_defaults(func=cmd_delete_task)
    
    # search
    search = subparsers.add_parser("search", help="Search across all entities")
    search.add_argument("--query", required=True, help="Search query")
    search.set_defaults(func=cmd_search)
    
    # export
    export = subparsers.add_parser("export", help="Export data to CSV")
    export.add_argument("--entity", required=True, choices=["users", "projects", "tasks"], help="Entity type to export")
    export.set_defaults(func=cmd_export)
    
    return parser


def main():
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        return args.func(args)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
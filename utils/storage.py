"""Data persistence module using JSON file I/O.

Handles saving and loading of users, projects, and tasks to local JSON files.
Includes error handling for missing files and malformed data.
"""
import json
import os
from typing import Dict, Any

from models.user import User
from models.project import Project
from models.task import Task


class StorageManager:
    """Manages persistent storage of application data in JSON format.
    
    Attributes:
        data_dir (str): Directory path for data files.
        users_file (str): Path to users JSON file.
        projects_file (str): Path to projects JSON file.
        tasks_file (str): Path to tasks JSON file.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the storage manager.
        
        Args:
            data_dir: Directory for data files (default: 'data').
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.projects_file = os.path.join(data_dir, "projects.json")
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_all(self) -> bool:
        """Save all current data to JSON files.
        
        Returns:
            True if all saves succeeded, False otherwise.
        """
        try:
            self.save_users()
            self.save_projects()
            self.save_tasks()
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_all(self) -> bool:
        """Load all data from JSON files.
        
        Returns:
            True if all loads succeeded, False otherwise.
        """
        try:
            self.load_users()
            self.load_projects()
            self.load_tasks()
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def save_users(self):
        """Save all users to JSON file."""
        users_data = [user.to_dict() for user in User.get_all_users()]
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2)
    
    def load_users(self):
        """Load users from JSON file with error handling.
        
        Handles missing files and malformed JSON gracefully.
        """
        User.clear_registry()
        try:
            if not os.path.exists(self.users_file):
                return
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Users data must be a list")
            for user_data in data:
                User.from_dict(user_data)
        except json.JSONDecodeError as e:
            print(f"Warning: Malformed users JSON - {e}. Starting with empty users.")
            User.clear_registry()
        except FileNotFoundError:
            pass  # No existing data is okay
        except Exception as e:
            print(f"Warning: Error loading users - {e}. Starting with empty users.")
            User.clear_registry()
    
    def save_projects(self):
        """Save all projects to JSON file."""
        projects_data = [project.to_dict() for project in Project.get_all_projects()]
        with open(self.projects_file, "w", encoding="utf-8") as f:
            json.dump(projects_data, f, indent=2)
    
    def load_projects(self):
        """Load projects from JSON file with error handling."""
        Project.clear_registry()
        try:
            if not os.path.exists(self.projects_file):
                return
            with open(self.projects_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Projects data must be a list")
            for project_data in data:
                Project.from_dict(project_data)
        except json.JSONDecodeError as e:
            print(f"Warning: Malformed projects JSON - {e}. Starting with empty projects.")
            Project.clear_registry()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Error loading projects - {e}. Starting with empty projects.")
            Project.clear_registry()
    
    def save_tasks(self):
        """Save all tasks to JSON file."""
        tasks_data = [task.to_dict() for task in Task.get_all_tasks()]
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, indent=2)
    
    def load_tasks(self):
        """Load tasks from JSON file with error handling."""
        Task.clear_registry()
        try:
            if not os.path.exists(self.tasks_file):
                return
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Tasks data must be a list")
            for task_data in data:
                Task.from_dict(task_data)
        except json.JSONDecodeError as e:
            print(f"Warning: Malformed tasks JSON - {e}. Starting with empty tasks.")
            Task.clear_registry()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Error loading tasks - {e}. Starting with empty tasks.")
            Task.clear_registry()
    
    def export_to_csv(self, filename: str, entity_type: str) -> bool:
        """Export data to CSV format.
        
        Args:
            filename: Output CSV filename.
            entity_type: One of 'users', 'projects', 'tasks'.
            
        Returns:
            True if export succeeded.
        """
        import csv
        try:
            filepath = os.path.join(self.data_dir, filename)
            if entity_type == "users":
                data = [user.to_dict() for user in User.get_all_users()]
            elif entity_type == "projects":
                data = [proj.to_dict() for proj in Project.get_all_projects()]
            elif entity_type == "tasks":
                data = [task.to_dict() for task in Task.get_all_tasks()]
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            if not data:
                print(f"No {entity_type} to export")
                return False
            
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
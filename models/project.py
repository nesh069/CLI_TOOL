"""Project class representing a project with tasks."""
from datetime import datetime
from typing import List, Optional


class Project:
    """Project class representing a development project.
    
    Demonstrates one-to-many relationship (Project -> Tasks).
    
    Attributes:
        _id (int): Unique project identifier.
        _title (str): Project title.
        _description (str): Project description.
        _due_date (str): Project due date (ISO format).
        _tasks (list): List of task IDs in this project.
        _user_id (int): ID of the user who owns this project.
    """
    
    _id_counter = 0
    _projects_registry = {}
    
    def __init__(self, title: str, description: str = "", due_date: str = "", user_id: int = 0):
        """Initialize a Project.
        
        Args:
            title: The project title.
            description: Optional project description.
            due_date: Optional due date (YYYY-MM-DD format).
            user_id: ID of the owning user.
        """
        Project._id_counter += 1
        self._id = Project._id_counter
        self._title = title
        self._description = description
        self._due_date = due_date
        self._tasks = []  # One-to-many: Project has many Tasks
        self._user_id = user_id
        Project._projects_registry[self._id] = self
    
    @property
    def id(self) -> int:
        """Get the project's unique ID."""
        return self._id
    
    @property
    def title(self) -> str:
        """Get the project title."""
        return self._title
    
    @title.setter
    def title(self, value: str):
        """Set the project title with validation.
        
        Args:
            value: The new title (must be non-empty).
            
        Raises:
            ValueError: If title is empty.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Project title must be a non-empty string")
        self._title = value.strip()
    
    @property
    def description(self) -> str:
        """Get the project description."""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """Set the project description.
        
        Args:
            value: The new description.
        """
        self._description = value.strip() if value else ""
    
    @property
    def due_date(self) -> str:
        """Get the project due date."""
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: str):
        """Set the project due date with validation.
        
        Args:
            value: Date string in YYYY-MM-DD format.
            
        Raises:
            ValueError: If date format is invalid.
        """
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Due date must be in YYYY-MM-DD format")
        self._due_date = value
    
    @property
    def tasks(self) -> List[int]:
        """Get list of task IDs in this project."""
        return self._tasks.copy()
    
    @property
    def user_id(self) -> int:
        """Get the owning user's ID."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: int):
        """Set the owning user's ID.
        
        Args:
            value: The user ID integer.
        """
        self._user_id = value
    
    def add_task(self, task_id: int):
        """Add a task ID to this project.
        
        Args:
            task_id: The task ID to add.
            
        Raises:
            ValueError: If task is already in project.
        """
        if task_id in self._tasks:
            raise ValueError(f"Task {task_id} is already in this project")
        self._tasks.append(task_id)
    
    def remove_task(self, task_id: int):
        """Remove a task ID from this project.
        
        Args:
            task_id: The task ID to remove.
            
        Raises:
            ValueError: If task is not found.
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task {task_id} not found in this project")
        self._tasks.remove(task_id)
    
    def get_task_count(self) -> int:
        """Return the number of tasks in this project.
        
        Returns:
            Integer count of tasks.
        """
        return len(self._tasks)
    
    def is_overdue(self) -> bool:
        """Check if the project is past its due date.
        
        Returns:
            True if due date has passed, False otherwise.
        """
        if not self._due_date:
            return False
        try:
            due = datetime.strptime(self._due_date, "%Y-%m-%d")
            return due < datetime.now()
        except ValueError:
            return False
    
    @classmethod
    def get_project_by_id(cls, project_id: int) -> Optional["Project"]:
        """Retrieve a project by ID.
        
        Args:
            project_id: The ID to look up.
            
        Returns:
            The Project instance or None.
        """
        return cls._projects_registry.get(project_id)
    
    @classmethod
    def get_all_projects(cls) -> List["Project"]:
        """Get all registered projects.
        
        Returns:
            List of all Project instances.
        """
        return list(cls._projects_registry.values())
    
    @classmethod
    def get_projects_by_user(cls, user_id: int) -> List["Project"]:
        """Get all projects owned by a specific user.
        
        Args:
            user_id: The user ID to filter by.
            
        Returns:
            List of Project instances for the user.
        """
        return [p for p in cls._projects_registry.values() if p._user_id == user_id]
    
    @classmethod
    def clear_registry(cls):
        """Clear the projects registry (useful for testing)."""
        cls._projects_registry.clear()
        cls._id_counter = 0
    
    def __str__(self) -> str:
        """Return human-readable string."""
        overdue = " [OVERDUE]" if self.is_overdue() else ""
        return f"Project(id={self._id}, title='{self._title}', tasks={len(self._tasks)}){overdue}"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"Project(id={self._id}, title='{self._title}', "
                f"description='{self._description}', due_date='{self._due_date}', "
                f"user_id={self._user_id}, tasks={self._tasks})")
    
    def to_dict(self) -> dict:
        """Convert project to dictionary for JSON serialization."""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "tasks": self._tasks,
            "user_id": self._user_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create a Project instance from a dictionary.
        
        Args:
            data: Dictionary containing project data.
            
        Returns:
            A new Project instance registered in the class registry.
        """
        project = cls.__new__(cls)
        project._id = data["id"]
        project._title = data["title"]
        project._description = data.get("description", "")
        project._due_date = data.get("due_date", "")
        project._tasks = data.get("tasks", [])
        project._user_id = data.get("user_id", 0)
        if data["id"] > cls._id_counter:
            cls._id_counter = data["id"]
        cls._projects_registry[project._id] = project
        return project
"""Task class representing a task within a project."""
from datetime import datetime
from typing import Optional


class Task:
    """Task class representing a unit of work in a project.
    
    Demonstrates many-to-many potential (tasks can have contributors)
    and belongs to a specific project.
    
    Attributes:
        _id (int): Unique task identifier.
        _title (str): Task title.
        _status (str): Current status (pending, in_progress, completed).
        _assigned_to (list): List of user IDs assigned to this task.
        _project_id (int): ID of the parent project.
        _created_at (str): ISO timestamp of creation.
        _completed_at (str): ISO timestamp of completion.
    """
    
    VALID_STATUSES = ["pending", "in_progress", "completed"]
    _id_counter = 0
    _tasks_registry = {}
    
    def __init__(self, title: str, project_id: int = 0, assigned_to: list = None):
        """Initialize a Task.
        
        Args:
            title: The task title.
            project_id: ID of the parent project.
            assigned_to: List of user IDs to assign (many-to-many relationship).
        """
        Task._id_counter += 1
        self._id = Task._id_counter
        self._title = title
        self._status = "pending"
        self._assigned_to = assigned_to if assigned_to is not None else []
        self._project_id = project_id
        self._created_at = datetime.now().isoformat()
        self._completed_at = ""
        Task._tasks_registry[self._id] = self
    
    @property
    def id(self) -> int:
        """Get the task's unique ID."""
        return self._id
    
    @property
    def title(self) -> str:
        """Get the task title."""
        return self._title
    
    @title.setter
    def title(self, value: str):
        """Set the task title with validation.
        
        Args:
            value: The new title (must be non-empty).
            
        Raises:
            ValueError: If title is empty.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task title must be a non-empty string")
        self._title = value.strip()
    
    @property
    def status(self) -> str:
        """Get the current task status."""
        return self._status
    
    @status.setter
    def status(self, value: str):
        """Set task status with validation.
        
        Args:
            value: One of 'pending', 'in_progress', 'completed'.
            
        Raises:
            ValueError: If status is not valid.
        """
        value = value.lower().replace(" ", "_")
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
        self._status = value
        if value == "completed":
            self._completed_at = datetime.now().isoformat()
    
    @property
    def assigned_to(self) -> list:
        """Get list of assigned user IDs."""
        return self._assigned_to.copy()
    
    def assign_user(self, user_id: int):
        """Assign a user to this task (many-to-many relationship).
        
        Args:
            user_id: The user ID to assign.
            
        Raises:
            ValueError: If user is already assigned.
        """
        if user_id in self._assigned_to:
            raise ValueError(f"User {user_id} is already assigned to this task")
        self._assigned_to.append(user_id)
    
    def unassign_user(self, user_id: int):
        """Remove a user assignment from this task.
        
        Args:
            user_id: The user ID to unassign.
            
        Raises:
            ValueError: If user is not assigned.
        """
        if user_id not in self._assigned_to:
            raise ValueError(f"User {user_id} is not assigned to this task")
        self._assigned_to.remove(user_id)
    
    @property
    def project_id(self) -> int:
        """Get the parent project ID."""
        return self._project_id
    
    @project_id.setter
    def project_id(self, value: int):
        """Set the parent project ID."""
        self._project_id = value
    
    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def completed_at(self) -> str:
        """Get completion timestamp."""
        return self._completed_at
    
    def mark_complete(self):
        """Mark this task as completed."""
        self.status = "completed"
    
    def mark_in_progress(self):
        """Mark this task as in progress."""
        self.status = "in_progress"
    
    def is_completed(self) -> bool:
        """Check if task is completed.
        
        Returns:
            True if status is 'completed'.
        """
        return self._status == "completed"
    
    @classmethod
    def get_task_by_id(cls, task_id: int) -> Optional["Task"]:
        """Retrieve a task by ID.
        
        Args:
            task_id: The ID to look up.
            
        Returns:
            The Task instance or None.
        """
        return cls._tasks_registry.get(task_id)
    
    @classmethod
    def get_all_tasks(cls) -> list:
        """Get all registered tasks.
        
        Returns:
            List of all Task instances.
        """
        return list(cls._tasks_registry.values())
    
    @classmethod
    def get_tasks_by_project(cls, project_id: int) -> list:
        """Get all tasks belonging to a specific project.
        
        Args:
            project_id: The project ID to filter by.
            
        Returns:
            List of Task instances for the project.
        """
        return [t for t in cls._tasks_registry.values() if t._project_id == project_id]
    
    @classmethod
    def get_tasks_by_user(cls, user_id: int) -> list:
        """Get all tasks assigned to a specific user.
        
        Args:
            user_id: The user ID to filter by.
            
        Returns:
            List of Task instances assigned to the user.
        """
        return [t for t in cls._tasks_registry.values() if user_id in t._assigned_to]
    
    @classmethod
    def clear_registry(cls):
        """Clear the tasks registry (useful for testing)."""
        cls._tasks_registry.clear()
        cls._id_counter = 0
    
    def __str__(self) -> str:
        """Return human-readable string with status indicator."""
        status_icon = "✓" if self._status == "completed" else "○" if self._status == "pending" else "►"
        return f"Task(id={self._id}, {status_icon} '{self._title}', status={self._status})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"Task(id={self._id}, title='{self._title}', status='{self._status}', "
                f"project_id={self._project_id}, assigned_to={self._assigned_to}, "
                f"created_at='{self._created_at}')")
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self._id,
            "title": self._title,
            "status": self._status,
            "assigned_to": self._assigned_to,
            "project_id": self._project_id,
            "created_at": self._created_at,
            "completed_at": self._completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task instance from a dictionary.
        
        Args:
            data: Dictionary containing task data.
            
        Returns:
            A new Task instance registered in the class registry.
        """
        task = cls.__new__(cls)
        task._id = data["id"]
        task._title = data["title"]
        task._status = data.get("status", "pending")
        task._assigned_to = data.get("assigned_to", [])
        task._project_id = data.get("project_id", 0)
        task._created_at = data.get("created_at", datetime.now().isoformat())
        task._completed_at = data.get("completed_at", "")
        if data["id"] > cls._id_counter:
            cls._id_counter = data["id"]
        cls._tasks_registry[task._id] = task
        return task
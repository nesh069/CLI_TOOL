"""User class extending Person with project management capabilities."""
from typing import List, Optional
from .person import Person


class User(Person):
    """User class representing a team member who owns projects.
    
    Inherits from Person and adds project management functionality.
    Demonstrates one-to-many relationship (User -> Projects).
    
    Attributes:
        _projects (list): List of project IDs owned by this user.
    """
    
    _users_registry = {}  # Class-level registry of all users by ID
    
    def __init__(self, name: str, email: str = ""):
        """Initialize a User with name and optional email.
        
        Args:
            name: The user's full name.
            email: The user's email address.
        """
        super().__init__(name, email)
        self._projects = []  # One-to-many: User has many Projects
        User._users_registry[self._id] = self
    
    @property
    def projects(self) -> List[int]:
        """Get list of project IDs associated with this user.
        
        Returns:
            List of project ID integers.
        """
        return self._projects.copy()
    
    def add_project(self, project_id: int):
        """Add a project ID to this user's project list.
        
        Args:
            project_id: The ID of the project to associate.
            
        Raises:
            ValueError: If project_id is already associated.
        """
        if project_id in self._projects:
            raise ValueError(f"Project {project_id} is already associated with this user")
        self._projects.append(project_id)
    
    def remove_project(self, project_id: int):
        """Remove a project ID from this user's project list.
        
        Args:
            project_id: The ID of the project to disassociate.
            
        Raises:
            ValueError: If project_id is not found.
        """
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found for this user")
        self._projects.remove(project_id)
    
    def get_project_count(self) -> int:
        """Return the number of projects owned by this user.
        
        Returns:
            Integer count of projects.
        """
        return len(self._projects)
    
    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional["User"]:
        """Retrieve a user from the registry by ID.
        
        Args:
            user_id: The ID of the user to find.
            
        Returns:
            The User instance or None if not found.
        """
        return cls._users_registry.get(user_id)
    
    @classmethod
    def get_all_users(cls) -> List["User"]:
        """Get all registered users.
        
        Returns:
            List of all User instances.
        """
        return list(cls._users_registry.values())
    
    @classmethod
    def clear_registry(cls):
        """Clear the users registry (useful for testing)."""
        cls._users_registry.clear()
        cls._id_counter = 0
    
    def __str__(self) -> str:
        """Return human-readable string with project count."""
        return (f"User(id={self._id}, name='{self._name}', "
                f"projects={len(self._projects)})")
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"User(id={self._id}, name='{self._name}', "
                f"email='{self._email}', projects={self._projects})")
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation including inherited and own attributes.
        """
        data = super().to_dict()
        data["projects"] = self._projects
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User instance from a dictionary.
        
        Args:
            data: Dictionary containing user data.
            
        Returns:
            A new User instance registered in the class registry.
        """
        user = cls.__new__(cls)
        Person.__init__(user, data["name"], data.get("email", ""))
        user._id = data["id"]
        user._projects = data.get("projects", [])
        if data["id"] > cls._id_counter:
            cls._id_counter = data["id"]
        cls._users_registry[user._id] = user
        return user
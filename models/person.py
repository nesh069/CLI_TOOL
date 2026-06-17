"""Base Person class demonstrating inheritance."""


class Person:
    """Base class representing a person in the system.
    
    Attributes:
        _name (str): The person's name (protected via property).
        _email (str): The person's email (protected via property).
    """
    
    _id_counter = 0  # Class attribute for auto-incrementing IDs
    
    def __init__(self, name: str, email: str = ""):
        """Initialize a Person with name and optional email.
        
        Args:
            name: The person's full name.
            email: The person's email address.
        """
        Person._id_counter += 1
        self._id = Person._id_counter
        self._name = name
        self._email = email
    
    @property
    def id(self) -> int:
        """Get the person's unique ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get the person's name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the person's name with validation.
        
        Args:
            value: The new name (must be non-empty).
            
        Raises:
            ValueError: If name is empty or not a string.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string")
        self._name = value.strip()
    
    @property
    def email(self) -> str:
        """Get the person's email."""
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Set the person's email with basic validation.
        
        Args:
            value: The new email address.
            
        Raises:
            ValueError: If email format is invalid.
        """
        if value and "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.__class__.__name__}(id={self._id}, name='{self._name}')"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"{self.__class__.__name__}(id={self._id}, name='{self._name}', "
                f"email='{self._email}')")
    
    def to_dict(self) -> dict:
        """Convert person to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the person.
        """
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Person":
        """Create a Person instance from a dictionary.
        
        Args:
            data: Dictionary containing person data.
            
        Returns:
            A new Person instance.
        """
        person = cls(data["name"], data.get("email", ""))
        person._id = data["id"]
        # Update class counter to avoid ID collisions
        if data["id"] > cls._id_counter:
            cls._id_counter = data["id"]
        return person
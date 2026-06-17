"""Unit tests for model classes.

Tests User, Project, and Task classes including:
- Initialization and properties
- Relationships (one-to-many, many-to-many)
- Validation and error handling
- Serialization/deserialization
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.person import Person
from models.user import User
from models.project import Project
from models.task import Task


class TestPerson:
    """Tests for the base Person class."""
    
    def test_person_initialization(self):
        """Test basic person creation."""
        person = Person("John Doe", "john@example.com")
        assert person.name == "John Doe"
        assert person.email == "john@example.com"
        assert person.id > 0
    
    def test_person_name_validation(self):
        """Test name setter validation."""
        person = Person("Test")
        with pytest.raises(ValueError):
            person.name = ""
        with pytest.raises(ValueError):
            person.name = 123
    
    def test_person_email_validation(self):
        """Test email setter validation."""
        person = Person("Test")
        with pytest.raises(ValueError):
            person.email = "invalid-email"
        person.email = "valid@example.com"
        assert person.email == "valid@example.com"
    
    def test_person_to_dict(self):
        """Test dictionary serialization."""
        person = Person("Jane", "jane@example.com")
        data = person.to_dict()
        assert data["name"] == "Jane"
        assert data["email"] == "jane@example.com"
    
    def test_person_from_dict(self):
        """Test deserialization from dictionary."""
        data = {"id": 99, "name": "Test", "email": "test@test.com"}
        person = Person.from_dict(data)
        assert person.id == 99
        assert person.name == "Test"


class TestUser:
    """Tests for the User class."""
    
    def setup_method(self):
        """Clear registry before each test."""
        User.clear_registry()
    
    def test_user_inheritance(self):
        """Test that User inherits from Person."""
        user = User("Alex")
        assert isinstance(user, Person)
        assert user.name == "Alex"
    
    def test_user_project_management(self):
        """Test one-to-many relationship: User -> Projects."""
        user = User("Alex")
        assert user.get_project_count() == 0
        
        user.add_project(1)
        user.add_project(2)
        assert user.get_project_count() == 2
        assert 1 in user.projects
        assert 2 in user.projects
    
    def test_user_duplicate_project(self):
        """Test adding duplicate project raises error."""
        user = User("Alex")
        user.add_project(1)
        with pytest.raises(ValueError):
            user.add_project(1)
    
    def test_user_registry(self):
        """Test class-level user registry."""
        user1 = User("User1")
        user2 = User("User2")
        
        assert User.get_user_by_id(user1.id) == user1
        assert User.get_user_by_id(user2.id) == user2
        assert len(User.get_all_users()) == 2
    
    def test_user_serialization(self):
        """Test user JSON serialization round-trip."""
        user = User("Alex", "alex@example.com")
        user.add_project(1)
        user.add_project(2)
        
        data = user.to_dict()
        User.clear_registry()
        
        restored = User.from_dict(data)
        assert restored.name == "Alex"
        assert restored.email == "alex@example.com"
        assert restored.projects == [1, 2]


class TestProject:
    """Tests for the Project class."""
    
    def setup_method(self):
        """Clear registry before each test."""
        Project.clear_registry()
    
    def test_project_initialization(self):
        """Test project creation."""
        project = Project("Test Project", "Description", "2025-12-31", 1)
        assert project.title == "Test Project"
        assert project.description == "Description"
        assert project.due_date == "2025-12-31"
        assert project.user_id == 1
    
    def test_project_title_validation(self):
        """Test title validation."""
        project = Project("Test")
        with pytest.raises(ValueError):
            project.title = ""
    
    def test_project_due_date_validation(self):
        """Test due date format validation."""
        project = Project("Test")
        with pytest.raises(ValueError):
            project.due_date = "invalid-date"
        project.due_date = "2025-12-31"
        assert project.due_date == "2025-12-31"
    
    def test_project_task_management(self):
        """Test one-to-many relationship: Project -> Tasks."""
        project = Project("Test")
        project.add_task(1)
        project.add_task(2)
        assert project.get_task_count() == 2
    
    def test_project_overdue(self):
        """Test overdue detection."""
        from datetime import datetime, timedelta
        
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        overdue_project = Project("Overdue", due_date=past_date)
        active_project = Project("Active", due_date=future_date)
        no_date_project = Project("No Date")
        
        assert overdue_project.is_overdue() == True
        assert active_project.is_overdue() == False
        assert no_date_project.is_overdue() == False
    
    def test_project_filter_by_user(self):
        """Test filtering projects by user ID."""
        p1 = Project("P1", user_id=1)
        p2 = Project("P2", user_id=1)
        p3 = Project("P3", user_id=2)
        
        user1_projects = Project.get_projects_by_user(1)
        assert len(user1_projects) == 2
        assert p1 in user1_projects
        assert p2 in user1_projects


class TestTask:
    """Tests for the Task class."""
    
    def setup_method(self):
        """Clear registry before each test."""
        Task.clear_registry()
    
    def test_task_initialization(self):
        """Test task creation."""
        task = Task("Implement feature", project_id=1)
        assert task.title == "Implement feature"
        assert task.status == "pending"
        assert task.project_id == 1
    
    def test_task_status_transitions(self):
        """Test status changes and completion tracking."""
        task = Task("Test")
        assert task.status == "pending"
        
        task.mark_in_progress()
        assert task.status == "in_progress"
        
        task.mark_complete()
        assert task.status == "completed"
        assert task.is_completed() == True
        assert task.completed_at != ""
    
    def test_task_status_validation(self):
        """Test invalid status rejection."""
        task = Task("Test")
        with pytest.raises(ValueError):
            task.status = "invalid_status"
    
    def test_task_assignment(self):
        """Test many-to-many user assignment."""
        task = Task("Test")
        task.assign_user(1)
        task.assign_user(2)
        assert len(task.assigned_to) == 2
        
        with pytest.raises(ValueError):
            task.assign_user(1)  # Duplicate
    
    def test_task_filtering(self):
        """Test task filtering by project and user."""
        t1 = Task("T1", project_id=1, assigned_to=[1])
        t2 = Task("T2", project_id=1, assigned_to=[1, 2])
        t3 = Task("T3", project_id=2, assigned_to=[2])
        
        p1_tasks = Task.get_tasks_by_project(1)
        assert len(p1_tasks) == 2
        
        u1_tasks = Task.get_tasks_by_user(1)
        assert len(u1_tasks) == 2
        
        u2_tasks = Task.get_tasks_by_user(2)
        assert len(u2_tasks) == 2
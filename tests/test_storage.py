"""Unit tests for StorageManager.

Tests JSON persistence including:
- Save/load round-trips
- Error handling for malformed files
- Missing file handling
"""
import pytest
import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import StorageManager


class TestStorageManager:
    """Tests for data persistence functionality."""
    
    def setup_method(self):
        """Create temporary directory and reset state."""
        self.temp_dir = tempfile.mkdtemp()
        User.clear_registry()
        Project.clear_registry()
        Task.clear_registry()
    
    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_users(self):
        """Test user persistence round-trip."""
        storage = StorageManager(self.temp_dir)
        
        user1 = User("Alex", "alex@example.com")
        user2 = User("Sam", "sam@example.com")
        
        storage.save_users()
        
        # Clear and reload
        User.clear_registry()
        assert len(User.get_all_users()) == 0
        
        storage.load_users()
        users = User.get_all_users()
        assert len(users) == 2
        
        names = {u.name for u in users}
        assert "Alex" in names
        assert "Sam" in names
    
    def test_save_and_load_projects(self):
        """Test project persistence round-trip."""
        storage = StorageManager(self.temp_dir)
        
        project = Project("Test Project", "Description", "2025-12-31", 1)
        project.add_task(1)
        
        storage.save_projects()
        
        Project.clear_registry()
        storage.load_projects()
        
        projects = Project.get_all_projects()
        assert len(projects) == 1
        assert projects[0].title == "Test Project"
        assert projects[0].tasks == [1]
    
    def test_save_and_load_tasks(self):
        """Test task persistence round-trip."""
        storage = StorageManager(self.temp_dir)
        
        task = Task("Test Task", project_id=1, assigned_to=[1, 2])
        task.mark_complete()
        
        storage.save_tasks()
        
        Task.clear_registry()
        storage.load_tasks()
        
        tasks = Task.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"
        assert tasks[0].status == "completed"
        assert tasks[0].assigned_to == [1, 2]
    
    def test_load_missing_files(self):
        """Test graceful handling of missing files."""
        storage = StorageManager(self.temp_dir)
        
        # Should not raise exceptions
        storage.load_users()
        storage.load_projects()
        storage.load_tasks()
        
        assert len(User.get_all_users()) == 0
        assert len(Project.get_all_projects()) == 0
        assert len(Task.get_all_tasks()) == 0
    
    def test_load_malformed_json(self):
        """Test handling of malformed JSON files."""
        storage = StorageManager(self.temp_dir)
        
        # Create invalid JSON
        with open(storage.users_file, "w") as f:
            f.write("{invalid json")
        
        # Should handle gracefully without crashing
        storage.load_users()
        assert len(User.get_all_users()) == 0
    
    def test_load_invalid_data_structure(self):
        """Test handling of valid JSON but wrong structure."""
        storage = StorageManager(self.temp_dir)
        
        # Create JSON that's not a list
        with open(storage.users_file, "w") as f:
            json.dump({"not": "a list"}, f)
        
        storage.load_users()
        assert len(User.get_all_users()) == 0
    
    def test_full_persistence(self):
        """Test complete save/load cycle with all entities."""
        storage = StorageManager(self.temp_dir)
        
        # Create data
        user = User("Alex", "alex@example.com")
        project = Project("CLI Tool", "Build CLI", "2025-12-31", user.id)
        user.add_project(project.id)
        task = Task("Implement CLI", project.id, assigned_to=[user.id])
        project.add_task(task.id)
        
        # Save all
        assert storage.save_all() == True
        
        # Clear all
        User.clear_registry()
        Project.clear_registry()
        Task.clear_registry()
        
        # Load all
        assert storage.load_all() == True
        
        # Verify
        assert len(User.get_all_users()) == 1
        assert len(Project.get_all_projects()) == 1
        assert len(Task.get_all_tasks()) == 1
        
        restored_user = User.get_all_users()[0]
        restored_project = Project.get_all_projects()[0]
        restored_task = Task.get_all_tasks()[0]
        
        assert restored_user.name == "Alex"
        assert restored_project.title == "CLI Tool"
        assert restored_task.title == "Implement CLI"
        assert restored_task.project_id == restored_project.id
    
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        storage = StorageManager(self.temp_dir)
        
        User("Alex", "alex@example.com")
        storage.save_users()
        
        result = storage.export_to_csv("users_export.csv", "users")
        assert result == True
        
        export_path = os.path.join(self.temp_dir, "users_export.csv")
        assert os.path.exists(export_path)
        
        with open(export_path, "r") as f:
            content = f.read()
            assert "Alex" in content
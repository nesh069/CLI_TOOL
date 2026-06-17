"""Unit tests for CLI commands.

Tests command handlers with mock data to verify:
- User creation and listing
- Project creation and association
- Task creation and completion
- Error handling for missing entities
"""
import pytest
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import StorageManager
from main import (
    cmd_add_user, cmd_list_users, cmd_add_project, cmd_list_projects,
    cmd_add_task, cmd_list_tasks, cmd_complete_task, cmd_search
)


class TestCLICommands:
    """Integration tests for CLI command handlers."""
    
    def setup_method(self):
        """Reset state before each test."""
        User.clear_registry()
        Project.clear_registry()
        Task.clear_registry()
    
    def test_add_user(self, capsys):
        """Test adding a user via CLI."""
        args = argparse.Namespace(name="Alex", email="alex@example.com")
        result = cmd_add_user(args)
        
        assert result == 0
        users = User.get_all_users()
        assert len(users) == 1
        assert users[0].name == "Alex"
    
    def test_add_user_duplicate_name_allowed(self):
        """Test that users with same name but different IDs are allowed."""
        args1 = argparse.Namespace(name="Alex", email="alex1@example.com")
        args2 = argparse.Namespace(name="Alex", email="alex2@example.com")
        
        cmd_add_user(args1)
        cmd_add_user(args2)
        
        assert len(User.get_all_users()) == 2
    
    def test_list_users_empty(self, capsys):
        """Test listing users when none exist."""
        args = argparse.Namespace()
        result = cmd_list_users(args)
        assert result == 0
    
    def test_add_project(self):
        """Test adding a project to a user."""
        # First create a user
        user_args = argparse.Namespace(name="Alex", email="")
        cmd_add_user(user_args)
        
        # Then add a project
        project_args = argparse.Namespace(
            user="Alex", title="CLI Tool", description="Build CLI", due_date=""
        )
        result = cmd_add_project(project_args)
        
        assert result == 0
        assert len(Project.get_all_projects()) == 1
        
        user = User.get_all_users()[0]
        assert user.get_project_count() == 1
    
    def test_add_project_user_not_found(self):
        """Test adding project to non-existent user."""
        args = argparse.Namespace(
            user="NonExistent", title="Test", description="", due_date=""
        )
        result = cmd_add_project(args)
        assert result == 1
    
    def test_add_task(self):
        """Test adding a task to a project."""
        # Setup: user -> project -> task
        cmd_add_user(argparse.Namespace(name="Alex", email=""))
        cmd_add_project(argparse.Namespace(
            user="Alex", title="CLI Tool", description="", due_date=""
        ))
        
        args = argparse.Namespace(
            project="CLI Tool", title="Implement feature", assigned=None
        )
        result = cmd_add_task(args)
        
        assert result == 0
        assert len(Task.get_all_tasks()) == 1
        
        project = Project.get_all_projects()[0]
        assert project.get_task_count() == 1
    
    def test_add_task_project_not_found(self):
        """Test adding task to non-existent project."""
        args = argparse.Namespace(
            project="NonExistent", title="Test", assigned=None
        )
        result = cmd_add_task(args)
        assert result == 1
    
    def test_complete_task(self):
        """Test marking a task as complete."""
        # Setup
        cmd_add_user(argparse.Namespace(name="Alex", email=""))
        cmd_add_project(argparse.Namespace(
            user="Alex", title="CLI Tool", description="", due_date=""
        ))
        cmd_add_task(argparse.Namespace(
            project="CLI Tool", title="Feature", assigned=None
        ))
        
        task = Task.get_all_tasks()[0]
        assert task.status == "pending"
        
        args = argparse.Namespace(id=task.id)
        result = cmd_complete_task(args)
        
        assert result == 0
        assert task.status == "completed"
    
    def test_complete_task_not_found(self):
        """Test completing non-existent task."""
        args = argparse.Namespace(id=999)
        result = cmd_complete_task(args)
        assert result == 1
    
    def test_search(self):
        """Test search functionality."""
        cmd_add_user(argparse.Namespace(name="Alex", email=""))
        cmd_add_project(argparse.Namespace(
            user="Alex", title="CLI Tool", description="", due_date=""
        ))
        
        args = argparse.Namespace(query="CLI")
        result = cmd_search(args)
        assert result == 0
    
    def test_list_projects_by_user(self):
        """Test filtering projects by user."""
        cmd_add_user(argparse.Namespace(name="Alex", email=""))
        cmd_add_project(argparse.Namespace(
            user="Alex", title="Project1", description="", due_date=""
        ))
        
        args = argparse.Namespace(user="Alex")
        result = cmd_list_projects(args)
        assert result == 0
    
    def test_list_tasks_by_project(self):
        """Test filtering tasks by project."""
        cmd_add_user(argparse.Namespace(name="Alex", email=""))
        cmd_add_project(argparse.Namespace(
            user="Alex", title="CLI Tool", description="", due_date=""
        ))
        cmd_add_task(argparse.Namespace(
            project="CLI Tool", title="Task1", assigned=None
        ))
        
        args = argparse.Namespace(project="CLI Tool", user="")
        result = cmd_list_tasks(args)
        assert result == 0
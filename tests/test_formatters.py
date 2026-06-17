"""Basic tests for the formatters module.

Just checks the functions dont crash basically.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.formatters import print_success, print_error, print_warning, print_info, print_header, format_table


class TestFormatters:
    """Smoke tests for terminal output functions."""

    def test_print_success(self, capsys):
        """should not raise any errors"""
        print_success("test worked")
        out, err = capsys.readouterr()
        assert "test worked" in out

    def test_print_error(self, capsys):
        print_error("something broke")
        out, err = capsys.readouterr()
        assert "something broke" in out

    def test_print_warning(self, capsys):
        print_warning("be careful")
        out, err = capsys.readouterr()
        assert "be careful" in out

    def test_print_info(self, capsys):
        print_info("just so you know")
        out, err = capsys.readouterr()
        assert "just so you know" in out

    def test_print_header(self, capsys):
        """header prints a rule line with the title"""
        print_header("My Header")
        out, err = capsys.readouterr()
        assert "My Header" in out

    def test_format_table_with_data(self, capsys):
        """table with rows should print without error"""
        data = [
            {"id": 1, "name": "Alex", "email": "alex@test.com"},
            {"id": 2, "name": "Sam", "email": "sam@test.com"},
        ]
        format_table(data)
        out, err = capsys.readouterr()
        assert "Alex" in out
        assert "Sam" in out

    def test_format_table_empty(self, capsys):
        """empty data list should just do nothing"""
        format_table([])
        out, err = capsys.readouterr()
        assert out == ""

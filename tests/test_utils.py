# tests/test_utils.py
"""
Unit tests for utility functions.
Run with: pytest tests/test_utils.py -v
"""

import pytest
from datetime import datetime, timedelta
from app.utils import (
    validate_email,
    calculate_priority_score,
    sanitize_input,
    parse_date,
)


class TestValidateEmail:
    """Tests for email validation"""

    def test_valid_email_simple(self):
        assert validate_email("user@example.com") == True

    def test_valid_email_with_subdomain(self):
        assert validate_email("user@mail.example.com") == True

    def test_invalid_email_no_at_symbol(self):
        # This test SHOULD pass but will FAIL due to bug
        assert validate_email("userexample.com") == False

    def test_invalid_email_no_domain(self):
        # This test SHOULD pass but will FAIL due to bug
        assert validate_email("user@") == False

    def test_invalid_email_spaces(self):
        # This test SHOULD pass but will FAIL due to bug
        assert validate_email("user @example.com") == False

    def test_invalid_email_special_chars(self):
        assert validate_email("user<script>@example.com") == False


class TestCalculatePriorityScore:
    """Tests for priority score calculation"""

    def test_critical_overdue(self):
        # Critical (100) + overdue bonus (50) = 150
        assert calculate_priority_score("critical", -5) == 150

    def test_high_due_today(self):
        # High (75) + due today bonus (30) = 105
        assert calculate_priority_score("high", 0) == 105

    def test_medium_due_in_3_days(self):
        # Medium (50) + within 3 days bonus (20) = 70
        # This will FAIL due to off-by-one bug
        assert calculate_priority_score("medium", 3) == 70

    def test_low_due_in_7_days(self):
        # Low (25) + within 7 days bonus (10) = 35
        # This will FAIL due to off-by-one bug
        assert calculate_priority_score("low", 7) == 35

    def test_low_due_in_30_days(self):
        # Low (25) + no bonus (0) = 25
        assert calculate_priority_score("low", 30) == 25

    def test_invalid_priority(self):
        # This should handle gracefully, not crash
        # This will FAIL - raises KeyError
        with pytest.raises(ValueError):
            calculate_priority_score("urgent", 5)


class TestSanitizeInput:
    """Tests for input sanitization - SECURITY CRITICAL"""

    def test_removes_script_tags(self):
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "</script>" not in result

    def test_removes_script_variations(self):
        # This will FAIL - case sensitivity bug
        result = sanitize_input("<SCRIPT>alert('xss')</SCRIPT>")
        assert "alert" not in result.lower()

    def test_removes_img_onerror(self):
        # This will FAIL - incomplete sanitization
        result = sanitize_input('<img src="x" onerror="alert(1)">')
        assert "onerror" not in result

    def test_removes_javascript_url(self):
        # This will FAIL - incomplete sanitization
        result = sanitize_input('<a href="javascript:alert(1)">click</a>')
        assert "javascript:" not in result

    def test_empty_string(self):
        assert sanitize_input("") == ""

    def test_none_handling(self):
        # This might fail depending on implementation
        assert sanitize_input(None) == ""


class TestParseDate:
    """Tests for date parsing"""

    def test_valid_date(self):
        result = parse_date("2026-02-15")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_invalid_format(self):
        # This will FAIL - no error handling
        with pytest.raises(ValueError):
            parse_date("15-02-2026")  # Wrong format

    def test_invalid_date_string(self):
        # This will FAIL - no error handling
        with pytest.raises(ValueError):
            parse_date("not-a-date")

    def test_empty_string(self):
        # This will FAIL - no error handling
        with pytest.raises(ValueError):
            parse_date("")

import pytest
import json
from unittest.mock import Mock, patch
from src.credx_ai.resume_parser import (
    clean_text,
    validate_profile,
    ResumeParser
)

def test_clean_text():
    """Test text cleaning functionality."""
    dirty_text = "This is a test-\nwith broken lines\n\n\nand   multiple    spaces"
    cleaned = clean_text(dirty_text)
    expected = "This is a testwith broken lines\n\nand multiple spaces"
    assert cleaned == expected

def test_validate_profile_complete():
    """Test profile validation with complete data."""
    valid_profile = {
        "name": "John Doe",
        "email": "john@example.com", 
        "phone": "+1234567890",
        "skills": ["Python", "JavaScript"],
        "experience_summary": "5 years of software development",
        "education": [{"degree": "BS Computer Science", "institution": "MIT", "start_date": "2015", "end_date": "2019"}],
        "seniority_level": "Senior",
        "job_interests": ["Backend Developer", "ML Engineer"],
        "raw_text": "Sample resume text",
        "confidence": 0.85
    }
    
    validated = validate_profile(valid_profile)
    assert validated["name"] == "John Doe"
    assert validated["seniority_level"] == "Senior"
    assert 0.0 <= validated["confidence"] <= 1.0

def test_validate_profile_missing_fields():
    """Test profile validation adds missing fields."""
    incomplete_profile = {
        "name": "Jane Doe",
        "skills": ["React", "Node.js"]
    }
    
    validated = validate_profile(incomplete_profile)
    assert "experience_summary" in validated
    assert "education" in validated
    assert "seniority_level" in validated
    assert validated["seniority_level"] == "Unknown"
    assert validated["confidence"] == 0.0

def test_legacy_resume_parser_class():
    """Test legacy ResumeParser class initialization."""
    parser = ResumeParser("test_api_key")
    assert parser.api_key == "test_api_key"

def test_handles_poor_formatting():
    """Test text cleaning handles poor formatting."""
    poorly_formatted = """Name: John-
Doe
Skills:    Python,     JavaScript,
React

Experience:
Software    Engineer
2020-2023


Education: BS Computer Science"""
    
    cleaned = clean_text(poorly_formatted)
    
    # Should merge hyphenated line breaks
    assert "John-\nDoe" not in cleaned
    # Should normalize excessive whitespace
    assert "    " not in cleaned
    assert "     " not in cleaned

def test_confidence_bounds():
    """Test confidence score is properly bounded."""
    profile_high = {"confidence": 1.5}
    profile_low = {"confidence": -0.5}
    
    validated_high = validate_profile(profile_high)
    validated_low = validate_profile(profile_low)
    
    assert validated_high["confidence"] == 1.0
    assert validated_low["confidence"] == 0.0

def test_seniority_levels():
    """Test valid seniority levels."""
    valid_levels = ["Intern", "Entry", "Mid", "Senior", "Lead", "Manager", "Director", "Executive", "Unknown"]
    
    for level in valid_levels:
        profile = {"seniority_level": level}
        validated = validate_profile(profile)
        assert validated["seniority_level"] == level

def test_schema_structure():
    """Test that required fields are present after validation."""
    empty_profile = {}
    validated = validate_profile(empty_profile)
    
    required_fields = ["name", "email", "phone", "skills", "experience_summary", 
                      "education", "seniority_level", "job_interests", "raw_text", "confidence"]
    
    for field in required_fields:
        assert field in validated
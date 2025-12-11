import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from src.credx_ai.resume_parser import (
    extract_text_from_pdf,
    fallback_extract_text,
    clean_text,
    call_gemini,
    validate_profile,
    parse_resume,
    ResumeParser,
    PROFILE_SCHEMA
)

class TestResumeParser:
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "This is a test-\nwith broken lines\n\n\nand   multiple    spaces"
        cleaned = clean_text(dirty_text)
        expected = "This is a testwith broken lines\n\nand multiple spaces"
        assert cleaned == expected
    
    def test_validate_profile_schema(self):
        """Test profile validation with correct schema."""
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
        assert isinstance(validated, dict)
        assert validated["name"] == "John Doe"
        assert validated["seniority_level"] in ["Intern", "Entry", "Mid", "Senior", "Lead", "Manager", "Director", "Executive", "Unknown"]
        assert 0.0 <= validated["confidence"] <= 1.0
    
    def test_validate_profile_missing_fields(self):
        """Test profile validation with missing fields."""
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
    
    @patch('src.credx_ai.resume_parser.genai')
    def test_call_gemini_success(self, mock_genai):
        """Test successful Gemini API call."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "name": "Test User",
            "email": "test@example.com",
            "phone": None,
            "skills": ["Python", "Machine Learning"],
            "experience_summary": "Experienced developer",
            "education": [],
            "seniority_level": "Senior",
            "job_interests": ["Data Scientist"],
            "confidence": 0.9
        })
        
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()
        mock_genai.types.GenerationConfig = Mock()
        
        result = call_gemini("Sample resume text", "test_api_key")
        
        assert result["name"] == "Test User"
        assert result["skills"] == ["Python", "Machine Learning"]
        assert result["seniority_level"] == "Senior"
        assert "raw_text" in result
    
    @patch('src.credx_ai.resume_parser.genai')
    def test_call_gemini_failure(self, mock_genai):
        """Test Gemini API call failure."""
        mock_genai.configure.side_effect = Exception("API Error")
        
        result = call_gemini("Sample resume text", "test_api_key")
        
        assert result["name"] is None
        assert result["experience_summary"] == "Failed to parse resume content"
        assert result["confidence"] == 0.0
        assert result["raw_text"] == "Sample resume text"
    
    @patch('src.credx_ai.resume_parser.fitz')
    def test_extract_text_from_pdf_success(self, mock_fitz):
        """Test successful PDF text extraction."""
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Sample PDF content"
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.close = Mock()
        mock_fitz.open.return_value = mock_doc
        
        result = extract_text_from_pdf("test.pdf")
        assert result == "Sample PDF content"
        mock_doc.close.assert_called_once()
    
    @patch('src.credx_ai.resume_parser.fitz')
    def test_extract_text_from_pdf_failure(self, mock_fitz):
        """Test PDF text extraction failure."""
        mock_fitz.open.side_effect = Exception("PDF Error")
        
        result = extract_text_from_pdf("test.pdf")
        assert result == ""
    
    @patch('src.credx_ai.resume_parser.pytesseract', None)
    @patch('src.credx_ai.resume_parser.Image', None)
    @patch('src.credx_ai.resume_parser.pdfminer_extract')
    def test_fallback_extract_text_pdfminer(self, mock_pdfminer):
        """Test fallback extraction using pdfminer."""
        mock_pdfminer.return_value = "Extracted text from pdfminer with sufficient length to pass the 200 character threshold for successful extraction"
        
        result = fallback_extract_text("test.pdf")
        assert "Extracted text from pdfminer" in result
        assert len(result) > 200
    
    def test_seniority_inference_from_profile(self):
        """Test seniority level inference."""
        senior_profile = {
            "name": "Senior Developer",
            "skills": ["Python", "Leadership"],
            "experience_summary": "Senior Software Engineer with 8+ years experience",
            "education": [],
            "seniority_level": "Senior",
            "job_interests": ["Tech Lead"],
            "raw_text": "Senior Software Engineer, 8+ years",
            "confidence": 0.8
        }
        
        validated = validate_profile(senior_profile)
        assert validated["seniority_level"] == "Senior"
    
    @patch('src.credx_ai.resume_parser.validate_profile')
    @patch('src.credx_ai.resume_parser.call_gemini')
    @patch('src.credx_ai.resume_parser.clean_text')
    @patch('src.credx_ai.resume_parser.fallback_extract_text')
    @patch('src.credx_ai.resume_parser.extract_text_from_pdf')
    @patch('src.credx_ai.resume_parser.os.path.exists')
    def test_parse_resume_success(self, mock_exists, mock_extract, mock_fallback, mock_clean, mock_gemini, mock_validate):
        """Test successful resume parsing."""
        mock_exists.return_value = True
        mock_extract.return_value = "Sample resume content with sufficient length for processing and analysis"
        mock_clean.return_value = "Cleaned resume content"
        mock_gemini.return_value = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": None,
            "skills": ["Python", "JavaScript"],
            "experience_summary": "Experienced developer",
            "education": [],
            "seniority_level": "Mid",
            "job_interests": ["Full Stack Developer"],
            "raw_text": "Sample resume content",
            "confidence": 0.85
        }
        mock_validate.return_value = mock_gemini.return_value
        
        result = parse_resume("test.pdf", "test_api_key")
        
        assert result["name"] == "John Doe"
        assert "Python" in result["skills"]
        assert result["seniority_level"] == "Mid"
        assert 0.0 <= result["confidence"] <= 1.0
    
    @patch('src.credx_ai.resume_parser.os.path.exists')
    def test_parse_resume_file_not_found(self, mock_exists):
        """Test resume parsing with non-existent file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            parse_resume("nonexistent.pdf")
    
    @patch('src.credx_ai.resume_parser.fallback_extract_text')
    @patch('src.credx_ai.resume_parser.extract_text_from_pdf')
    @patch('src.credx_ai.resume_parser.os.path.exists')
    def test_parse_resume_insufficient_text(self, mock_exists, mock_extract, mock_fallback):
        """Test resume parsing with insufficient text extraction."""
        mock_exists.return_value = True
        mock_extract.return_value = "Short"  # Less than 200 chars
        mock_fallback.return_value = "Also short"  # Less than 50 chars
        
        with pytest.raises(ValueError, match="Could not extract meaningful text"):
            parse_resume("test.pdf", "test_api_key")
    
    def test_legacy_resume_parser_class(self):
        """Test legacy ResumeParser class for backward compatibility."""
        parser = ResumeParser("test_api_key")
        assert parser.api_key == "test_api_key"
    
    @patch('src.credx_ai.resume_parser.fitz')
    def test_legacy_parser_extract_from_stream(self, mock_fitz):
        """Test legacy parser file stream extraction."""
        mock_file = Mock()
        mock_file.read.return_value = b"PDF content"
        
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Extracted text"
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.close = Mock()
        mock_fitz.open.return_value = mock_doc
        
        parser = ResumeParser("test_api_key")
        result = parser._extract_text_from_pdf(mock_file)
        
        assert result == "Extracted text"
        mock_doc.close.assert_called_once()
    
    def test_handles_poor_formatting(self):
        """Test handling of poorly formatted text."""
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
        assert "JohnDoe" in cleaned or "John Doe" in cleaned
        
        # Should normalize excessive whitespace
        assert "    " not in cleaned
        assert "     " not in cleaned
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'env_api_key'})
    @patch('src.credx_ai.resume_parser.validate_profile')
    @patch('src.credx_ai.resume_parser.call_gemini')
    @patch('src.credx_ai.resume_parser.clean_text')
    @patch('src.credx_ai.resume_parser.fallback_extract_text')
    @patch('src.credx_ai.resume_parser.extract_text_from_pdf')
    @patch('src.credx_ai.resume_parser.os.path.exists')
    def test_parse_resume_uses_env_api_key(self, mock_exists, mock_extract, mock_fallback, mock_clean, mock_gemini, mock_validate):
        """Test that parse_resume uses environment API key when none provided."""
        mock_exists.return_value = True
        mock_extract.return_value = "Sample resume content with sufficient length for processing and analysis"
        mock_clean.return_value = "Cleaned content"
        mock_gemini.return_value = {
            "name": None,
            "email": None,
            "phone": None,
            "skills": [],
            "experience_summary": "",
            "education": [],
            "seniority_level": "Unknown",
            "job_interests": [],
            "raw_text": "Sample resume content",
            "confidence": 0.0
        }
        mock_validate.return_value = mock_gemini.return_value
        
        parse_resume("test.pdf")  # No API key provided
        
        # Should call gemini with env API key
        mock_gemini.assert_called_once()
        args, kwargs = mock_gemini.call_args
        assert args[1] == 'env_api_key'  # Second argument should be the API key
"""
Tests for shared utilities
"""
import pytest
from datetime import datetime, timedelta

from shared.utils import (
    generate_uuid,
    generate_short_id,
    generate_api_key,
    hash_password,
    verify_password,
    generate_file_hash,
    sanitize_filename,
    validate_email,
    validate_url,
    format_file_size,
    parse_file_size,
    get_file_extension,
    is_allowed_file_type,
    truncate_string,
    camel_to_snake,
    snake_to_camel,
    deep_merge_dicts,
    flatten_dict,
    chunk_list,
    remove_none_values,
    get_timestamp,
    parse_timestamp,
    add_days,
    add_hours,
    is_expired,
    CircuitBreaker
)


def test_generate_uuid():
    """Test UUID generation"""
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()
    
    assert len(uuid1) == 36  # Standard UUID length
    assert uuid1 != uuid2  # Should be unique
    assert '-' in uuid1  # Should contain hyphens


def test_generate_short_id():
    """Test short ID generation"""
    short_id = generate_short_id(8)
    
    assert len(short_id) == 8
    assert short_id.isalnum()  # Should be alphanumeric


def test_generate_api_key():
    """Test API key generation"""
    api_key = generate_api_key(32)
    
    assert len(api_key) == 32
    assert api_key.isalnum()


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed != password  # Should be hashed
    assert len(hashed) == 64  # SHA-256 hex length
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_generate_file_hash():
    """Test file hash generation"""
    content1 = b"Hello, World!"
    content2 = b"Different content"
    
    hash1 = generate_file_hash(content1)
    hash2 = generate_file_hash(content2)
    
    assert len(hash1) == 64  # SHA-256 hex length
    assert hash1 != hash2  # Different content should have different hashes
    assert generate_file_hash(content1) == hash1  # Same content should have same hash


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("test file.pdf") == "test_file.pdf"
    assert sanitize_filename("file@#$%^&*().txt") == "file.txt"
    assert sanitize_filename("file...with...dots.pdf") == "file.with.dots.pdf"
    
    # Test long filename
    long_name = "a" * 300 + ".txt"
    sanitized = sanitize_filename(long_name)
    assert len(sanitized) <= 255


def test_validate_email():
    """Test email validation"""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name+tag@domain.co.uk") is True
    assert validate_email("invalid.email") is False
    assert validate_email("@domain.com") is False
    assert validate_email("user@") is False


def test_validate_url():
    """Test URL validation"""
    assert validate_url("https://example.com") is True
    assert validate_url("http://localhost:8000") is True
    assert validate_url("ftp://files.example.com") is True
    assert validate_url("not-a-url") is False
    assert validate_url("://missing-scheme.com") is False


def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1536) == "1.5 KB"


def test_parse_file_size():
    """Test file size parsing"""
    assert parse_file_size("1024") == 1024
    assert parse_file_size("1 KB") == 1024
    assert parse_file_size("1.5 MB") == int(1.5 * 1024 * 1024)
    assert parse_file_size("2 GB") == 2 * 1024 * 1024 * 1024
    
    with pytest.raises(ValueError):
        parse_file_size("invalid size")


def test_get_file_extension():
    """Test file extension extraction"""
    assert get_file_extension("file.pdf") == "pdf"
    assert get_file_extension("document.DOC") == "doc"
    assert get_file_extension("no_extension") == ""
    assert get_file_extension("file.tar.gz") == "gz"


def test_is_allowed_file_type():
    """Test file type validation"""
    allowed_types = ["pdf", "doc", "txt"]
    
    assert is_allowed_file_type("document.pdf", allowed_types) is True
    assert is_allowed_file_type("file.DOC", allowed_types) is True
    assert is_allowed_file_type("image.jpg", allowed_types) is False


def test_truncate_string():
    """Test string truncation"""
    text = "This is a long string that needs to be truncated"
    
    assert truncate_string(text, 20) == "This is a long st..."
    assert truncate_string(text, 100) == text  # No truncation needed
    assert truncate_string(text, 20, "***") == "This is a long st***"


def test_camel_to_snake():
    """Test camelCase to snake_case conversion"""
    assert camel_to_snake("camelCase") == "camel_case"
    assert camel_to_snake("XMLHttpRequest") == "xml_http_request"
    assert camel_to_snake("simpleWord") == "simple_word"
    assert camel_to_snake("alreadysnake_case") == "alreadysnake_case"


def test_snake_to_camel():
    """Test snake_case to camelCase conversion"""
    assert snake_to_camel("snake_case") == "snakeCase"
    assert snake_to_camel("simple_word") == "simpleWord"
    assert snake_to_camel("already_camelCase") == "alreadyCamelCase"


def test_deep_merge_dicts():
    """Test deep dictionary merging"""
    dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
    dict2 = {"b": {"d": 4, "e": 5}, "f": 6}
    
    result = deep_merge_dicts(dict1, dict2)
    
    assert result["a"] == 1
    assert result["b"]["c"] == 2
    assert result["b"]["d"] == 4  # Overwritten
    assert result["b"]["e"] == 5  # Added
    assert result["f"] == 6


def test_flatten_dict():
    """Test dictionary flattening"""
    nested = {
        "a": 1,
        "b": {
            "c": 2,
            "d": {
                "e": 3
            }
        }
    }
    
    flattened = flatten_dict(nested)
    
    assert flattened["a"] == 1
    assert flattened["b.c"] == 2
    assert flattened["b.d.e"] == 3


def test_chunk_list():
    """Test list chunking"""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chunks = chunk_list(data, 3)
    
    assert len(chunks) == 4
    assert chunks[0] == [1, 2, 3]
    assert chunks[1] == [4, 5, 6]
    assert chunks[2] == [7, 8, 9]
    assert chunks[3] == [10]


def test_remove_none_values():
    """Test None value removal"""
    data = {"a": 1, "b": None, "c": "value", "d": None}
    cleaned = remove_none_values(data)
    
    assert "a" in cleaned
    assert "c" in cleaned
    assert "b" not in cleaned
    assert "d" not in cleaned


def test_timestamp_functions():
    """Test timestamp utilities"""
    # Test timestamp generation and parsing
    timestamp_str = get_timestamp()
    parsed = parse_timestamp(timestamp_str)
    
    assert isinstance(parsed, datetime)
    
    # Test date arithmetic
    now = datetime.utcnow()
    future = add_days(now, 5)
    past = add_hours(now, -2)
    
    assert future > now
    assert past < now
    
    # Test expiration check
    expired_date = datetime.utcnow() - timedelta(hours=1)
    future_date = datetime.utcnow() + timedelta(hours=1)
    
    assert is_expired(expired_date) is True
    assert is_expired(future_date) is False


def test_circuit_breaker():
    """Test circuit breaker functionality"""
    breaker = CircuitBreaker(failure_threshold=2, timeout=1)
    
    # Function that always fails
    def failing_function():
        raise Exception("Always fails")
    
    # Function that always succeeds
    def success_function():
        return "success"
    
    # Test initial state
    assert breaker.state == "CLOSED"
    
    # Test successful calls
    result = breaker.call(success_function)
    assert result == "success"
    assert breaker.state == "CLOSED"
    
    # Test failures
    with pytest.raises(Exception):
        breaker.call(failing_function)
    
    with pytest.raises(Exception):
        breaker.call(failing_function)
    
    # Should be open now
    assert breaker.state == "OPEN"
    
    # Should raise circuit breaker exception
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        breaker.call(success_function)


if __name__ == "__main__":
    pytest.main([__file__])
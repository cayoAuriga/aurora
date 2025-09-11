# utils/password.py
# Password hashing utilities with enhanced security features

from passlib.context import CryptContext
from typing import Optional
import secrets
import string

# Configure password context with bcrypt and argon2
# bcrypt is the default, argon2 is more secure but requires additional dependencies
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increase rounds for better security (default is 12)
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # In case of any error (e.g., invalid hash format), return False
        return False

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

# Alias for compatibility
get_password_hash = hash_password

def generate_password(
    length: int = 16,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_special: bool = True,
    exclude_ambiguous: bool = True
) -> str:
    """
    Generate a secure random password
    
    Args:
        length: Length of the password (minimum 8)
        include_uppercase: Include uppercase letters
        include_lowercase: Include lowercase letters
        include_digits: Include digits
        include_special: Include special characters
        exclude_ambiguous: Exclude ambiguous characters (0, O, l, 1, etc.)
        
    Returns:
        str: A randomly generated password
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")
    
    # Build character set
    characters = ""
    required_chars = []
    
    if include_uppercase:
        uppercase = string.ascii_uppercase
        if exclude_ambiguous:
            uppercase = uppercase.replace('O', '').replace('I', '')
        characters += uppercase
        required_chars.append(secrets.choice(uppercase))
    
    if include_lowercase:
        lowercase = string.ascii_lowercase
        if exclude_ambiguous:
            lowercase = lowercase.replace('o', '').replace('l', '').replace('i', '')
        characters += lowercase
        required_chars.append(secrets.choice(lowercase))
    
    if include_digits:
        digits = string.digits
        if exclude_ambiguous:
            digits = digits.replace('0', '').replace('1', '')
        characters += digits
        required_chars.append(secrets.choice(digits))
    
    if include_special:
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if exclude_ambiguous:
            special = special.replace('|', '').replace('l', '')
        characters += special
        required_chars.append(secrets.choice(special))
    
    if not characters:
        raise ValueError("At least one character type must be included")
    
    # Generate remaining characters
    remaining_length = length - len(required_chars)
    if remaining_length > 0:
        password_chars = required_chars + [
            secrets.choice(characters) for _ in range(remaining_length)
        ]
    else:
        password_chars = required_chars[:length]
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)

def check_password_strength(password: str) -> dict:
    """
    Check password strength and return detailed analysis
    
    Args:
        password: The password to check
        
    Returns:
        dict: Analysis results including score and suggestions
    """
    results = {
        "score": 0,  # 0-5 score
        "length": len(password),
        "has_uppercase": False,
        "has_lowercase": False,
        "has_digits": False,
        "has_special": False,
        "has_repeated_chars": False,
        "is_common": False,
        "suggestions": []
    }
    
    # Check length
    if len(password) >= 8:
        results["score"] += 1
    else:
        results["suggestions"].append("Use at least 8 characters")
    
    if len(password) >= 12:
        results["score"] += 1
    
    # Check character types
    if any(c.isupper() for c in password):
        results["has_uppercase"] = True
        results["score"] += 0.5
    else:
        results["suggestions"].append("Add uppercase letters")
    
    if any(c.islower() for c in password):
        results["has_lowercase"] = True
        results["score"] += 0.5
    else:
        results["suggestions"].append("Add lowercase letters")
    
    if any(c.isdigit() for c in password):
        results["has_digits"] = True
        results["score"] += 0.5
    else:
        results["suggestions"].append("Add numbers")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        results["has_special"] = True
        results["score"] += 0.5
    else:
        results["suggestions"].append("Add special characters")
    
    # Check for repeated characters
    for i in range(len(password) - 2):
        if password[i] == password[i + 1] == password[i + 2]:
            results["has_repeated_chars"] = True
            results["score"] -= 0.5
            results["suggestions"].append("Avoid repeated characters")
            break
    
    # Check against common passwords (simplified check)
    common_passwords = [
        "password", "123456", "password123", "admin", "letmein",
        "welcome", "monkey", "dragon", "123456789", "qwerty"
    ]
    if password.lower() in common_passwords:
        results["is_common"] = True
        results["score"] -= 1
        results["suggestions"].append("Avoid common passwords")
    
    # Cap score at 5
    results["score"] = min(5, max(0, results["score"]))
    
    # Add strength label
    if results["score"] < 2:
        results["strength"] = "weak"
    elif results["score"] < 3.5:
        results["strength"] = "moderate"
    else:
        results["strength"] = "strong"
    
    return results

def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be rehashed
    (e.g., if the hashing algorithm or parameters have changed)
    
    Args:
        hashed_password: The hashed password to check
        
    Returns:
        bool: True if the password needs rehashing
    """
    return pwd_context.needs_update(hashed_password)

# For testing purposes
if __name__ == "__main__":
    # Test password generation
    test_password = generate_password()
    print(f"Generated password: {test_password}")
    
    # Test password strength
    strength = check_password_strength(test_password)
    print(f"Password strength: {strength}")
    
    # Test hashing and verification
    hashed = hash_password(test_password)
    print(f"Hashed: {hashed}")
    print(f"Verified: {verify_password(test_password, hashed)}")
    print(f"Wrong password verified: {verify_password('wrong_password', hashed)}")
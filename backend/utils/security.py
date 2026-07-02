import os
import re
import html
from typing import Tuple

# Sandboxed directories
BASE_WORKSPACE = r"c:\Users\HP\Desktop\capstone project"
DATA_DIR = os.path.join(BASE_WORKSPACE, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
DB_DIR = os.path.join(DATA_DIR, "db")

# Allowed extensions and size limits
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".ppt", ".pptx"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
MAX_INPUT_LENGTH = 5000  # Max chars in search/chat input

def ensure_sandbox_dirs():
    """Ensure that all sandboxed data directories exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)

def sanitize_input_text(text: str) -> str:
    """
    Sanitize text input by removing HTML tags and escaping special characters
    to prevent XSS and command injections. Truncates length.
    """
    if not text:
        return ""
    
    # Trim and truncate
    text = text.strip()[:MAX_INPUT_LENGTH]
    
    # Strip HTML tags
    clean_text = re.sub(r'<[^>]*>', '', text)
    
    # Escape HTML special characters
    return html.escape(clean_text)

def is_safe_path(path: str, base_dir: str) -> bool:
    """
    Validate that a resolved path resides strictly within the allowed base directory.
    Prevents path traversal attacks.
    """
    try:
        resolved_base = os.path.abspath(base_dir)
        resolved_target = os.path.abspath(path)
        
        # Check if target starts with base directory path
        return os.path.commonpath([resolved_base]) == os.path.commonpath([resolved_base, resolved_target])
    except Exception:
        return False

def validate_uploaded_file(filename: str, content: bytes) -> Tuple[bool, str]:
    """
    Validate an uploaded file's name, extension, size, and content.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "File name is empty."
        
    # Prevent path traversal in filename
    safe_filename = os.path.basename(filename)
    if safe_filename != filename:
        return False, "Invalid characters in file name (path traversal attempted)."
        
    # Safe path validation
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    if not is_safe_path(file_path, UPLOAD_DIR):
        return False, "Filename violates sandbox restrictions (path traversal attempted)."
        
    # Validate extension
    _, ext = os.path.splitext(safe_filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File is too large. Max allowed size is {MAX_FILE_SIZE / (1024*1024):.1f}MB."
        
    # Run text/XSS validations only on plain text/markdown files
    if ext in [".txt", ".md"]:
        if b'\x00' in content:
            return False, "Uploaded file appears to be a binary file. Only text/markdown files are allowed."
            
        # UTF-8 Decoding Check
        try:
            decoded_text = content.decode("utf-8")
        except UnicodeDecodeError:
            return False, "Uploaded file contains invalid character encoding. Only valid UTF-8 text files are allowed."
            
        # XSS Script & HTML Injection checks
        xss_patterns = [
            r"<script\b[^>]*>",
            r"javascript\s*:",
            r"\bon(?:click|load|mouseover|onerror)\s*=",
            r"<iframe\b[^>]*>",
            r"<object\b[^>]*>",
            r"<embed\b[^>]*>"
        ]
        for pattern in xss_patterns:
            if re.search(pattern, decoded_text, re.IGNORECASE):
                return False, "Uploaded file contains unsafe HTML/script execution payloads (potential XSS)."
            
    return True, "File is valid."

def validate_topic(topic: str) -> Tuple[bool, str]:
    """
    Validates study plan / quiz topic inputs.
    Must be non-empty, between 1 and 100 characters, and contain only safe characters.
    """
    if not topic or not topic.strip():
        return False, "Topic cannot be empty."
        
    topic_len = len(topic)
    if topic_len > 100:
        return False, f"Topic is too long (max 100 characters, got {topic_len})."
        
    # Check for safe characters: alphanumeric, spaces, and safe math/programming symbols: #, +, -, ., /, (, ), _, &, ,, :, ', "
    if not re.match(r"^[a-zA-Z0-9\s#\+\-\.\/\(\)_&,:\'\"?!]+$", topic):
        return False, "Topic contains invalid characters. Only alphanumeric, spaces, and symbols (+, #, -, ., /, _, &, ,, :, ', \", parentheses, ?, !) are allowed."
        
    return True, ""


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Scans the query for common prompt injection/jailbreak keyword patterns.
    Returns (is_injected, error_message).
    """
    if not text:
        return False, ""
        
    injection_patterns = [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
        r"system\s+override",
        r"bypass\s+(?:all\s+)?safety",
        r"forget\s+(?:all\s+)?(?:previous\s+)?instructions",
        r"forget\s+what\s+you\s+were\s+told",
        r"you\s+must\s+now\s+act\s+as",
        r"acting\s+as\s+a\s+jailbroken",
        r"ignore\s+(?:any\s+)?system\s+rules",
        r"jailbreak\s+helper",
        r"developer\s+mode\s+override",
        r"do\s+not\s+follow\s+instructions",
        r"dan\s+mode"
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True, "Potential prompt injection or safety bypass attempt detected."
            
    return False, ""

def sanitize_api_error(error_msg: str) -> str:
    """
    Redacts sensitive details (like API keys, absolute paths, database internals)
    from error messages before exposing them to users or standard logs.
    """
    if not error_msg:
        return ""
        
    # Redact potential Gemini/Google API keys
    redacted = re.sub(r'\b[a-zA-Z0-9_\-]{35,45}\b', '[REDACTED_API_KEY]', error_msg)
    
    # Redact internal file paths (Windows/Linux style)
    redacted = re.sub(r'[a-zA-Z]:\\[\w\s\\._\-]+', '[FILE_PATH]', redacted)
    redacted = re.sub(r'/[a-zA-Z0-9._\-]+(?:/[a-zA-Z0-9._\-]+)+', '[FILE_PATH]', redacted)
    
    return redacted


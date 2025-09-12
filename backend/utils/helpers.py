"""
Utility functions for the CountryCompare application.
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from functools import wraps
import time

logger = logging.getLogger(__name__)


def format_number(num: Union[int, float], precision: int = 2) -> str:
    """Format numbers with appropriate suffixes (K, M, B, T)."""
    if num is None:
        return "N/A"
    
    try:
        num = float(num)
        
        if num >= 1_000_000_000_000:
            return f"{num/1_000_000_000_000:.{precision}f}T"
        elif num >= 1_000_000_000:
            return f"{num/1_000_000_000:.{precision}f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.{precision}f}M"
        elif num >= 1_000:
            return f"{num/1_000:.{precision}f}K"
        else:
            return f"{num:.{precision}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(amount: Union[int, float], currency_symbol: str = "$") -> str:
    """Format currency amounts."""
    if amount is None:
        return "N/A"
    
    try:
        amount = float(amount)
        formatted_num = format_number(amount)
        return f"{currency_symbol}{formatted_num}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: Union[int, float], precision: int = 1) -> str:
    """Format percentage values."""
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        return f"{value:.{precision}f}%"
    except (ValueError, TypeError):
        return "N/A"


def calculate_percentage_change(old_value: Union[int, float], new_value: Union[int, float]) -> float:
    """Calculate percentage change between two values."""
    try:
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def normalize_text(text: str) -> str:
    """Normalize text by removing special characters and converting to lowercase."""
    if not text:
        return ""
    
    import re
    # Remove special characters and convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', text.lower())
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def generate_hash(data: str) -> str:
    """Generate MD5 hash for data."""
    return hashlib.md5(data.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_country_code(code: str) -> bool:
    """Validate country code format (2-3 characters)."""
    if not code:
        return False
    return len(code) in [2, 3] and code.isalpha()


def convert_temperature(celsius: float, to_fahrenheit: bool = True) -> float:
    """Convert temperature between Celsius and Fahrenheit."""
    try:
        if to_fahrenheit:
            return (celsius * 9/5) + 32
        else:
            return (celsius - 32) * 5/9
    except (ValueError, TypeError):
        return 0.0


def convert_distance(km: float, to_miles: bool = True) -> float:
    """Convert distance between kilometers and miles."""
    try:
        if to_miles:
            return km * 0.621371
        else:
            return km / 0.621371
    except (ValueError, TypeError):
        return 0.0


def convert_weight(kg: float, to_pounds: bool = True) -> float:
    """Convert weight between kilograms and pounds."""
    try:
        if to_pounds:
            return kg * 2.20462
        else:
            return kg / 2.20462
    except (ValueError, TypeError):
        return 0.0


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (OSError, ValueError):
        return 0.0


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    import re
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    import re
    pattern = r'https?://([^/]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else ""


def safe_json_loads(json_string: str) -> Optional[Any]:
    """Safely parse JSON string."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """Safely convert data to JSON string."""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "{}"


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def is_timestamp_recent(timestamp_str: str, hours: int = 24) -> bool:
    """Check if timestamp is within specified hours."""
    timestamp = parse_timestamp(timestamp_str)
    if not timestamp:
        return False
    
    now = datetime.utcnow()
    time_diff = now - timestamp
    return time_diff <= timedelta(hours=hours)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def measure_execution_time(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    import re
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower()


def is_image_file(filename: str) -> bool:
    """Check if file is an image based on extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    extension = get_file_extension(filename)
    return extension in image_extensions


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Flatten nested list."""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def deep_merge_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def get_nested_value(data: Dict[Any, Any], keys: List[str], default: Any = None) -> Any:
    """Get nested value from dictionary using list of keys."""
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict[Any, Any], keys: List[str], value: Any) -> None:
    """Set nested value in dictionary using list of keys."""
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = value


class DataValidator:
    """Data validation utility class."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float, max_val: float) -> bool:
        """Validate that numeric value is within range."""
        try:
            return min_val <= float(value) <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validate string length."""
        if not isinstance(text, str):
            return False
        
        if max_length is None:
            return len(text) >= min_length
        
        return min_length <= len(text) <= max_length
    
    @staticmethod
    def validate_list_length(lst: List[Any], min_length: int = 0, max_length: int = None) -> bool:
        """Validate list length."""
        if not isinstance(lst, list):
            return False
        
        if max_length is None:
            return len(lst) >= min_length
        
        return min_length <= len(lst) <= max_length

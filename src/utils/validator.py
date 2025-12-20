from typing import Any, Dict
import logging
import re


class Validator:
    def __init__(self):
        pass

    def validate_user_id(self, user_id: Any) -> bool:
        """
        Validates that the user ID is a positive integer.

        Args:
            user_id: The user ID to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        logging.debug(f"Validating user ID: {user_id}")
        return isinstance(user_id, int) and user_id > 0

    def validate_string(
        self, value: Any, min_length: int = 1, max_length: int = 255
    ) -> bool:
        """
        Validates a string's length and content against a safe pattern.

        Allowed characters: Alphanumeric, whitespace, -, ., ,, !, ?

        Args:
            value: The string to validate.
            min_length: Minimum allowed length.
            max_length: Maximum allowed length.

        Returns:
            bool: True if the string is valid, False otherwise.
        """
        logging.debug(f"Validating string: {value}")
        if not isinstance(value, str):
            return False

        if not (min_length <= len(value) <= max_length):
            return False

        return bool(re.match(r"^[\w\s\-.,!?]+$", value))

    def validate_number(
        self, value: Any, min_value: float = 0, max_value: float = 9999999
    ) -> bool:
        """
        Validates that a value is a number within a specified range.

        Args:
            value: The value to check.
            min_value: The minimum allowed value.
            max_value: The maximum allowed value.

        Returns:
            bool: True if the value is a number within range, False otherwise.
        """
        logging.debug(f"Validating number: {value}")
        try:
            num = float(value)
            return min_value <= num <= max_value
        except (ValueError, TypeError):
            return False

    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes input dictionary values.

        Strings are stripped of whitespace.
        Numbers and None are preserved.
        Other types are converted to string and stripped.

        Args:
            data: The dictionary to sanitize.

        Returns:
            Dict[str, Any]: A new dictionary with sanitized values.
        """
        logging.debug(f"Sanitizing input: {data}")
        sanitized = {}
        for key, value in data.items():
            if value is None or isinstance(value, (int, float)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value).strip()
        return sanitized

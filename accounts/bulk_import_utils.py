"""
Utility functions for bulk user import from CSV
"""
import csv
import io
from typing import List, Dict, Tuple
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User


def parse_csv(csv_file) -> Tuple[List[Dict], List[str]]:
    """
    Parse CSV file and return list of user data dictionaries
    
    Args:
        csv_file: Uploaded CSV file object
        
    Returns:
        Tuple of (parsed_data, errors)
        - parsed_data: List of dictionaries with user data
        - errors: List of error messages
    """
    errors = []
    parsed_data = []
    
    try:
        # Read file content
        file_content = csv_file.read()
        
        # Try to decode with different encodings
        try:
            content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = file_content.decode('utf-8-sig')  # Handle BOM
            except UnicodeDecodeError:
                try:
                    content = file_content.decode('latin-1')
                except UnicodeDecodeError:
                    errors.append("Unable to decode file. Please ensure it's a valid CSV file with UTF-8 encoding.")
                    return [], errors
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # Validate headers
        required_headers = {'username', 'full_name', 'email', 'password'}
        headers = set(csv_reader.fieldnames or [])
        
        missing_headers = required_headers - headers
        if missing_headers:
            errors.append(f"Missing required columns: {', '.join(missing_headers)}")
            return [], errors
        
        # Parse rows
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            # Skip empty rows
            if not any(row.values()):
                continue
            
            # Clean data
            user_data = {
                'row_number': row_num,
                'username': row.get('username', '').strip(),
                'full_name': row.get('full_name', '').strip(),
                'email': row.get('email', '').strip(),
                'password': row.get('password', '').strip(),
            }
            
            parsed_data.append(user_data)
        
        if not parsed_data:
            errors.append("CSV file is empty or contains no valid data rows.")
        
    except csv.Error as e:
        errors.append(f"CSV parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Unexpected error while parsing CSV: {str(e)}")
    
    return parsed_data, errors


def validate_csv_data(parsed_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate parsed CSV data
    
    Args:
        parsed_data: List of user data dictionaries from parse_csv()
        
    Returns:
        Tuple of (valid_rows, invalid_rows)
        - valid_rows: List of valid user data
        - invalid_rows: List of dicts with row data and error messages
    """
    valid_rows = []
    invalid_rows = []
    
    # Track usernames and emails to detect duplicates within the CSV
    seen_usernames = set()
    seen_emails = set()
    
    # Get existing usernames and emails from database
    existing_usernames = set(User.objects.values_list('username', flat=True))
    existing_emails = set(User.objects.values_list('email', flat=True))
    
    for user_data in parsed_data:
        errors = []
        row_num = user_data['row_number']
        
        # Validate username
        username = user_data['username']
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        elif not username.replace('_', '').isalnum():
            errors.append("Username can only contain letters, numbers, and underscores")
        elif username in existing_usernames:
            errors.append(f"Username '{username}' already exists in database")
        elif username in seen_usernames:
            errors.append(f"Duplicate username '{username}' in CSV file")
        else:
            seen_usernames.add(username)
        
        # Validate full_name
        full_name = user_data['full_name']
        if not full_name:
            errors.append("Full name is required")
        elif len(full_name) < 3:
            errors.append("Full name must be at least 3 characters")
        
        # Validate email
        email = user_data['email']
        if not email:
            errors.append("Email is required")
        else:
            try:
                validate_email(email)
                if email in existing_emails:
                    errors.append(f"Email '{email}' already exists in database")
                elif email in seen_emails:
                    errors.append(f"Duplicate email '{email}' in CSV file")
                else:
                    seen_emails.add(email)
            except ValidationError:
                errors.append(f"Invalid email format: '{email}'")
        
        # Validate password
        password = user_data['password']
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        # Categorize row
        if errors:
            invalid_rows.append({
                'row_number': row_num,
                'data': user_data,
                'errors': errors
            })
        else:
            valid_rows.append(user_data)
    
    return valid_rows, invalid_rows


def create_users_bulk(valid_data: List[Dict]) -> Tuple[int, List[str]]:
    """
    Create users in bulk from validated data
    
    Args:
        valid_data: List of validated user data dictionaries
        
    Returns:
        Tuple of (success_count, created_usernames)
        - success_count: Number of users successfully created
        - created_usernames: List of created usernames with their passwords
    """
    success_count = 0
    created_users = []
    
    for user_data in valid_data:
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                full_name=user_data['full_name'],
                role=User.Role.SALES,
                force_password_change=True  # Force password change on first login
            )
            success_count += 1
            created_users.append({
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'password': user_data['password']  # Store for summary
            })
        except Exception as e:
            # This shouldn't happen if validation was done correctly
            # But handle it gracefully
            print(f"Error creating user {user_data['username']}: {str(e)}")
    
    return success_count, created_users

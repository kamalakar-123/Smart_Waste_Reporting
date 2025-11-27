"""
Admin Configuration
List of Gmail IDs that should have admin access
"""

# Admin email addresses - only these users will have admin role
ADMIN_EMAILS = [
    'krishnakattimanimb@gmail.com',
    'kamalakaramarathi13@gmail.com',
    'dayanandaks045@gmail.com',
    'darshan99806@gmail.com'
]

def is_admin_email(email):
    """
    Check if an email address is in the admin list
    
    Args:
        email (str): Email address to check
        
    Returns:
        bool: True if email is an admin, False otherwise
    """
    if not email:
        return False
    return email.lower().strip() in [admin.lower() for admin in ADMIN_EMAILS]

def get_user_role(email):
    """
    Determine user role based on email
    
    Args:
        email (str): Email address to check
        
    Returns:
        str: 'admin' if email is in admin list, 'user' otherwise
    """
    return 'admin' if is_admin_email(email) else 'user'

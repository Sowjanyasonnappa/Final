"""
Role-based access control utilities
"""
from fastapi import HTTPException


def admin_only(current_user):
    """Check if user is admin"""
    if not current_user or current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")
    return current_user


def user_or_admin(current_user):
    """Check if user is authenticated"""
    if not current_user:
        raise HTTPException(status_code=403, detail="Access denied. Authentication required.")
    return current_user

# routes/admin_guard.py
from functools import wraps
from flask import session, redirect

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_login"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return wrapper

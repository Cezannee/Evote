# routes/admin_auth_routes.py
from flask import Blueprint, render_template, request, redirect, session
from models.admin import Admin
from extensions import db

admin_auth_bp = Blueprint("admin_auth_bp", __name__)

@admin_auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_login"):
        return redirect("/admin")

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            error = "Username dan password wajib diisi"
            return render_template("admin_login.html", error=error)

        admin = Admin.query.filter_by(username=username, password=password).first()
        if not admin:
            error = "Username atau password salah"
            return render_template("admin_login.html", error=error)

        session["admin_login"] = True
        session["admin_id"] = admin.id
        session["admin_username"] = admin.username
        session.modified = True
        return redirect("/admin")

    return render_template("admin_login.html", error=error)

from flask import Blueprint, render_template, request, redirect, session, jsonify
from services.user_service import UserService

auth_bp = Blueprint("auth_bp", __name__)
user_service = UserService()


# ================================
# LOGIN HTML (opsional)
# ================================
@auth_bp.route("/login")
def login_page():
    return render_template("login.html")


# ================================
# LOGIN API DIPAKAI FRONTEND JS
# ================================
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    nis = data.get("nis")
    if not nis:
        return jsonify({"status": "error", "message": "NIS harus diisi"}), 400

    # Ambil user dari database
    user = user_service.get_user_by_nis(nis)
    if not user:
        return jsonify({"status": "error", "message": "NIS tidak ditemukan"}), 404

    if user.has_voted:
        return jsonify({"status": "error", "message": "Anda sudah voting"}), 403

    # Simpan session
    session["nis"] = nis

    return jsonify({
        "status": "success",
        "message": "Login berhasil",
        "user": {
            "nis": user.nis,
            "name": user.name,
            "class_name": user.class_name
        }
    })


# ================================
# LOGOUT
# ================================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

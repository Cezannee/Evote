# routes/admin_routes.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.voter import Voter
from models.candidate import Candidate
from models.vote import Vote
from models.admin import Admin
from routes.admin_guard import admin_required
from services.pdf_generator import PDFGenerator

admin_bp = Blueprint("admin_bp", __name__)
pdf_gen = PDFGenerator()

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

def allowed_filename(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# IMPORT SISWA (Excel)
@admin_bp.route("/admin/upload_students", methods=["POST"])
@admin_required
def upload_students():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    rows = data.get("students") or []
    inserted = 0

    for r in rows:
        try:
            nis = str(r[0]).strip()
            nama = str(r[1]).strip()
            kelas = str(r[2]).strip() if len(r) > 2 else ""

            if not nis or not nama:
                continue

            exists = Voter.query.filter_by(nis=nis).first()
            if exists:
                continue

            v = Voter(
                nis=nis,
                name=nama,
                class_name=kelas,
                password_hash="12345",
                has_voted=False
            )

            db.session.add(v)
            inserted += 1

        except Exception:
            continue

    db.session.commit()
    return jsonify({"status":"ok","inserted":inserted})

# DATA PESERTA (pagination + search)
@admin_bp.route("/admin/voters", methods=["GET"])
@admin_required
def list_voters():
    page = int(request.args.get("page", 1))
    search = request.args.get("search", "")

    q = Voter.query

    if search:
        like = f"%{search}%"
        q = q.filter(
            (Voter.nis.like(like)) |
            (Voter.name.like(like)) |
            (Voter.class_name.like(like))
        )

    total = q.count()
    per_page = 30
    voters = q.order_by(Voter.id).offset((page-1)*per_page).limit(per_page).all()

    return jsonify({
        "page": page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page,
        "items": [v.to_dict() for v in voters]
    })

# KANDIDAT — GET
@admin_bp.route("/admin/candidates", methods=["GET"])
@admin_required
def get_candidates():
    cand = Candidate.query.order_by(Candidate.nomor).all()
    out = []
    for c in cand:
        out.append({
            "id": c.id,
            "nomor": c.nomor,
            "ketua": c.ketua,
            "wakil": c.wakil,
            "visi": c.visi,
            "misi": c.misi,
            "photo": c.photo
        })
    return jsonify(out)

# KANDIDAT — ADD
@admin_bp.route("/admin/add_candidate", methods=["POST"])
@admin_required
def add_candidate():
    nomor = request.form.get("nomor")
    ketua = request.form.get("ketua")
    wakil = request.form.get("wakil")
    visi = request.form.get("visi", "")
    misi = request.form.get("misi", "")

    photo = request.files.get("photo")
    if not photo or not allowed_filename(photo.filename):
        return jsonify({"status":"error","message":"Foto kandidat wajib"}), 400

    filename = secure_filename(photo.filename)
    filename = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    photo.save(save_path)

    c = Candidate(
        nomor=nomor,
        ketua=ketua,
        wakil=wakil,
        visi=visi,
        misi=misi,
        photo=filename
    )

    db.session.add(c)
    db.session.commit()
    return jsonify({"status":"ok","id":c.id})

# KANDIDAT — UPDATE
@admin_bp.route("/admin/update_candidate/<int:cand_id>", methods=["POST"])
@admin_required
def update_candidate(cand_id):
    c = Candidate.query.get_or_404(cand_id)

    nomor = request.form.get("nomor")
    ketua = request.form.get("ketua")
    wakil = request.form.get("wakil")
    visi = request.form.get("visi")
    misi = request.form.get("misi")

    if nomor: c.nomor = nomor
    if ketua: c.ketua = ketua
    if wakil: c.wakil = wakil
    if visi is not None: c.visi = visi
    if misi is not None: c.misi = misi

    photo = request.files.get("photo")
    if photo and allowed_filename(photo.filename):
        # hapus foto lama jika ada
        try:
            if c.photo:
                old_fp = os.path.join(current_app.config["UPLOAD_FOLDER"], c.photo)
                if os.path.exists(old_fp):
                    os.remove(old_fp)
        except Exception:
            pass

        filename = secure_filename(photo.filename)
        filename = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        photo.save(save_path)
        c.photo = filename

    db.session.commit()
    return jsonify({"status":"ok"})

# KANDIDAT — DELETE
@admin_bp.route("/admin/delete_candidate/<int:cand_id>", methods=["DELETE"])
@admin_required
def delete_candidate(cand_id):
    c = Candidate.query.get_or_404(cand_id)

    if c.photo:
        try:
            fp = os.path.join(current_app.config["UPLOAD_FOLDER"], c.photo)
            if os.path.exists(fp):
                os.remove(fp)
        except Exception:
            pass

    db.session.delete(c)
    db.session.commit()
    return jsonify({"status":"ok"})

# STATISTIK
@admin_bp.route("/admin/stats", methods=["GET"])
@admin_required
def stats():
    cand = Candidate.query.order_by(Candidate.nomor).all()
    out = []

    for c in cand:
        votes = Voter.query.filter_by(vote=c.id).count()
        out.append({
            "id": c.id,
            "nomor": c.nomor,
            "ketua": c.ketua,
            "wakil": c.wakil,
            "votes": votes
        })

    return jsonify(out)

# GENERATE PDF (grafik + golput)
@admin_bp.route("/admin/generate_report", methods=["GET"])
@admin_required
def generate_report():
    try:
        filepath = pdf_gen.generate_result_pdf()
        fname = os.path.basename(filepath)
        # file disajikan dari folder UPLOAD_FOLDER via route /candidate_photo/<file>
        return jsonify({"file": f"/candidate_photo/{fname}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RESET VOTES
@admin_bp.route("/admin/reset_votes", methods=["POST"])
@admin_required
def reset_votes():
    try:
        Vote.query.delete()
        Voter.query.update({Voter.has_voted: False})
        db.session.commit()
        return jsonify({"status":"ok"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status":"error","message":str(e)}), 500

# RESET PESERTA (hapus semua siswa)
@admin_bp.route("/admin/reset_voters", methods=["POST"])
@admin_required
def reset_voters():
    try:
        Vote.query.delete()
        Voter.query.delete()
        db.session.commit()
        return jsonify({"status":"ok","message":"Semua peserta dihapus"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status":"error","message":str(e)}), 500

from flask import Blueprint, render_template, request, redirect, jsonify
from models.candidate import Candidate
from models.voter import Voter
from extensions import db

vote_bp = Blueprint("vote_bp", __name__)   # NO url_prefix

# -------------------------
# Voting Page
# -------------------------
@vote_bp.route("/vote")
def vote_page():
    return render_template("voting.html")


# -------------------------
# Done Page
# -------------------------
@vote_bp.route("/done")
def done_page():
    return render_template("done.html")


# -------------------------
# API: Get candidates
# -------------------------
@vote_bp.route("/api/candidates")
def api_candidates():
    arr = []
    for c in Candidate.query.order_by(Candidate.nomor.asc()).all():
        arr.append(c.to_dict())
    return jsonify({"candidates": arr})


# -------------------------
# API: Submit Vote
# -------------------------
@vote_bp.route("/api/vote", methods=["POST"])
def submit_vote():
    data = request.json
    nis = data.get("nis")
    nomor = data.get("candidate_id")

    user = Voter.query.filter_by(nis=nis).first()
    if not user:
        return jsonify({"status": "error", "message": "User tidak ditemukan"})

    if user.has_voted:
        return jsonify({"status": "error", "message": "Anda sudah memilih!"})

    candidate = Candidate.query.filter_by(nomor=nomor).first()
    if not candidate:
        return jsonify({"status": "error", "message": "Kandidat tidak ditemukan"})

    user.vote = candidate.id
    user.has_voted = True
    db.session.commit()

    return jsonify({"status": "success", "message": "Berhasil memilih!"})

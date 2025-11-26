# routes/candidate_routes.py
from flask import Blueprint, request, jsonify
from services.candidate_service import CandidateService

candidate_bp = Blueprint("candidate_bp", __name__, url_prefix="/candidates")
candidate_service = CandidateService()

@candidate_bp.route("", methods=["GET"])
def get_candidates():
    cs = candidate_service.get_all_candidates()
    return jsonify([c.to_dict() for c in cs])

@candidate_bp.route("", methods=["POST"])
def add_candidate():
    name = request.form.get("name")
    kelas = request.form.get("classroom") or request.form.get("kelas")
    visi = request.form.get("vision") or request.form.get("visi")
    misi = request.form.get("mission") or request.form.get("misi")
    photo = request.files.get("photo")
    candidate_service.add_candidate(name, kelas, visi, misi, photo)
    return jsonify({"message":"Kandidat berhasil ditambahkan"})

@candidate_bp.route("/<int:id>", methods=["DELETE"])
def delete_candidate(id):
    candidate_service.delete_candidate(id)
    return jsonify({"message":"Kandidat dihapus"})

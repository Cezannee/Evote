import os
from extensions import db
from models.candidate import Candidate

UPLOAD_FOLDER = "uploads/candidates"

class CandidateService:

    def get_all_candidates(self):
        return Candidate.query.order_by(Candidate.nomor.asc()).all()

    def add_candidate(self, nomor, ketua, wakil, visi, misi, photo_file):
        filename = None
        if photo_file:
            filename = photo_file.filename
            path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(path)

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
        return c

    def update_candidate(self, cid, nomor, ketua, wakil, visi, misi, photo_file=None):
        c = Candidate.query.get(cid)
        if not c:
            return False

        c.nomor = nomor
        c.ketua = ketua
        c.wakil = wakil
        c.visi = visi
        c.misi = misi

        if photo_file:
            filename = photo_file.filename
            path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(path)
            c.photo = filename

        db.session.commit()
        return True

    def delete_candidate(self, cid):
        c = Candidate.query.get(cid)
        if not c:
            return False
        db.session.delete(c)
        db.session.commit()
        return True

# services/vote_service.py
from extensions import db
from models.vote import Vote
from models.voter import Voter
from models.candidate import Candidate

class VoteService:
    @staticmethod
    def has_voted_by_nis(nis):
        v = Voter.query.filter_by(nis=nis).first()
        if not v:
            return None
        return v.has_voted

    @staticmethod
    def submit_vote(nis, candidate_id):
        voter = Voter.query.filter_by(nis=nis).first()
        if not voter:
            return {"success": False, "message": "NIS tidak ditemukan"}
        if voter.has_voted:
            return {"success": False, "message": "Sudah voting"}

        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return {"success": False, "message": "Kandidat tidak ditemukan"}

        vote = Vote(voter_id=voter.id, candidate_id=candidate_id)
        db.session.add(vote)
        voter.has_voted = True
        db.session.commit()
        return {"success": True, "message": "Vote berhasil"}

    @staticmethod
    def get_counts():
        res = db.session.query(Vote.candidate_id, db.func.count(Vote.id)).group_by(Vote.candidate_id).all()
        return {r[0]: r[1] for r in res}

    @staticmethod
    def reset_all_votes():
        # Remove all votes and reset has_voted
        db.session.query(Vote).delete()
        Voter.query.update({Voter.has_voted: False})
        db.session.commit()
        return True

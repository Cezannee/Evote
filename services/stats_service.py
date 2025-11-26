from extensions import db
from models.candidate import Candidate
from models.voter import Voter

class StatsService:

    # -------------------------
    # Statistik Voting per Paslon
    # -------------------------
    def get_vote_stats(self):
        stats = []

        candidates = Candidate.query.order_by(Candidate.nomor.asc()).all()

        for c in candidates:
            count = Voter.query.filter_by(vote=c.id).count()

            stats.append({
                "nomor": c.nomor,
                "ketua": c.ketua,
                "wakil": c.wakil,
                "votes": count
            })

        return stats

    # -------------------------
    # Reset Semua Voting
    # -------------------------
    def reset_votes(self):
        voters = Voter.query.all()
        for v in voters:
            v.has_voted = False
            v.vote = None
        db.session.commit()

    # -------------------------
    # Statistik General (opsional)
    # -------------------------
    def summary(self):
        total = Voter.query.count()
        voted = Voter.query.filter_by(has_voted=True).count()
        not_voted = total - voted

        return {
            "total_voters": total,
            "voted": voted,
            "not_voted": not_voted,
            "rate": round((voted / total * 100) if total else 0, 2)
        }

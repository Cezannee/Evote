from models.voter import Voter
from extensions import db

class UserService:

    def get_user_by_nis(self, nis):
        return Voter.query.filter_by(nis=nis).first()

    def import_students(self, students):
        for s in students:
            nis, name, class_name = s
            exists = Voter.query.filter_by(nis=nis).first()
            if not exists:
                v = Voter(
                    nis=nis,
                    name=name,
                    class_name=class_name,
                    password_hash="12345"
                )
                db.session.add(v)
        db.session.commit()

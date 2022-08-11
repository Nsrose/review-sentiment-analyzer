from flask_sqlalchemy import SQLAlchemy

# When adding a new model DONT FORGET TO RUN:
# ipython
# from models import db
# db.create_all()
# 

db = SQLAlchemy()


class AirbnbComparisonSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Airbnb Comparison Session %s>' % self.id
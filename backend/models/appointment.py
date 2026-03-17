from datetime import datetime
from database import db

class Appointment(db.Model):
    """Appointment model representing a booked appointment"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    slot = db.relationship('Slot', backref='appointments')
    user = db.relationship('User', backref='appointments')

    def save(self):
        """Save the appointment to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the appointment from database"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'slot_id': self.slot_id,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}",
            'date': self.date.strftime('%Y-%m-%d'),
            'time': self.time,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

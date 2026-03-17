from database import db

class Slot(db.Model):
    """Slot model representing available appointment slots"""
    __tablename__ = 'slots'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)

    def save(self):
        """Save the slot to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the slot from database"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convert slot to dictionary"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'time': self.time,
            'capacity': self.capacity,
            'available': self.available,
            'is_full': self.available == 0
        }

    def book(self):
        """Book one appointment in this slot"""
        if self.available > 0:
            self.available -= 1
            db.session.commit()
            return True
        return False

    def cancel(self):
        """Cancel one appointment in this slot"""
        if self.available < self.capacity:
            self.available += 1
            db.session.commit()
            return True
        return False

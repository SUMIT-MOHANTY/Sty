from app import db
from datetime import datetime
from enum import Enum

class ApplicationStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"

class PassportApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(20), unique=True, nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    passport_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default=ApplicationStatus.SUBMITTED.value)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notes = db.Column(db.Text)

    # Relationships
    admin = db.relationship('User', backref='assigned_applications')

    def update_status(self, new_status):
        self.status = new_status
        self.last_updated = datetime.utcnow()

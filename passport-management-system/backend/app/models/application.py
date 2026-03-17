from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    application_type = Column(String)  # New, Renewal, etc.
    status = Column(String, default="Submitted")
    submission_date = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application")
    status_updates = relationship("StatusUpdate", back_populates="application")
    appointment = relationship("Appointment", back_populates="application", uselist=False)

from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship

from ..core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships
    time_slots = relationship("TimeSlot", back_populates="location")
    appointments = relationship("Appointment", back_populates="location")

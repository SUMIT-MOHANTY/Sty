from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.schemas.status_history import StatusHistoryCreate

class StatusHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_application_status_history(self, application_id: int) -> List[dict]:
        """
        Retrieve the complete status history for a specific application.
        """
        history = (
            self.db.query(ApplicationStatus)
            .filter(ApplicationStatus.application_id == application_id)
            .order_by(ApplicationStatus.timestamp.desc())
            .all()
        )

        # Check if application exists
        if not history and not self.db.query(Application).filter(Application.id == application_id).first():
            return []

        return history

    def get_status_updates(
        self, user_id: int, status: Optional[str] = None, limit: int = 10, skip: int = 0
    ) -> List[dict]:
        """
        Get recent status updates for applications associated with a user.
        Optionally filter by specific status.
        """
        query = (
            self.db.query(
                Application.id.label("application_id"),
                Application.company_name,
                Application.position_title,
                ApplicationStatus.status,
                ApplicationStatus.timestamp,
                ApplicationStatus.notes,
            )
            .join(ApplicationStatus, Application.id == ApplicationStatus.application_id)
            .filter(Application.user_id == user_id)
        )

        if status:
            query = query.filter(ApplicationStatus.status == status)

        updates = (
            query.order_by(ApplicationStatus.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [
            {
                "application_id": update.application_id,
                "company_name": update.company_name,
                "position_title": update.position_title,
                "status": update.status,
                "timestamp": update.timestamp,
                "notes": update.notes,
            }
            for update in updates
        ]

    def get_status_statistics(self, user_id: Optional[int] = None) -> dict:
        """
        Get statistics about application statuses.
        Optionally filter by user ID.
        """
        query = self.db.query(
            ApplicationStatus.status,
            func.count(ApplicationStatus.id).label("count"),
        )

        # Join with Application to filter by user_id if provided
        if user_id:
            query = query.join(
                Application, ApplicationStatus.application_id == Application.id
            ).filter(Application.user_id == user_id)

        # Group by status and get counts
        stats = query.group_by(ApplicationStatus.status).all()

        # Also get the total count
        total_query = self.db.query(func.count(ApplicationStatus.id))
        if user_id:
            total_query = total_query.join(
                Application, ApplicationStatus.application_id == Application.id
            ).filter(Application.user_id == user_id)
        total = total_query.scalar() or 0

        # Format the results
        result = {
            "total": total,
            "by_status": {item.status: item.count for item in stats},
        }

        return result

    def create_status_history(self, status_data: StatusHistoryCreate) -> ApplicationStatus:
        """
        Create a new status history entry for an application.
        """
        status = ApplicationStatus(
            application_id=status_data.application_id,
            status=status_data.status,
            notes=status_data.notes,
            created_by=status_data.created_by,
        )
        self.db.add(status)
        self.db.commit()
        self.db.refresh(status)
        return status

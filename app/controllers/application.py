from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.application import PassportApplication, ApplicationStatus
from app import db
from sqlalchemy import or_
from datetime import datetime

application_bp = Blueprint('application', __name__)

@application_bp.route('/')
@login_required
def list_applications():
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403

    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search_query = request.args.get('query', '')

    query = PassportApplication.query

    # Apply filters if provided
    if status_filter:
        query = query.filter(PassportApplication.status == status_filter)

    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                PassportApplication.application_number.like(search),
                PassportApplication.applicant_name.like(search),
                PassportApplication.email.like(search)
            )
        )

    # Sort by newest first
    applications = query.order_by(PassportApplication.submission_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('applications/list.html',
                         applications=applications,
                         statuses=ApplicationStatus,
                         current_status=status_filter,
                         search_query=search_query)

@application_bp.route('/<int:application_id>')
@login_required
def view_application(application_id):
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403

    application = PassportApplication.query.get_or_404(application_id)
    return render_template('applications/view.html',
                          application=application,
                          statuses=ApplicationStatus)

@application_bp.route('/<int:application_id>/update-status', methods=['POST'])
@login_required
def update_status(application_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    application = PassportApplication.query.get_or_404(application_id)

    new_status = request.form.get('status')
    notes = request.form.get('notes')

    # Validate the status
    try:
        valid_status = ApplicationStatus(new_status)
        application.status = valid_status.value

        if notes:
            if application.notes:
                application.notes += f"\n\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            else:
                application.notes = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"

        application.assigned_to = current_user.id
        db.session.commit()

        flash('Application status updated successfully!', 'success')
        return redirect(url_for('application.view_application', application_id=application_id))
    except ValueError:
        flash('Invalid status provided', 'danger')
        return redirect(url_for('application.view_application', application_id=application_id))

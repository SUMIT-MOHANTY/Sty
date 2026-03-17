from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403
    return render_template('index.html')

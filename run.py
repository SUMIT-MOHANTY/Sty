import os
from app import create_app, db
from app.models.user import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

@app.cli.command('create-admin')
def create_admin():
    """Create an admin user for testing."""
    admin = User(
        email='admin@example.com',
        first_name='Admin',
        last_name='User'
    )
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

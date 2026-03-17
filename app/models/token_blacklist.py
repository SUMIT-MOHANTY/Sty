from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime

db = SQLAlchemy()

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'revoked_at': self.revoked_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }

    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'

# Cleanup expired tokens periodically
def cleanup_expired_tokens():
    now = datetime.utcnow()
    TokenBlacklist.query.filter(TokenBlacklist.expires_at < now).delete()
    db.session.commit()

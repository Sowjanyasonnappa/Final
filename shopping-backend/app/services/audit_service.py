from sqlalchemy.orm import Session

from app.database.audit_log_model import AuditLog


def log_action(db: Session, user_id: int | None, action: str, details: str | None = None):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.flush()
    return log

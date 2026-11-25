from sqlalchemy.orm import Session

from app.infrastructure.database import check_database


def database_available(db: Session) -> bool:
    return check_database(db)
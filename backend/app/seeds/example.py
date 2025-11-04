from __future__ import annotations

from app.db.session import SessionLocal
from app.models.tables import CurationPolicy


def main() -> None:
    session = SessionLocal()
    try:
        if session.query(CurationPolicy).count() == 0:
            policy = CurationPolicy(name="Daily Mixed", description="Default policy", policy_json={"size": 50})
            session.add(policy)
            session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()

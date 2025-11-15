from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, full_name: str, email: str, password_hash: str):
    user = models.User(full_name=full_name, email=email, password_hash=password_hash)
    db.add(user); db.commit(); db.refresh(user)
    return user

def create_report(db: Session, report_in: schemas.ReportCreate):
    report = models.Report(
        fried_item=report_in.fried_item,
        lot_number=report_in.lot_number,
        date=report_in.date,
        start_time=report_in.start_time,
        end_time=report_in.end_time,
        total_fried=report_in.total_fried,
        goal=report_in.goal,
        oil_lot=report_in.oil_lot,
        comments=report_in.comments,
        team=report_in.team,
        leader_signature=report_in.leader_signature
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    # add cooling checks
    for cc in report_in.cooling_checks:
        row = models.CoolingCheck(
            report_id=report.id,
            time=cc.time,
            temperature=cc.temperature,
            personnel=cc.personnel,
            corrective_action=cc.corrective_action,
            verification_signature=cc.verification_signature
        )
        db.add(row)
    db.commit()
    db.refresh(report)
    return report

def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()

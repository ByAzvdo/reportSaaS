from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud, utils
from io import BytesIO
from fastapi.responses import StreamingResponse
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

router = APIRouter(prefix="/reports", tags=["reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-image", response_model=dict)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    # OCR
    text = utils.ocr_parser.ocr_image_bytes(content)
    parsed = utils.ocr_parser.parse_report_text(text)
    # Build report schema
    report_in = schemas.ReportCreate(**parsed)
    report = crud.create_report(db, report_in)
    return {"report_id": report.id}

@router.get("/{report_id}", response_model=schemas.ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = crud.get_report(db, report_id)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    # pydantic will handle relationships if you convert manually; simple dict:
    out = {
        "id": r.id,
        "fried_item": r.fried_item,
        "lot_number": r.lot_number,
        "date": r.date,
        "start_time": r.start_time,
        "end_time": r.end_time,
        "total_fried": r.total_fried,
        "goal": r.goal,
        "oil_lot": r.oil_lot,
        "comments": r.comments,
        "team": r.team,
        "leader_signature": r.leader_signature,
        "cooling_checks": [
            {
                "id": cc.id,
                "time": cc.time,
                "temperature": cc.temperature,
                "personnel": cc.personnel,
                "corrective_action": cc.corrective_action,
                "verification_signature": cc.verification_signature
            } for cc in r.cooling_checks
        ]
    }
    return out

@router.get("/{report_id}/excel")
def generate_excel(report_id: int, db: Session = Depends(get_db)):
    r = crud.get_report(db, report_id)
    if not r: raise HTTPException(status_code=404)
    # create workbook in memory
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Production Frying Report"
    # headers
    headers = ["id","fried_item","lot_number","date","start_time","end_time","total_fried","goal","oil_lot","comments","team","leader_signature"]
    ws1.append(headers)
    ws1.append([r.id, r.fried_item, r.lot_number, str(r.date), r.start_time, r.end_time, r.total_fried, r.goal, r.oil_lot, r.comments, r.team, r.leader_signature])
    # cooling checks
    ws2 = wb.create_sheet("CoolingChecks")
    ws2.append(["id","report_id","time","temperature","personnel","corrective_action","verification_signature"])
    for cc in r.cooling_checks:
        ws2.append([cc.id, r.id, cc.time, cc.temperature, cc.personnel, cc.corrective_action, cc.verification_signature])
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=report_{report_id}.xlsx"})

@router.get("/{report_id}/pdf")
def generate_pdf(report_id: int, db: Session = Depends(get_db)):
    r = crud.get_report(db, report_id)
    if not r: raise HTTPException(status_code=404)
    bio = BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    width, height = A4
    # Simple layout: you will improve to match exact design; here we place text with coordinates
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height-50, f"Production Frying Report - ID {r.id}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height-80, f"Fried Item: {r.fried_item}")
    c.drawString(50, height-100, f"LOT#: {r.lot_number}")
    # ... draw other fields
    y = height - 150
    c.drawString(50, y, "Cooling Checks:")
    y -= 20
    for cc in r.cooling_checks:
        c.drawString(60, y, f"{cc.time} | {cc.temperature} | {cc.personnel} | {cc.corrective_action}")
        y -= 18
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    bio.seek(0)
    return StreamingResponse(bio, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})

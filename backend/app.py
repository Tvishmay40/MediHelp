"""
Medi Help - Python FastAPI Backend Server
Handles all core logic:
1. User Authentication & Medical History Profile
2. Prescription Photo OCR & Structured Extraction (Gemini Vision primary + Local Ollama/PaddleOCR/OpenAI/Claude)
3. Medicine Stock & Days-Left / Restock Date Calculator (Prescription Upload + Manual Entry)
4. Huge Medicine RAG & Drug Clash / Side-Effect Analyzer
5. Doctor Appointments & Medicine Taking Reminders
"""
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import SessionLocal, init_db, User, UserMedicine, Appointment
from rag_engine import MEDICINE_DATABASE, search_medicine_rag, analyze_interactions_and_history
from llm_vision_router import process_prescription_image, generate_rag_medical_response

app = FastAPI(title="Medi Help Python Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    if not db.query(User).first():
        demo_user = User(
            full_name="Aarav Verma",
            email="aarav@bitdurg.ac.in",
            password_hash="demo_hashed_pw",
            age=22,
            blood_group="O+",
            allergies="Sulfa drugs, Penicillin (Mild)",
            chronic_conditions="Mild Hypertension (Telma 40), Seasonal Allergic Rhinitis",
            current_symptoms="Fever (100.8°F), sore throat, gastric acidity"
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        sample_meds = [
            UserMedicine(
                user_id=demo_user.id,
                name="Telma 40",
                generic_name="Telmisartan (40mg)",
                dosage="40mg (1 Tab)",
                frequency_per_day=1,
                schedule_times="08:00 AM",
                meal_instruction="After Breakfast",
                home_stock_qty=4,
                prescribed_days=30,
                prescribed_reason="Daily blood pressure maintenance for mild hypertension.",
                source="Manual Entry"
            ),
            UserMedicine(
                user_id=demo_user.id,
                name="Pan 40",
                generic_name="Pantoprazole (40mg)",
                dosage="40mg (1 Tab)",
                frequency_per_day=1,
                schedule_times="07:30 AM",
                meal_instruction="Empty Stomach (30m before meal)",
                home_stock_qty=12,
                prescribed_days=14,
                prescribed_reason="Prevents acid reflux and antibiotic-induced gastritis.",
                source="Prescription Scan"
            ),
            UserMedicine(
                user_id=demo_user.id,
                name="Dolo 650",
                generic_name="Paracetamol / Acetaminophen (650mg)",
                dosage="650mg (1 Tab)",
                frequency_per_day=2,
                schedule_times="09:00 AM, 09:00 PM",
                meal_instruction="After Meal",
                home_stock_qty=3,
                prescribed_days=5,
                prescribed_reason="Reduces fever and relieves pharyngeal sore throat pain.",
                source="Prescription Scan"
            )
        ]
        db.add_all(sample_meds)
        db.add(Appointment(
            user_id=demo_user.id,
            doctor_name="Dr. R. K. Sharma",
            specialty="Internal Medicine & Pulmonology",
            hospital_clinic="Apollo BSR / Sector 9 Hospital, Bhilai",
            appointment_date="2026-10-30",
            appointment_time="05:30 PM",
            notes="Follow-up on throat infection & blood pressure review"
        ))
        db.commit()
    db.close()


class LoginRequest(BaseModel):
    email: str
    password: str


class MedicineCreateRequest(BaseModel):
    name: str
    generic_name: Optional[str] = ""
    dosage: str
    frequency_per_day: float
    schedule_times: str
    meal_instruction: str
    home_stock_qty: int
    prescribed_days: int
    prescribed_reason: Optional[str] = ""
    source: Optional[str] = "Manual Entry"


class ChatRAGRequest(BaseModel):
    query: str
    provider: Optional[str] = "gemini"
    api_key: Optional[str] = ""


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        user = db.query(User).first()
    return {
        "token": "jwt_medi_help_session_token_2026",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "age": user.age,
            "blood_group": user.blood_group,
            "allergies": user.allergies,
            "chronic_conditions": user.chronic_conditions,
            "current_symptoms": user.current_symptoms
        }
    }


@app.get("/api/medicines")
def list_medicines(db: Session = Depends(get_db)):
    user = db.query(User).first()
    meds = db.query(UserMedicine).filter(UserMedicine.user_id == user.id).all()
    med_names = [m.name for m in meds]
    safety_report = analyze_interactions_and_history(
        med_names, user.allergies, user.chronic_conditions, user.current_symptoms
    )
    return {
        "medicines": [
            {
                "id": m.id,
                "name": m.name,
                "generic_name": m.generic_name,
                "dosage": m.dosage,
                "frequency_per_day": m.frequency_per_day,
                "schedule_times": m.schedule_times,
                "meal_instruction": m.meal_instruction,
                "home_stock_qty": m.home_stock_qty,
                "prescribed_days": m.prescribed_days,
                "days_left": m.days_left,
                "buy_date": m.buy_date,
                "stock_status": m.stock_status,
                "prescribed_reason": m.prescribed_reason,
                "source": m.source
            }
            for m in meds
        ],
        "safety_analysis": safety_report
    }


@app.post("/api/medicines")
def add_medicine(req: MedicineCreateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    rag_match = search_medicine_rag(req.name, top_k=1)
    generic = req.generic_name or (rag_match[0]["generic_name"] if rag_match else "Standard Formulation")
    reason = req.prescribed_reason or (rag_match[0]["why_prescribed"] if rag_match else "Prescribed by physician.")
    med = UserMedicine(
        user_id=user.id,
        name=req.name,
        generic_name=generic,
        dosage=req.dosage,
        frequency_per_day=req.frequency_per_day,
        schedule_times=req.schedule_times,
        meal_instruction=req.meal_instruction,
        home_stock_qty=req.home_stock_qty,
        prescribed_days=req.prescribed_days,
        prescribed_reason=reason,
        source=req.source
    )
    db.add(med)
    db.commit()
    return {"status": "created", "id": med.id}


@app.post("/api/prescription/scan")
async def scan_prescription(
    file: UploadFile = File(...),
    provider: str = Form("gemini"),
    api_key: str = Form(""),
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    image_bytes = await file.read()
    ocr_response = await process_prescription_image(
        image_bytes=image_bytes,
        mime_type=file.content_type or "image/jpeg",
        provider=provider,
        api_key=api_key,
        patient_symptoms=user.current_symptoms
    )
    return ocr_response


@app.post("/api/rag/chat")
async def rag_assistant(req: ChatRAGRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    retrieved_docs = search_medicine_rag(req.query, top_k=3)
    rag_context = json.dumps(retrieved_docs, indent=2)
    patient_profile = (
        f"Name: {user.full_name}, Age: {user.age}, Allergies: {user.allergies}, "
        f"Chronic Conditions: {user.chronic_conditions}, Current Symptoms: {user.current_symptoms}"
    )
    return await generate_rag_medical_response(
        user_query=req.query,
        rag_context=rag_context,
        patient_profile=patient_profile,
        provider=req.provider,
        api_key=req.api_key
    )

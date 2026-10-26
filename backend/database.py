"""
SQLite Database & SQLAlchemy Models for Medi Help:
- Users & Authentication Credentials
- Patient Medical History (Chronic conditions, allergies, past surgeries, symptoms)
- Active Medicines & Home Stock Tracker (auto-calculates days left & restock date)
- Medicine Taking Reminders
- Doctor Appointments
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medi_help.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    age = Column(Integer, default=28)
    blood_group = Column(String, default="O+")
    allergies = Column(Text, default="Sulfa drugs, Dust")
    chronic_conditions = Column(Text, default="Mild Hypertension, Seasonal Allergic Rhinitis")
    current_symptoms = Column(Text, default="Fever, sore throat, gastric acidity, mild headache")

    medicines = relationship("UserMedicine", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


class UserMedicine(Base):
    __tablename__ = "user_medicines"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    generic_name = Column(String, default="")
    dosage = Column(String, nullable=False)           # e.g., "500mg", "40mg"
    frequency_per_day = Column(Float, default=2.0)    # e.g., 2 times/day
    schedule_times = Column(String, default="08:00 AM, 08:00 PM")
    meal_instruction = Column(String, default="After Meal")
    home_stock_qty = Column(Integer, default=10)      # current tablets in home inventory
    prescribed_days = Column(Integer, default=5)
    prescribed_reason = Column(String, default="")
    source = Column(String, default="Prescription Scan")  # "Prescription Scan" or "Manual Entry"
    last_updated = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d"))

    user = relationship("User", back_populates="medicines")

    @property
    def days_left(self) -> float:
        if self.frequency_per_day <= 0:
            return 999.0
        return round(self.home_stock_qty / self.frequency_per_day, 1)

    @property
    def buy_date(self) -> str:
        # Recommend buying 1 day before stock runs out
        buffer_days = max(0, int(self.days_left) - 1)
        target_date = datetime.now() + timedelta(days=buffer_days)
        return target_date.strftime("%Y-%m-%d")

    @property
    def stock_status(self) -> str:
        if self.days_left <= 2:
            return "CRITICAL_RESTOCK"
        elif self.days_left <= 5:
            return "LOW_STOCK"
        return "OPTIMAL"


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doctor_name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    hospital_clinic = Column(String, default="Sector 9 Hospital, Bhilai")
    appointment_date = Column(String, nullable=False)
    appointment_time = Column(String, nullable=False)
    notes = Column(Text, default="")
    reminder_enabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="appointments")


def init_db():
    Base.metadata.create_all(bind=engine)

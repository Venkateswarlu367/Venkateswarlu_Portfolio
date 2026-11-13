import os
import secrets
import time
import smtplib

from email.message import EmailMessage

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr


# Create FastAPI application
app = FastAPI(title="Portfolio OTP Service")


# Allow your portfolio website to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# OTP is valid for 5 minutes
OTP_TTL = 300

# Temporary OTP storage
otp_store = {}


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetRequest(BaseModel):
    email: EmailStr
    new_password: str


def generate_otp():
    """Generate a random 4-digit OTP."""
    return f"{secrets.randbelow(10000):04d}"


def send_email(to_email, otp):
    """Send OTP through Gmail SMTP."""

    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    sender = os.getenv("SMTP_FROM", username)

    message = EmailMessage()

    message["Subject"] = "Your Portfolio Password Reset OTP"
    message["From"] = sender
    message["To"] = to_email

    message.set_content(
        f"""
Your 4-digit OTP is: {otp}

This OTP expires in 5 minutes.

If you did not request a password reset, please ignore this email.
"""
    )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


@app.get("/")
def home():
    return {
        "message": "Portfolio OTP server is running"
    }


@app.post("/auth/send-otp")
def send_otp(req: EmailRequest):

    email = str(req.email).lower()

    otp = generate_otp()

    otp_store[email] = {
        "otp": otp,
        "expires": time.time() + OTP_TTL,
        "verified": False
    }

    try:
        send_email(email, otp)

    except Exception as e:

        otp_store.pop(email, None)

        raise HTTPException(
            status_code=500,
            detail="Email could not be sent. Check SMTP settings."
        )

    return {
        "message": "OTP sent successfully"
    }


@app.post("/auth/verify-otp")
def verify_otp(req: VerifyRequest):

    email = str(req.email).lower()

    item = otp_store.get(email)

    if not item:
        raise HTTPException(
            status_code=400,
            detail="OTP not found. Request a new OTP."
        )

    if time.time() > item["expires"]:
        otp_store.pop(email, None)

        raise HTTPException(
            status_code=400,
            detail="OTP expired. Request a new OTP."
        )

    if not req.otp.isdigit() or len(req.otp) != 4:
        raise HTTPException(
            status_code=400,
            detail="OTP must contain exactly 4 digits."
        )

    if not secrets.compare_digest(req.otp, item["otp"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP."
        )

    item["verified"] = True

    return {
        "message": "OTP verified successfully"
    }


@app.post("/auth/reset-password")
def reset_password(req: ResetRequest):

    email = str(req.email).lower()

    item = otp_store.get(email)

    if not item:
        raise HTTPException(
            status_code=400,
            detail="OTP verification not found."
        )

    if not item.get("verified"):
        raise HTTPException(
            status_code=400,
            detail="Verify OTP before changing the password."
        )

    if time.time() > item["expires"]:
        otp_store.pop(email, None)

        raise HTTPException(
            status_code=400,
            detail="OTP expired. Request a new OTP."
        )

    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters."
        )

    otp_store.pop(email, None)

    return {
        "message": "Password reset authorized"
    }
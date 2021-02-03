from datetime import datetime

from sqlalchemy import func
from taxipassengers_backend.db import db


class PassengerModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authId = db.Column(db.Integer, unique=True)
    firstName = db.Column(db.String(250))
    lastName = db.Column(db.String(250))
    dateOfBirth = db.Column(db.String(250), nullable=True)
    email = db.Column(db.String(250), unique=True)
    phoneNumber = db.Column(db.String(250), unique=True)
    image = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Float, default=0.0)

    homeLocation = db.Column(db.String(250), nullable=True)
    homePickupTime = db.Column(db.String(250), nullable=True)
    workLocation = db.Column(db.String(250), nullable=True)
    workPickupTime = db.Column(db.String(250), nullable=True)
    paymentMethod = db.Column(db.String(250), nullable=True)

    emailStatus = db.Column(db.Integer, default=1)
    phoneNumberStatus = db.Column(db.Integer, default=0)

    suspendedAt = db.Column(db.DateTime, nullable=True)
    updateTimestamp = db.Column(db.DateTime, onupdate=datetime.now)
    timestamp = db.Column(db.DateTime, server_default=func.now())

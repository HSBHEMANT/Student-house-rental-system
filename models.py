from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'owner'
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    rent = db.Column(db.Float, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    facilities = db.Column(db.Text)  # JSON string
    images = db.Column(db.Text)      # JSON string
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ New field for QR code
    qr_code_path = db.Column(db.String(255), nullable=True)

    # Foreign key
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='property', lazy=True)

    def __repr__(self):
        return f'<Property {self.title}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'paid'
    notes = db.Column(db.Text)

    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

    def __repr__(self):
        return f'<Booking {self.id}>'

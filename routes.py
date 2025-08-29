import os
import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Property, Booking
from forms import LoginForm, RegistrationForm, PropertyForm, SearchForm, BookingForm

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):

    # ---------------- Home ----------------
    @app.route('/')
    def index():
        search_form = SearchForm()
        recent_properties = Property.query.filter_by(available=True).order_by(Property.created_at.desc()).limit(6).all()
        return render_template('index.html', form=search_form, properties=recent_properties)

    # ---------------- Auth ----------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Registration failed.', 'danger')
                app.logger.error(f'Registration error: {e}')
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    # ---------------- Dashboard ----------------
    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        form = SearchForm()
        search_results = []
        student_properties = []

        if current_user.role == 'owner':
            properties = Property.query.filter_by(owner_id=current_user.id).order_by(Property.created_at.desc()).all()
            bookings = Booking.query.join(Property).filter(Property.owner_id == current_user.id).all()
        else:
            properties = []
            bookings = Booking.query.filter_by(student_id=current_user.id).all()

            # Handle search submission
            if form.validate_on_submit():
                filters = [Property.available == True]
                if form.location.data:
                    filters.append(Property.location.ilike(f"%{form.location.data.strip()}%"))
                if form.room_type.data:
                    filters.append(Property.room_type == form.room_type.data)
                if form.min_rent.data:
                    filters.append(Property.rent >= form.min_rent.data)
                if form.max_rent.data:
                    filters.append(Property.rent <= form.max_rent.data)
                search_results = Property.query.filter(*filters).order_by(Property.created_at.desc()).all()

        return render_template(
            'dashboard.html',
            form=form,
            properties=properties,
            bookings=bookings,
            search_results=search_results,
            student_properties=student_properties
        )

    # ---------------- Add Property ----------------
    @app.route('/add_property', methods=['GET', 'POST'])
    @login_required
    def add_property():
        if current_user.role != 'owner':
            flash('Only owners can add properties.', 'danger')
            return redirect(url_for('dashboard'))
        form = PropertyForm()
        if form.validate_on_submit():
            image_filenames = []
            if form.images.data:
                for image in form.images.data:
                    if image and allowed_file(image.filename):
                        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secure_filename(image.filename)}"
                        upload_path = app.config['UPLOAD_FOLDER']
                        os.makedirs(upload_path, exist_ok=True)
                        image.save(os.path.join(upload_path, filename))
                        image_filenames.append(filename)
            facilities_list = []
            if form.facilities.data:
                facilities_list = [f.strip() for f in form.facilities.data.split('\n') if f.strip()]
            new_property = Property(
                title=form.title.data,
                description=form.description.data,
                location=form.location.data,
                rent=form.rent.data,
                room_type=form.room_type.data,
                facilities=json.dumps(facilities_list),
                images=json.dumps(image_filenames),
                owner_id=current_user.id
            )
            try:
                db.session.add(new_property)
                db.session.commit()
                flash('Property added!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Failed to add property.', 'danger')
                app.logger.error(f'Add property error: {e}')
        return render_template('add_property.html', form=form)

    # ---------------- Property Details ----------------
    @app.route('/property/<int:property_id>')
    def property_details(property_id):
        property_obj = Property.query.get_or_404(property_id)
        booking_form = BookingForm() if current_user.is_authenticated and current_user.role == 'student' else None
        facilities = json.loads(property_obj.facilities) if property_obj.facilities else []
        images = json.loads(property_obj.images) if property_obj.images else []
        return render_template(
            'property_details.html',
            property=property_obj,
            facilities=facilities,
            images=images,
            booking_form=booking_form
        )

    # ---------------- Upload QR ----------------
    @app.route('/upload_qr/<int:property_id>', methods=['GET', 'POST'])
    @login_required
    def upload_qr(property_id):
        property_obj = Property.query.get_or_404(property_id)
        if property_obj.owner_id != current_user.id:
            flash('Not allowed.', 'danger')
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            if 'qr_code' not in request.files or request.files['qr_code'].filename == '':
                flash('No file selected.', 'danger')
                return redirect(request.url)
            file = request.files['qr_code']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                property_obj.qr_code_path = filepath
                db.session.commit()
                flash('QR Code uploaded!', 'success')
                return redirect(url_for('dashboard'))
        return render_template('upload_qr.html', property=property_obj)

    # ---------------- Booking ----------------
    @app.route('/book_property/<int:property_id>', methods=['POST'])
    @login_required
    def book_property(property_id):
        if current_user.role != 'student':
            flash('Only students can book.', 'danger')
            return redirect(url_for('property_details', property_id=property_id))
        property_obj = Property.query.get_or_404(property_id)
        form = BookingForm()
        if form.validate_on_submit():
            days = (form.check_out_date.data - form.check_in_date.data).days
            total_amount = (days / 30) * property_obj.rent if days > 0 else property_obj.rent
            booking = Booking(
                check_in_date=form.check_in_date.data,
                check_out_date=form.check_out_date.data,
                total_amount=total_amount,
                notes=form.notes.data,
                student_id=current_user.id,
                property_id=property_id
            )
            try:
                db.session.add(booking)
                db.session.commit()
                flash("Booking created. Please pay using QR code.", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("Booking failed.", "danger")
                app.logger.error(f'Booking error: {e}')
        return redirect(url_for('property_details', property_id=property_id))

    # ---------------- Serve Uploaded Files ----------------
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ---------------- Delete Property ----------------
    @app.route('/delete_property/<int:property_id>', methods=['POST'])
    @login_required
    def delete_property(property_id):
        property_obj = Property.query.get_or_404(property_id)
        if property_obj.owner_id != current_user.id:
            flash("Not allowed", "danger")
            return redirect(url_for('dashboard'))
        db.session.delete(property_obj)
        db.session.commit()
        flash("Property deleted", "success")
        return redirect(url_for('dashboard'))

    # ---------------- Delete Booking ----------------
    @app.route('/delete_booking/<int:booking_id>', methods=['POST'])
    @login_required
    def delete_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)
        if (current_user.role == 'owner' and booking.property.owner_id == current_user.id) or \
           (current_user.role == 'student' and booking.student_id == current_user.id):
            db.session.delete(booking)
            db.session.commit()
            flash("Booking deleted", "success")
        else:
            flash("Not allowed", "danger")
        return redirect(url_for('dashboard'))

    # ---------------- Edit Property ----------------
    @app.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
    @login_required
    def edit_property(property_id):
        property_obj = Property.query.get_or_404(property_id)
        if property_obj.owner_id != current_user.id:
            flash("Not allowed", "danger")
            return redirect(url_for("dashboard"))

        form = PropertyForm(obj=property_obj)

        if form.validate_on_submit():
            property_obj.title = form.title.data
            property_obj.description = form.description.data
            property_obj.location = form.location.data
            property_obj.rent = form.rent.data
            property_obj.room_type = form.room_type.data

            facilities_list = []
            if form.facilities.data:
                facilities_list = [f.strip() for f in form.facilities.data.split("\n") if f.strip()]
            property_obj.facilities = json.dumps(facilities_list)

            if form.images.data:
                image_filenames = []
                for image in form.images.data:
                    if image and allowed_file(image.filename):
                        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secure_filename(image.filename)}"
                        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                        image.save(filepath)
                        image_filenames.append(filename)
                if image_filenames:
                    property_obj.images = json.dumps(image_filenames)

            try:
                db.session.commit()
                flash("Property updated successfully!", "success")
                return redirect(url_for("dashboard"))
            except Exception as e:
                db.session.rollback()
                flash("Error updating property.", "danger")
                app.logger.error(f"Edit property error: {e}")

        return render_template("add_property.html", form=form, edit_mode=True, property=property_obj)

# Student House Rental System

## Overview

The Student House Rental System is a full-stack web application built with Flask that connects students looking for housing with property owners. The platform facilitates property listings, searches, bookings, and payments through an intuitive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5, CSS3, Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **UI Components**: Responsive design with cards, modals, and forms
- **Icons**: Font Awesome for consistent iconography
- **Styling**: Custom CSS with CSS Grid for image galleries

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Authentication**: Flask-Login for user session management
- **Forms**: Flask-WTF with WTForms for form handling and validation
- **File Handling**: Werkzeug for secure file uploads
- **Architecture Pattern**: MVC (Model-View-Controller) with Blueprint-style routing

### Database Architecture
- **ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **Database**: Configured for PostgreSQL via environment variables
- **Models**: User, Property, and Booking entities with proper relationships
- **Schema**: Relational design with foreign keys and cascading deletes

## Key Components

### User Management
- **Authentication**: Username/password login with password hashing
- **User Roles**: Two-tier system (students and property owners)
- **Registration**: Email validation and unique username enforcement
- **Session Management**: Flask-Login handles user sessions and login requirements

### Property Management
- **Property Model**: Title, description, location, rent, room type, facilities
- **Image Upload**: Multiple file upload with validation (JPG, PNG, GIF)
- **Property Types**: Single room, shared room, studio, full apartment
- **Availability Tracking**: Boolean flag for property availability

### Search and Filtering
- **Search Form**: Location, rent range, and room type filters
- **Query System**: SQLAlchemy filters for property searches
- **Results Display**: Grid layout with property cards

### Booking System
- **Booking Model**: Links students to properties with dates and amounts
- **Status Tracking**: Pending, paid, cancelled booking states
- **Payment Integration**: Stripe checkout sessions for payment processing

### File Management
- **Upload Directory**: Static/uploads folder for property images
- **File Validation**: Extension and size limits (16MB max)
- **Secure Filenames**: Werkzeug secure_filename utility

## Data Flow

### Property Listing Flow
1. Property owner logs in and accesses dashboard
2. Owner fills out property form with details and images
3. Form validation ensures data integrity
4. Files are uploaded to static/uploads directory
5. Property is saved to database with owner relationship

### Booking Flow
1. Student searches and finds desired property
2. Student fills out booking form with dates
3. System calculates total amount based on dates and rent
4. Stripe checkout session is created for payment
5. Upon successful payment, booking status updates to 'paid'

### Search Flow
1. User submits search form with filters
2. Backend builds SQLAlchemy query with filter conditions
3. Results are fetched and passed to template
4. Frontend displays results in responsive grid layout

## External Dependencies

### Payment Processing
- **Stripe**: Handles payment processing and checkout sessions
- **Configuration**: Uses STRIPE_SECRET_KEY environment variable
- **Webhooks**: Checkout session completion updates booking status

### File Storage
- **Local Storage**: Files stored in static/uploads directory
- **Serving**: Flask serves uploaded files through URL routes
- **Security**: File extension validation and secure filename generation

### Environment Configuration
- **Database**: DATABASE_URL environment variable for database connection
- **Security**: SESSION_SECRET for Flask session encryption
- **Deployment**: REPLIT_DEPLOYMENT and REPLIT_DEV_DOMAIN for domain detection

## Deployment Strategy

### Environment Variables
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session encryption key
- `STRIPE_SECRET_KEY`: Stripe API key for payments
- `REPLIT_DEPLOYMENT`: Deployment environment flag
- `REPLIT_DEV_DOMAIN`: Domain for Stripe redirects

### Database Configuration
- **Connection Pooling**: Pool recycle every 300 seconds with pre-ping
- **Migrations**: SQLAlchemy table creation on app startup
- **Error Handling**: Pool pre-ping prevents disconnection issues

### File Upload Configuration
- **Upload Folder**: Configured as 'static/uploads'
- **Size Limit**: 16MB maximum file size
- **Security**: Allowed extensions and secure filename handling

### Production Considerations
- **Proxy Configuration**: ProxyFix middleware for reverse proxy setup
- **Logging**: Debug-level logging configured
- **Security**: Password hashing with Werkzeug security utilities
- **Static Files**: Flask serves uploaded files with proper routing
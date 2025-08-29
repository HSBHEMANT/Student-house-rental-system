// Main JavaScript functionality for the Student House Rental System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Image gallery modal functionality
    initializeImageGallery();
    
    // File upload enhancement
    initializeFileUpload();
    
    // Search form enhancement
    initializeSearchForm();
    
    // Form validation enhancement
    initializeFormValidation();
    
    // Auto-hide flash messages
    initializeFlashMessages();
});

function initializeImageGallery() {
    const galleryImages = document.querySelectorAll('.gallery-image');
    
    galleryImages.forEach(image => {
        image.addEventListener('click', function() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Property Image</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="₹{this.src}" class="img-fluid" alt="Property Image">
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            
            // Remove modal from DOM when hidden
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        });
    });
}

function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const wrapper = input.closest('.file-upload-wrapper');
        if (!wrapper) return;
        
        const display = wrapper.querySelector('.file-upload-display');
        if (!display) return;
        
        // Drag and drop functionality
        display.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        display.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        display.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            input.files = files;
            updateFileDisplayText(display, files);
        });
        
        // File selection change
        input.addEventListener('change', function() {
            updateFileDisplayText(display, this.files);
        });
    });
}

function updateFileDisplayText(display, files) {
    const textElement = display.querySelector('p') || display;
    
    if (files.length > 0) {
        const fileNames = Array.from(files).map(file => file.name);
        textElement.innerHTML = `
            <i class="fas fa-check-circle text-success"></i><br>
            <strong>₹{files.length} file(s) selected:</strong><br>
            <small>₹{fileNames.join(', ')}</small>
        `;
    } else {
        textElement.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i><br>
            <strong>Click to upload images</strong><br>
            <small>or drag and drop files here</small>
        `;
    }
}

function initializeSearchForm() {
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return;
    
    const locationInput = document.getElementById('location');
    const minRentInput = document.getElementById('min_rent');
    const maxRentInput = document.getElementById('max_rent');
    
    // Real-time validation
    if (minRentInput && maxRentInput) {
        function validateRentRange() {
            const minRent = parseFloat(minRentInput.value) || 0;
            const maxRent = parseFloat(maxRentInput.value) || Infinity;
            
            if (minRent > maxRent) {
                maxRentInput.setCustomValidity('Maximum rent must be greater than minimum rent');
            } else {
                maxRentInput.setCustomValidity('');
            }
        }
        
        minRentInput.addEventListener('input', validateRentRange);
        maxRentInput.addEventListener('input', validateRentRange);
    }
    
    // Auto-submit on Enter key
    if (locationInput) {
        locationInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchForm.submit();
            }
        });
    }
}

function initializeFormValidation() {
    // Custom validation for booking form
    const bookingForm = document.getElementById('booking-form');
    if (!bookingForm) return;
    
    const checkInDate = document.getElementById('check_in_date');
    const checkOutDate = document.getElementById('check_out_date');
    
    if (checkInDate && checkOutDate) {
        function validateDates() {
            const checkIn = new Date(checkInDate.value);
            const checkOut = new Date(checkOutDate.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            // Check-in date should not be in the past
            if (checkIn < today) {
                checkInDate.setCustomValidity('Check-in date cannot be in the past');
            } else {
                checkInDate.setCustomValidity('');
            }
            
            // Check-out date should be after check-in
            if (checkOut <= checkIn) {
                checkOutDate.setCustomValidity('Check-out date must be after check-in date');
            } else {
                checkOutDate.setCustomValidity('');
            }
            
            // Update total amount calculation
            updateBookingSummary(checkIn, checkOut);
        }
        
        checkInDate.addEventListener('change', validateDates);
        checkOutDate.addEventListener('change', validateDates);
        
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        checkInDate.min = today;
        checkOutDate.min = today;
    }
}

function updateBookingSummary(checkIn, checkOut) {
    const summaryElement = document.getElementById('booking-summary');
    if (!summaryElement) return;
    
    const rentPerMonth = parseFloat(summaryElement.dataset.rent) || 0;
    
    if (checkIn && checkOut && checkOut > checkIn) {
        const days = (checkOut - checkIn) / (1000 * 60 * 60 * 24);
        const totalAmount = (days / 30) * rentPerMonth;
        
        const totalElement = document.getElementById('total-amount');
        if (totalElement) {
            totalElement.textContent = `₹₹{totalAmount.toFixed(2)}`;
        }
        
        const durationElement = document.getElementById('booking-duration');
        if (durationElement) {
            durationElement.textContent = `₹{Math.ceil(days)} days`;
        }
    }
}

function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert[data-bs-dismiss="alert"]');
    
    flashMessages.forEach(message => {
        // Auto-hide success and info messages after 5 seconds
        if (message.classList.contains('alert-success') || message.classList.contains('alert-info')) {
            setTimeout(() => {
                const alert = new bootstrap.Alert(message);
                alert.close();
            }, 5000);
        }
    });
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Property card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const propertyCards = document.querySelectorAll('.property-card');
    
    propertyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        });
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

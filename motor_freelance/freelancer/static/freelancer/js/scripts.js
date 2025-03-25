/**
 * Motor Manufacturing Freelancer Portal - Main JavaScript
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initializeTooltips();
    
    // Add custom form validation
    setupFormValidation();
    
    // Setup work filter functionality
    setupWorkFilters();
    
    // Handle concurrency for work selection
    setupConcurrencyHandling();
    
    // Initialize dashboard charts if on dashboard page
    if (document.querySelector('.dashboard-charts')) {
        initializeDashboardCharts();
    }
    
    // Add fade in animation to cards
    animateCards();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup custom form validation
 */
function setupFormValidation() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Password validation for registration form
    const passwordField = document.getElementById('id_password1');
    const confirmPasswordField = document.getElementById('id_password2');
    
    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity("Passwords do not match");
            } else {
                confirmPasswordField.setCustomValidity("");
            }
        });
    }
}

/**
 * Setup work filter functionality
 */
function setupWorkFilters() {
    const categoryFilter = document.getElementById('category-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const hoursFilter = document.getElementById('hours-filter');
    const hoursValue = document.getElementById('hours-value');
    const workItems = document.querySelectorAll('.work-item');
    const noResults = document.getElementById('no-results');
    const resetFilters = document.getElementById('reset-filters');
    
    if (!categoryFilter || !workItems.length) return;
    
    // Update hours filter value display
    if (hoursFilter && hoursValue) {
        hoursFilter.addEventListener('input', function() {
            const value = this.value;
            hoursValue.textContent = value > 0 ? `${value} hours or less` : 'Any hours';
        });
    }
    
    // Apply filters function
    function applyFilters() {
        const category = categoryFilter ? categoryFilter.value : '';
        const priority = priorityFilter ? priorityFilter.value : '';
        const hours = hoursFilter ? hoursFilter.value : '0';
        
        let visibleCount = 0;
        
        workItems.forEach(item => {
            const itemCategory = item.dataset.category;
            const itemPriority = item.dataset.priority;
            const itemHours = parseInt(item.dataset.hours);
            
            const categoryMatch = !category || itemCategory === category;
            const priorityMatch = !priority || itemPriority === priority;
            const hoursMatch = hours === '0' || itemHours <= parseInt(hours);
            
            if (categoryMatch && priorityMatch && hoursMatch) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show/hide no results message
        if (noResults) {
            if (visibleCount === 0 && workItems.length > 0) {
                noResults.classList.remove('d-none');
                const workItemsContainer = document.getElementById('work-items-container');
                if (workItemsContainer) {
                    workItemsContainer.classList.add('d-none');
                }
            } else {
                noResults.classList.add('d-none');
                const workItemsContainer = document.getElementById('work-items-container');
                if (workItemsContainer) {
                    workItemsContainer.classList.remove('d-none');
                }
            }
        }
    }
    
    // Add event listeners to filters
    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', applyFilters);
    }
    
    if (hoursFilter) {
        hoursFilter.addEventListener('input', applyFilters);
    }
    
    // Reset filters
    if (resetFilters) {
        resetFilters.addEventListener('click', function() {
            if (categoryFilter) categoryFilter.value = '';
            if (priorityFilter) priorityFilter.value = '';
            if (hoursFilter) {
                hoursFilter.value = '0';
                if (hoursValue) hoursValue.textContent = 'Any hours';
            }
            applyFilters();
        });
    }
}

/**
 * Handle concurrency for work selection
 */
function setupConcurrencyHandling() {
    const workSelectForms = document.querySelectorAll('form[action*="work_select"]');
    
    workSelectForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            
            if (submitButton) {
                // Disable the button
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });
}

/**
 * Initialize dashboard charts
 */
function initializeDashboardCharts() {
    // This is a placeholder for dashboard charts
    // In a real application, you would use Chart.js or similar library
    console.log('Dashboard charts initialized');
}

/**
 * Add fade in animation to cards
 */
function animateCards() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach((card, index) => {
        // Add fade-in class with a delay based on index
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Format currency display
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Handle work submission form
 */
document.addEventListener('DOMContentLoaded', function() {
    const submissionForm = document.querySelector('form[action*="work_submit"]');
    
    if (submissionForm) {
        submissionForm.addEventListener('submit', function(e) {
            // Validate quality check is completed
            const qualityCheck = document.getElementById('id_quality_check_passed');
            
            if (qualityCheck && !qualityCheck.checked) {
                e.preventDefault();
                alert('Please confirm that your work meets quality standards before submitting.');
                return false;
            }
            
            // Disable submit button to prevent double submission
            const submitButton = submissionForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            }
        });
    }
});

/**
 * Helper functions for eligibility form
 */
document.addEventListener('DOMContentLoaded', function() {
    const dobField = document.getElementById('id_date_of_birth');
    
    if (dobField) {
        dobField.addEventListener('change', function() {
            validateAge(this);
        });
    }
    
    function validateAge(field) {
        const dob = new Date(field.value);
        const today = new Date();
        
        let age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            age--;
        }
        
        if (age < 18) {
            field.setCustomValidity("You must be at least 18 years old to register.");
        } else if (age > 60) {
            field.setCustomValidity("You must be under 60 years old to register.");
        } else {
            field.setCustomValidity("");
        }
    }
});

/**
 * Handle responsive design adjustments
 */
window.addEventListener('resize', function() {
    adjustLayoutForScreenSize();
});

function adjustLayoutForScreenSize() {
    const width = window.innerWidth;
    
    // Adjust card layouts on small screens
    if (width < 768) {
        document.querySelectorAll('.card-title').forEach(title => {
            title.classList.add('small');
        });
    } else {
        document.querySelectorAll('.card-title').forEach(title => {
            title.classList.remove('small');
        });
    }
}

// Run once on page load
document.addEventListener('DOMContentLoaded', function() {
    adjustLayoutForScreenSize();
});

/**
 * Handle form errors highlight
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add is-invalid class to form fields with errors
    document.querySelectorAll('.invalid-feedback').forEach(feedback => {
        const input = feedback.previousElementSibling;
        if (input && (input.classList.contains('form-control') || input.classList.contains('form-select'))) {
            input.classList.add('is-invalid');
        }
    });
});

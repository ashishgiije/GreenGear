// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const body = document.body;

    // Create backdrop element
    const backdrop = document.createElement('div');
    backdrop.className = 'menu-backdrop';
    document.body.appendChild(backdrop);

    function toggleMenu() {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
        backdrop.classList.toggle('active');
        body.classList.toggle('menu-open');
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMenu();
        });

        // Close menu when clicking on backdrop
        backdrop.addEventListener('click', function() {
            toggleMenu();
        });

        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                toggleMenu();
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.matches('.nav-dropbtn') && !event.target.matches('.nav-register-btn')) {
                const dropdowns = document.getElementsByClassName('nav-dropdown-content');
                for (let i = 0; i < dropdowns.length; i++) {
                    const openDropdown = dropdowns[i];
                    if (openDropdown.style.display === 'block') {
                        openDropdown.style.display = 'none';
                    }
                }
            }
        });
    }

    // Handle dropdown menus for mobile
    const dropBtns = document.querySelectorAll('.nav-dropbtn, .nav-register-btn');
    dropBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.nextElementSibling;
            if (dropdown && dropdown.classList.contains('nav-dropdown-content')) {
                dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Search functionality
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('.search-input');
            if (searchInput.value.trim()) {
                // Implement search logic here
                console.log('Searching for:', searchInput.value);
                this.submit(); // Submit the form if you want actual search
            }
        });
    }

    // Equipment filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            // Implement filtering logic here
            console.log('Filter by:', filter);
        });
    });

    // Booking form validation
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            const startDate = this.querySelector('#start_date');
            const duration = this.querySelector('#duration');
            
            if (!startDate.value || !duration.value) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }

    // Equipment image gallery
    const mainImage = document.querySelector('.main-equipment-image');
    const thumbnails = document.querySelectorAll('.thumbnail');
    
    if (thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                if (mainImage) {
                    mainImage.src = this.src;
                }
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Close menu on window resize (if resizing to larger screen)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
            backdrop.classList.remove('active');
            body.classList.remove('menu-open');
        }
    });
});


// Price calculation for booking
function calculateTotalPrice() {
    const ratePerDay = parseFloat(document.getElementById('rate_per_day').value) || 0;
    const ratePerHour = parseFloat(document.getElementById('rate_per_hour').value) || 0;
    const duration = parseInt(document.getElementById('duration').value) || 0;
    const durationType = document.getElementById('duration_type').value;
    
    let total = 0;
    if (durationType === 'days') {
        total = ratePerDay * duration;
    } else if (durationType === 'hours') {
        total = ratePerHour * duration;
    }
    
    const totalElement = document.getElementById('total_price');
    if (totalElement) {
        totalElement.textContent = '₹' + total.toFixed(2);
    }
}

// Initialize price calculation if on booking page
document.addEventListener('DOMContentLoaded', function() {
    const durationInput = document.getElementById('duration');
    const durationType = document.getElementById('duration_type');
    
    if (durationInput) {
        durationInput.addEventListener('input', calculateTotalPrice);
    }
    if (durationType) {
        durationType.addEventListener('change', calculateTotalPrice);
    }
});

// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentElement) {
                    message.parentElement.removeChild(message);
                }
            }, 300);
        }, 5000);
    });

    // Close message on click
    const closeButtons = document.querySelectorAll('.close-message');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.closest('.alert');
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentElement) {
                    message.parentElement.removeChild(message);
                }
            }, 300);
        });
    });
});
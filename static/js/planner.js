// Set default dates (today and 7 days from today)
const today = new Date();
const nextWeek = new Date();
nextWeek.setDate(today.getDate() + 7);

document.getElementById('departure_date').value = today.toISOString().split('T')[0];
document.getElementById('return_date').value = nextWeek.toISOString().split('T')[0];

// Update slider value display
const numDaysSlider = document.getElementById('num_days');
const numDaysValue = document.getElementById('num_days_value');

numDaysSlider.addEventListener('input', (e) => {
    numDaysValue.textContent = e.target.value;
});

// Update preview box
function updatePreview() {
    const destination = document.getElementById('destination').value;
    const travelTheme = document.getElementById('travel_theme').value;
    const previewBox = document.getElementById('preview-box');
    const previewText = document.getElementById('preview-text');
    
    if (destination) {
        previewBox.style.display = 'block';
        previewText.textContent = `🌟 Your ${travelTheme} to ${destination} is about to begin! 🌟`;
    } else {
        previewBox.style.display = 'none';
    }
}

document.getElementById('destination').addEventListener('input', updatePreview);
document.getElementById('travel_theme').addEventListener('change', updatePreview);

// Form submission
document.getElementById('travelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const generateBtn = document.getElementById('generateBtn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoader = generateBtn.querySelector('.btn-loader');
    const resultsSection = document.getElementById('results');
    
    const loadingDiv = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    
    // Disable button and show loading
    generateBtn.disabled = true;
    if (btnText && btnLoader) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
    } else {
        generateBtn.innerHTML = '⏳ Generating...';
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Hide previous results
    document.getElementById('flights-section').style.display = 'none';
    document.getElementById('hotels-section').style.display = 'none';
    document.getElementById('itinerary-section').style.display = 'none';
    document.getElementById('errors-section').style.display = 'none';
    
    // Show loading
    loadingDiv.style.display = 'block';
    
    // Collect form data
    const formData = {
        source: document.getElementById('source').value,
        destination: document.getElementById('destination').value,
        num_days: parseInt(document.getElementById('num_days').value),
        travel_theme: document.getElementById('travel_theme').value,
        activity_preferences: document.getElementById('activity_preferences').value,
        departure_date: document.getElementById('departure_date').value,
        return_date: document.getElementById('return_date').value,
        budget: document.querySelector('input[name="budget"]:checked').value,
        flight_class: document.querySelector('input[name="flight_class"]:checked').value,
        hotel_rating: document.getElementById('hotel_rating').value,
        visa_required: document.getElementById('visa_required').checked,
        travel_insurance: document.getElementById('travel_insurance').checked
    };
    
    try {
        // Update loading text for flights
        loadingText.textContent = '✈️ Fetching best flight options...';
        
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Hide loading
        loadingDiv.style.display = 'none';
        
        // Display results with animations
        setTimeout(() => {
            displayFlights(data.flights);
            displayHotelsRestaurants(data.hotels_restaurants);
            displayItinerary(data.itinerary);
            displayErrors(data.errors);
            
            // Show all result sections
            document.getElementById('flights-section').style.display = 'block';
            document.getElementById('hotels-section').style.display = 'block';
            document.getElementById('itinerary-section').style.display = 'block';
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
        
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.style.display = 'none';
        displayError('Failed to generate travel plan. Please try again.');
    } finally {
        // Re-enable button
        generateBtn.disabled = false;
        if (btnText) {
            btnText.style.display = 'inline';
            if (btnLoader) btnLoader.style.display = 'none';
        } else {
            generateBtn.innerHTML = '<span class="btn-text">🚀 Generate Travel Plan</span>';
        }
    }
});

function displayFlights(flights) {
    const container = document.getElementById('flights-container');
    container.innerHTML = '';
    
    if (!flights || flights.length === 0) {
        container.innerHTML = '<div class="warning-box">⚠️ No flight data available.</div>';
        return;
    }
    
    flights.forEach((flight, index) => {
        setTimeout(() => {
            const flightCard = document.createElement('div');
            flightCard.className = 'flight-card';
            
            const airlineLogo = flight.airline_logo 
                ? `<img src="${flight.airline_logo}" alt="Airline logo" class="airline-logo" onerror="this.style.display='none'">`
                : '';
            
            const bookingButton = flight.booking_link
                ? `<a href="${flight.booking_link}" target="_blank" class="btn-book">🔗 Book Now</a>`
                : `<span class="btn-book" style="background-color: #6c757d; cursor: default;">🔍 View Details</span>`;
            
            flightCard.innerHTML = `
                <div class="flight-header">
                    ${airlineLogo}
                    <div class="airline-info">
                        <div class="airline-name">${flight.airline || 'Unknown Airline'}</div>
                        <div class="route">${flight.departure_airport} → ${flight.arrival_airport}</div>
                    </div>
                </div>
                <div class="flight-details">
                    <div><strong>Departure:</strong> ${flight.departure_time}</div>
                    <div><strong>Arrival:</strong> ${flight.arrival_time}</div>
                    <div><strong>Duration:</strong> ${flight.total_duration} min</div>
                </div>
                <div class="flight-price">₹${flight.price}</div>
                <div>${bookingButton}</div>
            `;
            
            container.appendChild(flightCard);
        }, index * 200);
    });
}

function displayHotelsRestaurants(content) {
    const container = document.getElementById('hotels-container');
    
    if (!content) {
        container.innerHTML = '<div class="warning-box">⚠️ No hotel/restaurant data available.</div>';
        return;
    }
    
    container.textContent = content;
}

function displayItinerary(content) {
    const container = document.getElementById('itinerary-container');
    
    if (!content) {
        const numDays = document.getElementById('num_days').value;
        const destination = document.getElementById('destination').value;
        container.innerHTML = `
            <div class="warning-box">
                ⚠️ No live itinerary. Here's a generic ${numDays}-day itinerary suggestion for ${destination}.
            </div>
            <div class="content-box">
                - Day 1: Arrival and local exploration
                - Day 2: Sightseeing
                - Day 3: Adventure activities
                - Day 4: Relaxation
                - Day 5: Departure
            </div>
        `;
        return;
    }
    
    container.textContent = content;
}

function displayErrors(errors) {
    const errorsSection = document.getElementById('errors-section');
    const errorsContainer = document.getElementById('errors-container');
    
    if (!errors || errors.length === 0) {
        errorsSection.style.display = 'none';
        return;
    }
    
    errorsContainer.innerHTML = '';
    errors.forEach(error => {
        const errorDiv = document.createElement('div');
        errorDiv.textContent = error;
        errorsContainer.appendChild(errorDiv);
    });
    
    errorsSection.style.display = 'block';
}

function displayError(message) {
    const resultsSection = document.getElementById('results');
    resultsSection.innerHTML = `
        <div class="error-section" style="display: block;">
            <h3>❌ Error</h3>
            <div id="errors-container">
                <div>${message}</div>
            </div>
        </div>
    `;
    resultsSection.style.display = 'block';
}

// Initialize preview on page load
updatePreview();

// Add form input animations
document.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
    });
});


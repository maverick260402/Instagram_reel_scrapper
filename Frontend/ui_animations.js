/**
 * UI Animations Controller
 * Handles scroll animations and interactive effects
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Scroll Animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Select elements to animate
    // You can add the 'animate-on-scroll' class to HTML elements manually,
    // or this script can auto-target common containers
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .card, .stat-card, .form-group, h1, .table-container');
    
    animatedElements.forEach((el, index) => {
        el.classList.add('animate-on-scroll');
        
        // Add staggered delays for children of the same container if needed
        if (index % 3 === 1) el.classList.add('delay-100');
        if (index % 3 === 2) el.classList.add('delay-200');
        
        observer.observe(el);
    });
});
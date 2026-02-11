/**
 * Analytics Hub Landing Page - JavaScript
 * Includes: Scroll Animations, FAQ Accordion, Mobile Menu
 */

// ==================== DOM Elements ====================
const navbar = document.getElementById('navbar');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');
const faqItems = document.querySelectorAll('.faq-item');
const contactForm = document.getElementById('contactForm');

// ==================== Navbar Scroll Effect ====================
let lastScrollY = window.scrollY;

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    lastScrollY = window.scrollY;
});

// ==================== Mobile Menu Toggle ====================
mobileMenuBtn?.addEventListener('click', () => {
    mobileMenuBtn.classList.toggle('active');
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking a link
navLinks?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenuBtn.classList.remove('active');
        navLinks.classList.remove('active');
    });
});

// ==================== Smooth Scroll for Anchor Links ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ==================== Scroll Animations (Intersection Observer) ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            // Optionally unobserve after animation
            // fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.animate-on-scroll').forEach(el => {
    fadeInObserver.observe(el);
});

// ==================== FAQ Accordion ====================
faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question?.addEventListener('click', () => {
        // Close other items
        faqItems.forEach(otherItem => {
            if (otherItem !== item) {
                otherItem.classList.remove('active');
            }
        });
        // Toggle current item
        item.classList.toggle('active');
    });
});

// ==================== Contact Form Handler ====================
contactForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(contactForm);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: formData.get('message')
    };

    // Show success message (you can replace this with actual API call)
    alert('Thank you for your message! We\'ll get back to you soon.');
    contactForm.reset();
});

// ==================== Animated Stat Counters ====================

document.addEventListener('DOMContentLoaded', () => {
    initAnimatedCounters();
});

function initAnimatedCounters() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const endVal = parseFloat(el.getAttribute('data-count'));
                const prefix = el.getAttribute('data-prefix') || '';
                const suffix = el.getAttribute('data-suffix') || '';
                const decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals')) : 0;

                if (!isNaN(endVal)) {
                    animateCounter(el, endVal, prefix, suffix, decimals);
                }
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(el => observer.observe(el));
}

function animateCounter(el, target, prefix, suffix, decimals) {
    const duration = 1800;
    const startTime = performance.now();

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeOutCubic(progress);
        const current = eased * target;

        if (decimals > 0) {
            el.textContent = prefix + current.toFixed(decimals) + suffix;
        } else {
            el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            if (decimals > 0) {
                el.textContent = prefix + target.toFixed(decimals) + suffix;
            } else {
                el.textContent = prefix + target.toLocaleString() + suffix;
            }
        }
    }

    requestAnimationFrame(update);
}
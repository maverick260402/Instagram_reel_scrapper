/**
 * Analytics Hub Landing Page - JavaScript
 * Includes: Three.js Point Sphere, Scroll Animations, FAQ Accordion, Mobile Menu
 */

// ==================== DOM Elements ====================
const navbar = document.getElementById('navbar');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');
const pointSphereCanvas = document.getElementById('pointSphere');
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

document.querySelectorAll('.fade-in').forEach(el => {
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

// ==================== Three.js Point Sphere Animation ====================
let scene, camera, renderer, particles, particlePositions;
let mouseX = 0, mouseY = 0;
let windowHalfX = window.innerWidth / 2;
let windowHalfY = window.innerHeight / 2;

function initPointSphere() {
    if (!pointSphereCanvas || typeof THREE === 'undefined') {
        console.warn('Three.js or canvas not available');
        return;
    }

    // Scene setup
    scene = new THREE.Scene();

    // Camera setup
    const containerWidth = pointSphereCanvas.parentElement.offsetWidth;
    const containerHeight = pointSphereCanvas.parentElement.offsetHeight;
    camera = new THREE.PerspectiveCamera(75, containerWidth / containerHeight, 0.1, 1000);
    camera.position.z = 400;

    // Renderer setup
    renderer = new THREE.WebGLRenderer({
        canvas: pointSphereCanvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(containerWidth, containerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    // Create particles
    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    particlePositions = new Float32Array(particleCount * 3);
    const originalPositions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const radius = 200;

    for (let i = 0; i < particleCount; i++) {
        // Distribute points on sphere surface using Fibonacci sphere algorithm
        const phi = Math.acos(-1 + (2 * i) / particleCount);
        const theta = Math.sqrt(particleCount * Math.PI) * phi;

        const x = radius * Math.cos(theta) * Math.sin(phi);
        const y = radius * Math.sin(theta) * Math.sin(phi);
        const z = radius * Math.cos(phi);

        particlePositions[i * 3] = x;
        particlePositions[i * 3 + 1] = y;
        particlePositions[i * 3 + 2] = z;

        originalPositions[i * 3] = x;
        originalPositions[i * 3 + 1] = y;
        originalPositions[i * 3 + 2] = z;

        // Color variation: purple to lighter purple
        const intensity = 0.5 + Math.random() * 0.5;
        colors[i * 3] = 0.545 * intensity; // R (139/255)
        colors[i * 3 + 1] = 0.361 * intensity; // G (92/255)
        colors[i * 3 + 2] = 0.965 * intensity; // B (246/255)
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.userData.originalPositions = originalPositions;

    // Particle material
    const material = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        sizeAttenuation: true,
        blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Mouse move listener
    document.addEventListener('mousemove', onMouseMove);
    window.addEventListener('resize', onWindowResize);

    // Start animation
    animate();
}

function onMouseMove(event) {
    mouseX = (event.clientX - windowHalfX) / windowHalfX;
    mouseY = (event.clientY - windowHalfY) / windowHalfY;
}

function onWindowResize() {
    if (!pointSphereCanvas || !camera || !renderer) return;

    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    const containerWidth = pointSphereCanvas.parentElement.offsetWidth;
    const containerHeight = pointSphereCanvas.parentElement.offsetHeight;

    camera.aspect = containerWidth / containerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(containerWidth, containerHeight);
}

function animate() {
    requestAnimationFrame(animate);

    if (!particles) return;

    const time = Date.now() * 0.001;
    const scrollProgress = window.scrollY / (document.body.scrollHeight - window.innerHeight);

    // Rotate based on time and mouse
    particles.rotation.y = time * 0.1 + mouseX * 0.5;
    particles.rotation.x = Math.sin(time * 0.1) * 0.2 + mouseY * 0.3;

    // Scale based on scroll
    const scale = 1 - scrollProgress * 0.3;
    particles.scale.setScalar(Math.max(scale, 0.7));

    // Particle repulsion from mouse
    const positions = particles.geometry.attributes.position.array;
    const originalPositions = particles.geometry.userData.originalPositions;
    const repulsionRadius = 80;
    const repulsionStrength = 30;

    // Convert mouse position to 3D space (approximate)
    const mouseX3D = mouseX * 300;
    const mouseY3D = -mouseY * 300;

    for (let i = 0; i < positions.length; i += 3) {
        const ox = originalPositions[i];
        const oy = originalPositions[i + 1];
        const oz = originalPositions[i + 2];

        // Calculate distance from mouse (simplified 2D check)
        const dx = positions[i] - mouseX3D;
        const dy = positions[i + 1] - mouseY3D;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < repulsionRadius && distance > 0) {
            const force = (repulsionRadius - distance) / repulsionRadius;
            const pushX = (dx / distance) * force * repulsionStrength;
            const pushY = (dy / distance) * force * repulsionStrength;

            positions[i] = ox + pushX;
            positions[i + 1] = oy + pushY;
        } else {
            // Smoothly return to original position
            positions[i] += (ox - positions[i]) * 0.05;
            positions[i + 1] += (oy - positions[i + 1]) * 0.05;
            positions[i + 2] += (oz - positions[i + 2]) * 0.05;
        }
    }

    particles.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
}

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Three.js sphere after DOM is ready
    // Small delay to ensure Three.js is loaded
    setTimeout(initPointSphere, 100);
});

// Also try initializing if Three.js loads after DOMContentLoaded
if (typeof THREE !== 'undefined') {
    setTimeout(initPointSphere, 100);
}

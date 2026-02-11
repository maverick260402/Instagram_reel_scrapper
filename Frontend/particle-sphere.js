/**
 * Particle Sphere - Interactive 3D data cluster visualization
 * Network graph style with data scraps and scanner effect
 */

(function () {
    const canvas = document.getElementById('particleSphere');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    let width, height, centerX, centerY, sphereRadius;
    let animationId;

    // Accumulated rotation angles
    let angleX = 0;
    let angleY = 0;

    // Velocity for inertia
    let velocityX = 0;
    let velocityY = 0;

    // Drag state
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;

    // Configuration
    const PARTICLE_COUNT = 1000;
    const PARTICLE_COLOR_R = 26;
    const PARTICLE_COLOR_G = 26;
    const PARTICLE_COLOR_B = 26;
    const AUTO_ROTATE_SPEED = 0.004;
    const DRAG_SENSITIVITY = 0.008;
    const INERTIA_FRICTION = 0.96;
    const INERTIA_THRESHOLD = 0.0001;
    const MIN_PARTICLE_SIZE = 1.0;
    const MAX_PARTICLE_SIZE = 3.0;

    // Network graph connections — light grey like wireframe
    const CONNECTION_DISTANCE = 0.18;
    const CONN_COLOR_R = 229;
    const CONN_COLOR_G = 229;
    const CONN_COLOR_B = 229;
    const CONNECTION_OPACITY = 0.5;
    const CONNECTION_WIDTH = 0.7;

    // Scanner line
    const SCANNER_COLOR = '0, 122, 255'; // #007AFF
    const SCANNER_CYCLE = 5000; // ms per full scan

    // Data scraps — floating niche labels orbiting outside the sphere
    const DATA_SCRAPS = [
        { label: '</>', angle: 0, orbitRadius: 1.22, orbitTilt: 0.3, size: 10 },
        { label: 'CSV', angle: Math.PI * 0.4, orbitRadius: 1.28, orbitTilt: -0.2, size: 9 },
        { label: '@', angle: Math.PI * 0.8, orbitRadius: 1.18, orbitTilt: 0.5, size: 12 },
        { label: '{ }', angle: Math.PI * 1.2, orbitRadius: 1.25, orbitTilt: -0.4, size: 9 },
        { label: 'API', angle: Math.PI * 1.5, orbitRadius: 1.3, orbitTilt: 0.15, size: 9 },
        { label: '#', angle: Math.PI * 1.8, orbitRadius: 1.2, orbitTilt: -0.35, size: 11 },
    ];

    const particles = [];

    function resize() {
        const rect = canvas.parentElement.getBoundingClientRect();
        const size = Math.min(rect.width, 600);
        width = size;
        height = size;
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        centerX = width / 2;
        centerY = height / 2;
        sphereRadius = size * 0.38;
    }

    function initParticles() {
        particles.length = 0;
        const goldenAngle = Math.PI * (3 - Math.sqrt(5));

        for (let i = 0; i < PARTICLE_COUNT; i++) {
            const y = 1 - (i / (PARTICLE_COUNT - 1)) * 2;
            const radiusAtY = Math.sqrt(1 - y * y);
            const theta = goldenAngle * i;

            const jitter = 0.04;
            const px = radiusAtY * Math.cos(theta) + (Math.random() - 0.5) * jitter;
            const py = y + (Math.random() - 0.5) * jitter;
            const pz = radiusAtY * Math.sin(theta) + (Math.random() - 0.5) * jitter;

            const len = Math.sqrt(px * px + py * py + pz * pz);
            const depthVariance = 0.7 + Math.random() * 0.3;

            particles.push({
                x: (px / len) * depthVariance,
                y: (py / len) * depthVariance,
                z: (pz / len) * depthVariance,
                baseSize: MIN_PARTICLE_SIZE + Math.random() * (MAX_PARTICLE_SIZE - MIN_PARTICLE_SIZE)
            });
        }
    }

    function rotatePoint(x, y, z, rx, ry) {
        let cosY = Math.cos(ry), sinY = Math.sin(ry);
        let x1 = x * cosY - z * sinY;
        let z1 = x * sinY + z * cosY;

        let cosX = Math.cos(rx), sinX = Math.sin(rx);
        let y1 = y * cosX - z1 * sinX;
        let z2 = y * sinX + z1 * cosX;

        return { x: x1, y: y1, z: z2 };
    }

    // ---- Scanner line ----
    function drawScanner(time) {
        const progress = (time % SCANNER_CYCLE) / SCANNER_CYCLE;
        // Scan from top to bottom of sphere
        const scanY = centerY - sphereRadius + (sphereRadius * 2) * progress;

        // Calculate horizontal extent at this Y position (circle cross-section)
        const dy = (scanY - centerY) / sphereRadius;
        if (Math.abs(dy) > 1) return;

        const halfWidth = Math.sqrt(1 - dy * dy) * sphereRadius;

        // Draw the scan line with fade
        const gradient = ctx.createLinearGradient(
            centerX - halfWidth, scanY,
            centerX + halfWidth, scanY
        );
        gradient.addColorStop(0, `rgba(${SCANNER_COLOR}, 0)`);
        gradient.addColorStop(0.15, `rgba(${SCANNER_COLOR}, 0.25)`);
        gradient.addColorStop(0.5, `rgba(${SCANNER_COLOR}, 0.4)`);
        gradient.addColorStop(0.85, `rgba(${SCANNER_COLOR}, 0.25)`);
        gradient.addColorStop(1, `rgba(${SCANNER_COLOR}, 0)`);

        ctx.beginPath();
        ctx.moveTo(centerX - halfWidth, scanY);
        ctx.lineTo(centerX + halfWidth, scanY);
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Subtle glow trail above the line
        const trailGradient = ctx.createLinearGradient(
            centerX, scanY - 20,
            centerX, scanY
        );
        trailGradient.addColorStop(0, `rgba(${SCANNER_COLOR}, 0)`);
        trailGradient.addColorStop(1, `rgba(${SCANNER_COLOR}, 0.06)`);

        // Clip trail to circle
        const trailTop = scanY - 20;
        const dyTop = (trailTop - centerY) / sphereRadius;
        const halfWidthTop = Math.abs(dyTop) <= 1 ? Math.sqrt(1 - dyTop * dyTop) * sphereRadius : 0;

        ctx.beginPath();
        ctx.moveTo(centerX - halfWidthTop, trailTop);
        ctx.lineTo(centerX + halfWidthTop, trailTop);
        ctx.lineTo(centerX + halfWidth, scanY);
        ctx.lineTo(centerX - halfWidth, scanY);
        ctx.closePath();
        ctx.fillStyle = trailGradient;
        ctx.fill();
    }

    // ---- Data scraps ----
    function drawDataScraps(time) {
        const orbitSpeed = 0.0003;

        ctx.font = '600 ${size}px "JetBrains Mono", "SF Mono", "Fira Code", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let i = 0; i < DATA_SCRAPS.length; i++) {
            const scrap = DATA_SCRAPS[i];
            const t = scrap.angle + time * orbitSpeed;

            // 3D orbit position
            const ox = Math.cos(t) * scrap.orbitRadius;
            const oy = Math.sin(t) * scrap.orbitTilt * scrap.orbitRadius * 0.6;
            const oz = Math.sin(t) * scrap.orbitRadius;

            // Apply same rotation as the sphere
            const rotated = rotatePoint(ox, oy, oz, angleX, angleY);

            const screenX = centerX + rotated.x * sphereRadius;
            const screenY = centerY + rotated.y * sphereRadius;

            // Depth-based opacity: front = more visible, back = hidden
            const depthFactor = (rotated.z + 1) / 2;
            if (depthFactor < 0.3) continue; // Hide when behind sphere

            const opacity = 0.06 + depthFactor * 0.08; // Very subtle: 0.06 to 0.14

            ctx.font = `bold ${scrap.size}px "JetBrains Mono", "SF Mono", "Fira Code", monospace`;

            const gradient = ctx.createLinearGradient(0, screenY - scrap.size / 2, 0, screenY + scrap.size / 2);
            gradient.addColorStop(0, `rgba(26, 26, 26, ${opacity})`);
            gradient.addColorStop(1, `rgba(74, 74, 74, ${opacity})`);

            ctx.fillStyle = gradient;
            ctx.fillText(scrap.label, screenX, screenY);
        }
    }

    let lastTime = 0;

    function render(time) {
        const dt = lastTime ? (time - lastTime) / 1000 : 0.016;
        lastTime = time;

        ctx.clearRect(0, 0, width, height);

        // Auto-rotation when idle
        if (!isDragging && Math.abs(velocityX) < INERTIA_THRESHOLD && Math.abs(velocityY) < INERTIA_THRESHOLD) {
            angleY += AUTO_ROTATE_SPEED * dt;
        }

        // Inertia
        if (!isDragging) {
            angleX += velocityX;
            angleY += velocityY;
            velocityX *= INERTIA_FRICTION;
            velocityY *= INERTIA_FRICTION;
            if (Math.abs(velocityX) < INERTIA_THRESHOLD) velocityX = 0;
            if (Math.abs(velocityY) < INERTIA_THRESHOLD) velocityY = 0;
        }

        // Transform particles
        const projected = [];

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            const r = rotatePoint(p.x, p.y, p.z, angleX, angleY);

            const depthFactor = (r.z + 1) / 2;
            const screenX = centerX + r.x * sphereRadius;
            const screenY = centerY + r.y * sphereRadius;
            const size = p.baseSize * (0.3 + depthFactor * 0.7);
            const opacity = 0.12 + depthFactor * 0.55;

            projected.push({
                x: screenX,
                y: screenY,
                z: r.z,
                rx: r.x,
                ry: r.y,
                rz: r.z,
                size: size,
                opacity: opacity
            });
        }

        projected.sort((a, b) => a.z - b.z);

        // Draw connection lines (light grey network graph)
        ctx.lineWidth = CONNECTION_WIDTH;
        const connThreshSq = CONNECTION_DISTANCE * CONNECTION_DISTANCE;
        const frontParticles = projected.filter(p => p.z > -0.2);

        for (let i = 0; i < frontParticles.length; i++) {
            const a = frontParticles[i];
            for (let j = i + 1; j < frontParticles.length; j++) {
                const b = frontParticles[j];

                const dx = a.rx - b.rx;
                const dy = a.ry - b.ry;
                const dz = a.rz - b.rz;
                const distSq = dx * dx + dy * dy + dz * dz;

                if (distSq < connThreshSq) {
                    const proximity = 1 - Math.sqrt(distSq) / CONNECTION_DISTANCE;
                    const avgDepth = (a.z + b.z + 2) / 4;
                    const lineAlpha = CONNECTION_OPACITY * proximity * avgDepth;

                    if (lineAlpha > 0.01) {
                        ctx.beginPath();
                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);
                        ctx.strokeStyle = `rgba(${CONN_COLOR_R}, ${CONN_COLOR_G}, ${CONN_COLOR_B}, ${lineAlpha})`;
                        ctx.stroke();
                    }
                }
            }
        }

        // Draw particles
        for (let i = 0; i < projected.length; i++) {
            const p = projected[i];
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${PARTICLE_COLOR_R}, ${PARTICLE_COLOR_G}, ${PARTICLE_COLOR_B}, ${p.opacity})`;
            ctx.fill();
        }

        // Draw floating data scraps
        drawDataScraps(time);

        // Draw scanner line on top
        drawScanner(time);

        animationId = requestAnimationFrame(render);
    }

    // ---- Mouse drag ----

    function onMouseDown(e) {
        isDragging = true;
        velocityX = 0;
        velocityY = 0;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        canvas.style.cursor = 'grabbing';
    }

    function onMouseMove(e) {
        if (!isDragging) return;
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        angleY += dx * DRAG_SENSITIVITY;
        angleX += dy * DRAG_SENSITIVITY;
        velocityY = dx * DRAG_SENSITIVITY;
        velocityX = dy * DRAG_SENSITIVITY;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
    }

    function onMouseUp() {
        isDragging = false;
        canvas.style.cursor = 'grab';
    }

    // ---- Touch drag ----

    function onTouchStart(e) {
        if (e.touches.length === 1) {
            isDragging = true;
            velocityX = 0;
            velocityY = 0;
            lastMouseX = e.touches[0].clientX;
            lastMouseY = e.touches[0].clientY;
        }
    }

    function onTouchMove(e) {
        if (!isDragging || e.touches.length !== 1) return;
        e.preventDefault();
        const dx = e.touches[0].clientX - lastMouseX;
        const dy = e.touches[0].clientY - lastMouseY;
        angleY += dx * DRAG_SENSITIVITY;
        angleX += dy * DRAG_SENSITIVITY;
        velocityY = dx * DRAG_SENSITIVITY;
        velocityX = dy * DRAG_SENSITIVITY;
        lastMouseX = e.touches[0].clientX;
        lastMouseY = e.touches[0].clientY;
    }

    function onTouchEnd() {
        isDragging = false;
    }

    // ---- Init ----

    function init() {
        resize();
        initParticles();
        canvas.style.cursor = 'grab';

        canvas.addEventListener('mousedown', onMouseDown);
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);

        canvas.addEventListener('touchstart', onTouchStart, { passive: true });
        canvas.addEventListener('touchmove', onTouchMove, { passive: false });
        canvas.addEventListener('touchend', onTouchEnd);

        window.addEventListener('resize', resize);
        animationId = requestAnimationFrame(render);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

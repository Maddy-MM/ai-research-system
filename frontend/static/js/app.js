/**
 * ResearchMind Frontend Application
 * Multi-Agent Pipeline Client Controller
 */

(() => {
    // Prevent browser from restoring stale scroll positions on navigation/reload
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }

    // -------------------------------------------------------------------------
    // Disable Zoom (Desktop Ctrl/Cmd+Wheel, Ctrl/Cmd+Keys, Mobile Pinch/Gestures)
    // -------------------------------------------------------------------------
    function initZoomPrevention() {
        let isModifierDown = false;

        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                isModifierDown = true;
                const zoomKeys = ['+', '-', '=', '_', '0'];
                const zoomCodes = ['NumpadAdd', 'NumpadSubtract', 'Numpad0', 'Equal', 'Minus', 'Digit0'];
                if (zoomKeys.includes(e.key) || zoomCodes.includes(e.code)) {
                    e.preventDefault();
                }
            }
        }, { passive: false });

        window.addEventListener('keyup', (e) => {
            if (!e.ctrlKey && !e.metaKey) {
                isModifierDown = false;
            }
        }, { passive: true });

        // Intercept wheel only when Ctrl/Cmd is engaged so normal scroll is 100% native
        window.addEventListener('wheel', (e) => {
            if (e.ctrlKey || e.metaKey || isModifierDown) {
                e.preventDefault();
            }
        }, { passive: false });

        // Prevent mobile multi-touch pinch-to-zoom gestures
        document.addEventListener('touchmove', (e) => {
            if (e.touches && e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });

        // Prevent iOS Safari gesture zoom
        document.addEventListener('gesturestart', (e) => {
            e.preventDefault();
        }, { passive: false });
        document.addEventListener('gesturechange', (e) => {
            e.preventDefault();
        }, { passive: false });
        document.addEventListener('gestureend', (e) => {
            e.preventDefault();
        }, { passive: false });
    }
    initZoomPrevention();

    // -------------------------------------------------------------------------
    // Particle Canvas Background (Login Screen 0 - Rich Multi-Agent Neural Constellation)
    // -------------------------------------------------------------------------
    function initParticleCanvas() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let animId;
        let particles = [];
        let pulses = [];
        let pulseTimer = 0;
        let globalTick = 0;
        const mouse = { x: null, y: null };

        function getParticleCount() {
            const area = canvas.width * canvas.height;
            return Math.min(125, Math.max(50, Math.floor(area / 14500)));
        }

        function getConnectionDistance() {
            return canvas.width > 768 ? 155 : 115;
        }

        function getSpeed() {
            return canvas.width > 768 ? 0.32 : 0.24;
        }

        function resize() {
            if (!canvas.parentElement) return;
            const w = canvas.parentElement.offsetWidth || window.innerWidth;
            const h = canvas.parentElement.offsetHeight || window.innerHeight;
            canvas.width = w;
            canvas.height = h;
        }

        function createParticles() {
            particles = [];
            pulses = [];
            const count = getParticleCount();
            const speed = getSpeed();
            for (let i = 0; i < count; i++) {
                const bvx = (Math.random() - 0.5) * speed;
                const bvy = (Math.random() - 0.5) * speed;

                // 5 Distinct Agent Tiers for deep celestial intelligence:
                let tier = 'standard';
                let r = Math.random() * 0.9 + 1.1;
                let opacity = Math.random() * 0.25 + 0.35;
                const pulsePhase = Math.random() * Math.PI * 2;

                if (i % 18 === 0) {
                    tier = 'solar'; // Planner node (Golden beacon)
                    r = Math.random() * 1.2 + 3.0;
                    opacity = 0.95;
                } else if (i % 7 === 0) {
                    tier = 'amber'; // Researcher node
                    r = Math.random() * 0.8 + 2.1;
                    opacity = 0.80;
                } else if (i % 11 === 0) {
                    tier = 'violet'; // Critic / Evaluation node
                    r = Math.random() * 0.7 + 1.8;
                    opacity = 0.80;
                } else if (i % 13 === 0) {
                    tier = 'cyan'; // Fact-Check Verifier node
                    r = Math.random() * 0.7 + 1.7;
                    opacity = 0.80;
                } else if (i % 3 === 0) {
                    tier = 'micro'; // Synaptic cosmic dust
                    r = Math.random() * 0.35 + 0.50;
                    opacity = Math.random() * 0.15 + 0.18;
                }

                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: bvx,
                    vy: bvy,
                    baseVx: bvx,
                    baseVy: bvy,
                    r,
                    opacity,
                    tier,
                    pulsePhase
                });
            }
        }

        function spawnSignalPulse() {
            if (pulses.length >= 12 || particles.length < 2) return;
            const activeParticles = particles.filter(p => p.tier !== 'micro');
            if (activeParticles.length < 2) return;
            const from = activeParticles[Math.floor(Math.random() * activeParticles.length)];
            const connectionDist = getConnectionDistance();

            const candidates = [];
            for (let i = 0; i < activeParticles.length; i++) {
                const candidate = activeParticles[i];
                if (candidate === from) continue;
                const dx = from.x - candidate.x;
                const dy = from.y - candidate.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < connectionDist && dist > 18) {
                    candidates.push(candidate);
                }
            }

            if (candidates.length > 0) {
                const to = candidates[Math.floor(Math.random() * candidates.length)];
                let color = 'rgba(255, 175, 95, 0.95)';
                let glowColor = 'rgba(255, 126, 41, 0.8)';
                if (from.tier === 'violet' || to.tier === 'violet') {
                    color = 'rgba(216, 180, 254, 0.95)';
                    glowColor = 'rgba(168, 85, 247, 0.8)';
                } else if (from.tier === 'cyan' || to.tier === 'cyan') {
                    color = 'rgba(125, 245, 240, 0.95)';
                    glowColor = 'rgba(20, 184, 166, 0.8)';
                } else if (from.tier === 'solar') {
                    color = 'rgba(255, 230, 150, 0.98)';
                    glowColor = 'rgba(255, 180, 50, 0.9)';
                }

                pulses.push({
                    from,
                    to,
                    progress: 0,
                    speed: Math.random() * 0.014 + 0.012,
                    color,
                    glowColor,
                    size: Math.random() * 0.6 + 1.8
                });
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            globalTick++;
            const connectionDist = getConnectionDistance();

            // 1. Draw Constellation Network Connections with Distance & Tier Gradients
            for (let i = 0; i < particles.length; i++) {
                const pi = particles[i];
                if (pi.tier === 'micro') continue;

                for (let j = i + 1; j < particles.length; j++) {
                    const pj = particles[j];
                    if (pj.tier === 'micro') continue;

                    const dx = pi.x - pj.x;
                    const dy = pi.y - pj.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < connectionDist) {
                        const alpha = (1 - dist / connectionDist);
                        ctx.beginPath();
                        ctx.moveTo(pi.x, pi.y);
                        ctx.lineTo(pj.x, pj.y);

                        if (pi.tier === 'violet' || pj.tier === 'violet') {
                            ctx.strokeStyle = `rgba(168, 85, 247, ${alpha * 0.22})`;
                        } else if (pi.tier === 'cyan' || pj.tier === 'cyan') {
                            ctx.strokeStyle = `rgba(45, 212, 191, ${alpha * 0.20})`;
                        } else if (pi.tier === 'solar' || pj.tier === 'solar') {
                            ctx.strokeStyle = `rgba(255, 175, 75, ${alpha * 0.26})`;
                        } else {
                            ctx.strokeStyle = `rgba(255, 140, 50, ${alpha * 0.18})`;
                        }
                        ctx.lineWidth = 0.8;
                        ctx.stroke();
                    }
                }
            }

            // 2. Mouse Proximity Synaptic Glow Connections
            if (mouse.x !== null && canvas.width > 768) {
                const mouseRange = 140;
                for (let i = 0; i < particles.length; i++) {
                    const p = particles[i];
                    if (p.tier === 'micro') continue;
                    const dx = p.x - mouse.x;
                    const dy = p.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouseRange) {
                        const mAlpha = (1 - dist / mouseRange);
                        ctx.beginPath();
                        ctx.moveTo(mouse.x, mouse.y);
                        ctx.lineTo(p.x, p.y);
                        ctx.strokeStyle = `rgba(255, 160, 60, ${mAlpha * 0.35})`;
                        ctx.lineWidth = 0.9;
                        ctx.stroke();
                    }
                }
            }

            // 3. Dynamic Multi-Agent Signal Pulses (Streaming Intelligence Packets)
            pulseTimer++;
            if (pulseTimer % 28 === 0) {
                spawnSignalPulse();
            }

            for (let k = pulses.length - 1; k >= 0; k--) {
                const pulse = pulses[k];
                pulse.progress += pulse.speed;

                if (pulse.progress >= 1) {
                    pulses.splice(k, 1);
                    continue;
                }

                // Interpolate position along line
                const px = pulse.from.x + (pulse.to.x - pulse.from.x) * pulse.progress;
                const py = pulse.from.y + (pulse.to.y - pulse.from.y) * pulse.progress;

                ctx.save();
                ctx.beginPath();
                ctx.arc(px, py, pulse.size, 0, Math.PI * 2);
                ctx.fillStyle = pulse.color;
                ctx.shadowColor = pulse.glowColor;
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            // 4. Mouse Interactive Vortex / Swirl
            if (mouse.x !== null && canvas.width > 768) {
                for (let i = 0; i < particles.length; i++) {
                    const pi = particles[i];
                    const dx = pi.x - mouse.x;
                    const dy = pi.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    const vortexRadius = 88;
                    const eyeRadius = 24;

                    if (dist < vortexRadius && dist > 1) {
                        const factor = 1 - dist / vortexRadius;
                        const tangentX = -dy / dist;
                        const tangentY = dx / dist;
                        const swirlSpeed = factor * factor * 3.4;

                        let radialForce = 0;
                        if (dist > eyeRadius) {
                            radialForce = -factor * 1.5;
                        } else {
                            radialForce = ((eyeRadius - dist) / eyeRadius) * 2.2;
                        }

                        const radialX = dx / dist;
                        const radialY = dy / dist;

                        pi.vx += tangentX * swirlSpeed + radialX * radialForce;
                        pi.vy += tangentY * swirlSpeed + radialY * radialForce;
                    }
                }
            }

            // 5. Update Particle Positions & Draw Nodes with Ambient Halos
            for (const p of particles) {
                p.vx = p.vx * 0.93 + p.baseVx * 0.07;
                p.vy = p.vy * 0.93 + p.baseVy * 0.07;

                const curSpeed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                const maxSpeed = 4.2;
                if (curSpeed > maxSpeed) {
                    p.vx = (p.vx / curSpeed) * maxSpeed;
                    p.vy = (p.vy / curSpeed) * maxSpeed;
                }

                p.x += p.vx;
                p.y += p.vy;

                // Wrap around edges gracefully
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                // Subtle breathing pulse on key agent nodes
                const breath = Math.sin(globalTick * 0.04 + p.pulsePhase) * 0.25;

                ctx.save();

                // Draw radiant outer pulse rings for Solar and major agent nodes
                if (p.tier === 'solar') {
                    const outerHalo = (p.r * 2.6) + breath * 3;
                    const haloAlpha = Math.max(0.08, 0.22 + breath * 0.12);
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, outerHalo, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 140, 40, ${haloAlpha * 0.4})`;
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 205, 115, ${p.opacity})`;
                    ctx.shadowColor = 'rgba(255, 140, 40, 0.95)';
                    ctx.shadowBlur = 14;
                    ctx.fill();
                } else if (p.tier === 'amber') {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 175, 80, ${p.opacity})`;
                    ctx.shadowColor = 'rgba(255, 126, 41, 0.85)';
                    ctx.shadowBlur = 9;
                    ctx.fill();
                } else if (p.tier === 'violet') {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(196, 142, 255, ${p.opacity})`;
                    ctx.shadowColor = 'rgba(168, 85, 247, 0.85)';
                    ctx.shadowBlur = 8;
                    ctx.fill();
                } else if (p.tier === 'cyan') {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(110, 240, 230, ${p.opacity})`;
                    ctx.shadowColor = 'rgba(20, 184, 166, 0.85)';
                    ctx.shadowBlur = 8;
                    ctx.fill();
                } else if (p.tier === 'micro') {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 210, 160, ${p.opacity})`;
                    ctx.fill();
                } else {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 145, 60, ${p.opacity})`;
                    ctx.shadowColor = 'rgba(255, 126, 41, 0.5)';
                    ctx.shadowBlur = 4;
                    ctx.fill();
                }

                ctx.restore();
            }

            animId = requestAnimationFrame(draw);
        }

        resize();
        createParticles();
        draw();

        window.addEventListener('resize', () => {
            resize();
            createParticles();
        });

        // Mouse tracking for subtle desktop interactivity
        window.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });
        window.addEventListener('mouseleave', () => {
            mouse.x = null;
            mouse.y = null;
        });

        // Cleanup & resume when view changes
        let isRunning = true;
        const observer = new MutationObserver(() => {
            const loginView = document.getElementById('view-login');
            if (loginView && loginView.classList.contains('hidden')) {
                if (isRunning) {
                    cancelAnimationFrame(animId);
                    isRunning = false;
                }
            } else if (loginView && !loginView.classList.contains('hidden')) {
                if (!isRunning) {
                    resize();
                    createParticles();
                    animId = requestAnimationFrame(draw);
                    isRunning = true;
                }
            }
        });
        const loginView = document.getElementById('view-login');
        if (loginView) {
            observer.observe(loginView, { attributes: true, attributeFilter: ['class'] });
        }
    }

    // -------------------------------------------------------------------------
    // Stage Neural Stream Canvas (Screen 1 Celestial Neural Constellation)
    // -------------------------------------------------------------------------
    function initStageNeuralCanvas() {
        const canvas = document.getElementById('stage-neural-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let animId;
        let particles = [];
        let pulses = [];
        let pulseTimer = 0;
        let globalTick = 0;

        // Mouse tracking & smooth physics for ambient cursor glow
        const mouse = { x: null, y: null, active: false };
        const smoothMouse = { x: null, y: null };
        let mouseIntensity = 0;

        function getParticleCount() {
            const area = canvas.width * canvas.height;
            // Rich, active multi-agent intelligence field: ~48 on mobile, ~85-95 on desktop
            return Math.min(96, Math.max(48, Math.floor(area / 14000)));
        }

        function getConnectionDistance() {
            return canvas.width > 768 ? 155 : 105;
        }

        function getBaseSpeed() {
            return canvas.width > 768 ? 0.28 : 0.20;
        }

        function resize() {
            if (!canvas) return;
            const parent = canvas.parentElement || document.querySelector('.app-main-stage');
            const w = (parent && parent.offsetWidth > 0) ? parent.offsetWidth : window.innerWidth;
            const h = (parent && parent.offsetHeight > 0) ? parent.offsetHeight : window.innerHeight;
            if (w <= 0 || h <= 0) return;
            canvas.width = w;
            canvas.height = h;
            createParticles();
        }

        function createParticles() {
            particles = [];
            pulses = [];
            const count = getParticleCount();
            const speed = getBaseSpeed();

            for (let i = 0; i < count; i++) {
                const vx = (Math.random() - 0.5) * speed;
                const vy = (Math.random() - 0.5) * speed;

                // 5 Specialized Multi-Agent Intelligence Tiers
                let tier = 'matrix';
                let r = Math.random() * 0.5 + 0.9; // 0.9 - 1.4px
                let opacity = Math.random() * 0.20 + 0.38;
                let color = { r: 250, g: 240, b: 255 };
                let shadowColor = 'rgba(255, 255, 255, 0.3)';
                let shadowBlur = 4;

                if (i % 14 === 0) {
                    tier = 'solar_beacon'; // Multi-Agent Pipeline Core
                    r = Math.random() * 0.8 + 3.2;
                    opacity = 0.95;
                    color = { r: 255, g: 155, b: 50 };
                    shadowColor = 'rgba(255, 126, 41, 0.75)';
                    shadowBlur = 15;
                } else if (i % 6 === 0) {
                    tier = 'researcher'; // MCP Retrieval Nodes
                    r = Math.random() * 0.6 + 2.2;
                    opacity = 0.85;
                    color = { r: 255, g: 175, b: 85 };
                    shadowColor = 'rgba(255, 140, 50, 0.6)';
                    shadowBlur = 11;
                } else if (i % 10 === 0) {
                    tier = 'critic'; // Evaluation Nodes
                    r = Math.random() * 0.5 + 2.0;
                    opacity = 0.82;
                    color = { r: 180, g: 115, b: 255 };
                    shadowColor = 'rgba(168, 85, 247, 0.65)';
                    shadowBlur = 10;
                } else if (i % 12 === 0) {
                    tier = 'verifier'; // Fact-Check Nodes
                    r = Math.random() * 0.5 + 1.9;
                    opacity = 0.80;
                    color = { r: 45, g: 212, b: 191 };
                    shadowColor = 'rgba(45, 212, 191, 0.6)';
                    shadowBlur = 10;
                }

                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: vx,
                    vy: vy,
                    baseVx: vx,
                    baseVy: vy,
                    r: r,
                    opacity: opacity,
                    tier: tier,
                    color: color,
                    shadowColor: shadowColor,
                    shadowBlur: shadowBlur,
                    hoverBoost: 0,
                    pulsePhase: Math.random() * Math.PI * 2
                });
            }
        }

        function spawnSignalPulse() {
            if (pulses.length >= 7 || particles.length < 2) return;
            const activeParticles = particles.filter(p => p.tier !== 'matrix');
            if (activeParticles.length < 2) return;
            const from = activeParticles[Math.floor(Math.random() * activeParticles.length)];
            const connectionDist = getConnectionDistance();

            const candidates = [];
            for (let i = 0; i < activeParticles.length; i++) {
                const c = activeParticles[i];
                if (c === from) continue;
                const dx = from.x - c.x;
                const dy = from.y - c.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < connectionDist && dist > 20) {
                    candidates.push(c);
                }
            }

            if (candidates.length > 0) {
                const to = candidates[Math.floor(Math.random() * candidates.length)];
                let color = 'rgba(255, 175, 85, 0.95)';
                let glowColor = 'rgba(255, 126, 41, 0.8)';

                if (from.tier === 'critic' || to.tier === 'critic') {
                    color = 'rgba(216, 180, 254, 0.95)';
                    glowColor = 'rgba(168, 85, 247, 0.8)';
                } else if (from.tier === 'verifier' || to.tier === 'verifier') {
                    color = 'rgba(125, 245, 240, 0.95)';
                    glowColor = 'rgba(20, 184, 166, 0.8)';
                } else if (from.tier === 'solar_beacon' || to.tier === 'solar_beacon') {
                    color = 'rgba(255, 220, 130, 0.98)';
                    glowColor = 'rgba(255, 155, 50, 0.9)';
                }

                pulses.push({
                    from,
                    to,
                    progress: 0,
                    speed: Math.random() * 0.012 + 0.010,
                    color,
                    glowColor,
                    size: Math.random() * 0.6 + 1.8
                });
            }
        }

        function draw() {
            if (canvas.width <= 10 || canvas.height <= 10) {
                resize();
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            globalTick++;

            const connectionDist = getConnectionDistance();

            // Smooth physics interpolation for interactive cursor glow
            if (mouse.active && mouse.x !== null) {
                if (smoothMouse.x === null) {
                    smoothMouse.x = mouse.x;
                    smoothMouse.y = mouse.y;
                } else {
                    smoothMouse.x += (mouse.x - smoothMouse.x) * 0.16;
                    smoothMouse.y += (mouse.y - smoothMouse.y) * 0.16;
                }
                mouseIntensity += (1 - mouseIntensity) * 0.08;
            } else {
                mouseIntensity += (0 - mouseIntensity) * 0.05;
                if (mouseIntensity < 0.005) {
                    smoothMouse.x = null;
                    smoothMouse.y = null;
                }
            }

            // 1. Ambient Orange Aurora Glow Following Cursor
            if (mouseIntensity > 0.01 && smoothMouse.x !== null) {
                const lanternRadius = 220;
                const lanternGrad = ctx.createRadialGradient(
                    smoothMouse.x, smoothMouse.y, 0,
                    smoothMouse.x, smoothMouse.y, lanternRadius
                );
                lanternGrad.addColorStop(0, `rgba(255, 140, 50, ${(0.16 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(0.35, `rgba(255, 105, 30, ${(0.08 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(0.65, `rgba(139, 92, 246, ${(0.035 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');

                ctx.save();
                ctx.fillStyle = lanternGrad;
                ctx.beginPath();
                ctx.arc(smoothMouse.x, smoothMouse.y, lanternRadius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // Warm glowing cursor starlight anchor
                ctx.save();
                ctx.beginPath();
                ctx.arc(smoothMouse.x, smoothMouse.y, 2.6, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 225, 150, ${(0.92 * mouseIntensity).toFixed(3)})`;
                ctx.shadowColor = 'rgba(255, 140, 50, 0.85)';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            // 2. Multi-Agent Synaptic Lattice Filaments (Constellation network between nodes)
            for (let i = 0; i < particles.length; i++) {
                const p1 = particles[i];

                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < connectionDist) {
                        const alphaFactor = 1 - (dist / connectionDist);

                        // Subtle attenuation in primary reading zone for text crispness
                        let textAtten = 1.0;
                        const midX = (p1.x + p2.x) * 0.5;
                        const midY = (p1.y + p2.y) * 0.5;
                        if (midX < canvas.width * 0.48 && midY < canvas.height * 0.58) {
                            textAtten = 0.55;
                        }

                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);

                        if (p1.tier === 'critic' || p2.tier === 'critic') {
                            ctx.strokeStyle = `rgba(168, 85, 247, ${(alphaFactor * 0.24 * textAtten).toFixed(3)})`;
                            ctx.lineWidth = 0.75;
                        } else if (p1.tier === 'verifier' || p2.tier === 'verifier') {
                            ctx.strokeStyle = `rgba(45, 212, 191, ${(alphaFactor * 0.22 * textAtten).toFixed(3)})`;
                            ctx.lineWidth = 0.75;
                        } else if (p1.tier === 'solar_beacon' || p2.tier === 'solar_beacon') {
                            ctx.strokeStyle = `rgba(255, 155, 60, ${(alphaFactor * 0.30 * textAtten).toFixed(3)})`;
                            ctx.lineWidth = 0.9;
                        } else {
                            ctx.strokeStyle = `rgba(255, 165, 85, ${(alphaFactor * 0.18 * textAtten).toFixed(3)})`;
                            ctx.lineWidth = 0.65;
                        }

                        ctx.stroke();
                    }
                }
            }

            // 3. Mouse Proximity Synaptic Glow Connections (Screen 0 style, anchored to glowing cursor)
            if (mouseIntensity > 0.01 && smoothMouse.x !== null && canvas.width > 768) {
                const mouseRange = 140;
                for (let i = 0; i < particles.length; i++) {
                    const p = particles[i];
                    const dx = p.x - smoothMouse.x;
                    const dy = p.y - smoothMouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouseRange) {
                        const mAlpha = (1 - dist / mouseRange) * mouseIntensity;
                        ctx.beginPath();
                        ctx.moveTo(smoothMouse.x, smoothMouse.y);
                        ctx.lineTo(p.x, p.y);
                        // Micro/matrix gets subtle filament, prominent agent nodes get exact Screen 0 0.35 alpha
                        const lineAlpha = p.tier === 'matrix' ? mAlpha * 0.22 : mAlpha * 0.35;
                        ctx.strokeStyle = `rgba(255, 160, 60, ${lineAlpha.toFixed(3)})`;
                        ctx.lineWidth = 0.9;
                        ctx.stroke();
                    }
                }
            }

            // 4. Dynamic Multi-Agent Signal Pulses (Streaming Intelligence Packets)
            pulseTimer++;
            if (pulseTimer % 24 === 0) {
                spawnSignalPulse();
            }

            for (let i = pulses.length - 1; i >= 0; i--) {
                const pulse = pulses[i];
                pulse.progress += pulse.speed;

                if (pulse.progress >= 1) {
                    pulses.splice(i, 1);
                    continue;
                }

                const px = pulse.from.x + (pulse.to.x - pulse.from.x) * pulse.progress;
                const py = pulse.from.y + (pulse.to.y - pulse.from.y) * pulse.progress;

                ctx.save();
                ctx.beginPath();
                ctx.arc(px, py, pulse.size, 0, Math.PI * 2);
                ctx.fillStyle = pulse.color;
                ctx.shadowColor = pulse.glowColor;
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            // 5. Mouse Interactive Vortex / Swirl (Fluid constellation physics matching Screen 0)
            if (mouseIntensity > 0.01 && smoothMouse.x !== null && canvas.width > 768) {
                for (let i = 0; i < particles.length; i++) {
                    const pi = particles[i];
                    const dx = pi.x - smoothMouse.x;
                    const dy = pi.y - smoothMouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    const vortexRadius = 88;
                    const eyeRadius = 24;

                    if (dist < vortexRadius && dist > 1) {
                        const factor = (1 - dist / vortexRadius) * mouseIntensity;
                        const tangentX = -dy / dist;
                        const tangentY = dx / dist;
                        const swirlSpeed = factor * factor * 3.4;

                        let radialForce = 0;
                        if (dist > eyeRadius) {
                            radialForce = -factor * 1.5;
                        } else {
                            radialForce = ((eyeRadius - dist) / eyeRadius) * 2.2 * mouseIntensity;
                        }

                        const radialX = dx / dist;
                        const radialY = dy / dist;

                        pi.vx += tangentX * swirlSpeed + radialX * radialForce;
                        pi.vy += tangentY * swirlSpeed + radialY * radialForce;
                    }
                }
            }

            // 6. Update Particle Velocities & Draw Nodes (Clean, natural, no excessive inflation)
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];

                // Base velocity relaxation & speed clamping (matching Screen 0)
                p.vx = p.vx * 0.93 + p.baseVx * 0.07;
                p.vy = p.vy * 0.93 + p.baseVy * 0.07;

                const curSpeed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                const maxSpeed = 4.2;
                if (curSpeed > maxSpeed) {
                    p.vx = (p.vx / curSpeed) * maxSpeed;
                    p.vy = (p.vy / curSpeed) * maxSpeed;
                }

                p.x += p.vx;
                p.y += p.vy;

                // Screen boundary wrapping
                if (p.x < -18) p.x = canvas.width + 18;
                if (p.x > canvas.width + 18) p.x = -18;
                if (p.y < -18) p.y = canvas.height + 18;
                if (p.y > canvas.height + 18) p.y = -18;

                // Gentle cosmic breathing (matching Screen 0)
                const pulse = Math.sin(globalTick * 0.025 + p.pulsePhase);
                let currentR = p.r + pulse * 0.25;
                let currentAlpha = p.opacity + pulse * 0.08;

                // Contrast preservation in hero reading zone
                if (p.x < canvas.width * 0.48 && p.y < canvas.height * 0.58) {
                    currentAlpha *= 0.65;
                }

                ctx.save();
                ctx.beginPath();
                ctx.arc(p.x, p.y, Math.max(0.4, currentR), 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${Math.min(1, Math.max(0, currentAlpha)).toFixed(3)})`;

                // Halation & glow
                ctx.shadowColor = p.shadowColor;
                ctx.shadowBlur = p.shadowBlur;
                ctx.fill();
                ctx.restore();
            }

            animId = requestAnimationFrame(draw);
        }

        window.addEventListener('resize', resize);

        window.addEventListener('mousemove', (e) => {
            if (!canvas) return;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (x >= -40 && x <= rect.width + 40 && y >= -40 && y <= rect.height + 40) {
                mouse.x = x;
                mouse.y = y;
                mouse.active = true;
            } else {
                mouse.active = false;
            }
        });

        window.addEventListener('mouseleave', () => {
            mouse.active = false;
        });

        // Lifecycle observer: run whenever authenticated view is active (across both Search & Results)
        let isRunning = false;
        function updateRunningState() {
            const authView = document.getElementById('view-authenticated');
            const shouldRun = authView && !authView.classList.contains('hidden');

            if (shouldRun) {
                resize();
                if (!isRunning) {
                    animId = requestAnimationFrame(draw);
                    isRunning = true;
                }
            } else if (!shouldRun && isRunning) {
                cancelAnimationFrame(animId);
                isRunning = false;
            }
        }

        const observer = new MutationObserver(updateRunningState);
        const authView = document.getElementById('view-authenticated');
        if (authView) observer.observe(authView, { attributes: true, attributeFilter: ['class'] });
        const searchStage = document.getElementById('stage-search');
        if (searchStage) observer.observe(searchStage, { attributes: true, attributeFilter: ['class'] });
        const resultsStage = document.getElementById('stage-results');
        if (resultsStage) observer.observe(resultsStage, { attributes: true, attributeFilter: ['class'] });

        // Initial check
        updateRunningState();
    }

    // -------------------------------------------------------------------------
    // Modal Neural Galaxy Canvas (Mid-Screen Execution Pipeline Constellation)
    // -------------------------------------------------------------------------
    function initModalNeuralCanvas() {
        const canvas = document.getElementById('modal-neural-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let animId;
        let particles = [];
        let pulses = [];
        let pulseTimer = 0;
        let globalTick = 0;
        let isRunning = false;

        // Mouse tracking & smooth physics for ambient cursor glow in modal
        const mouse = { x: null, y: null, active: false };
        const smoothMouse = { x: null, y: null };
        let mouseIntensity = 0;

        function getParticleCount() {
            const area = canvas.width * canvas.height;
            return Math.min(85, Math.max(45, Math.floor(area / 16000)));
        }

        function getConnectionDistance() {
            return canvas.width > 768 ? 150 : 100;
        }

        function getBaseSpeed() {
            return canvas.width > 768 ? 0.28 : 0.20;
        }

        function resize() {
            if (!canvas) return;
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            createParticles();
        }

        function createParticles() {
            particles = [];
            pulses = [];
            const count = getParticleCount();
            const speed = getBaseSpeed();

            for (let i = 0; i < count; i++) {
                const vx = (Math.random() - 0.5) * speed;
                const vy = (Math.random() - 0.5) * speed;

                let tier = 'matrix';
                let r = Math.random() * 0.5 + 0.9;
                let opacity = Math.random() * 0.20 + 0.40;
                let color = { r: 250, g: 240, b: 255 };
                let shadowColor = 'rgba(255, 255, 255, 0.3)';
                let shadowBlur = 4;

                if (i % 12 === 0) {
                    tier = 'solar_beacon';
                    r = Math.random() * 0.8 + 3.2;
                    opacity = 0.95;
                    color = { r: 255, g: 155, b: 50 };
                    shadowColor = 'rgba(255, 126, 41, 0.75)';
                    shadowBlur = 15;
                } else if (i % 5 === 0) {
                    tier = 'researcher';
                    r = Math.random() * 0.6 + 2.2;
                    opacity = 0.85;
                    color = { r: 255, g: 175, b: 85 };
                    shadowColor = 'rgba(255, 140, 50, 0.6)';
                    shadowBlur = 11;
                } else if (i % 8 === 0) {
                    tier = 'critic';
                    r = Math.random() * 0.5 + 2.0;
                    opacity = 0.82;
                    color = { r: 180, g: 115, b: 255 };
                    shadowColor = 'rgba(168, 85, 247, 0.65)';
                    shadowBlur = 10;
                } else if (i % 10 === 0) {
                    tier = 'verifier';
                    r = Math.random() * 0.5 + 1.9;
                    opacity = 0.80;
                    color = { r: 45, g: 212, b: 191 };
                    shadowColor = 'rgba(45, 212, 191, 0.6)';
                    shadowBlur = 10;
                }

                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx, vy,
                    baseVx: vx, baseVy: vy,
                    r, opacity,
                    color, shadowColor, shadowBlur,
                    tier,
                    pulsePhase: Math.random() * Math.PI * 2
                });
            }
        }

        function spawnSignalPulse() {
            if (particles.length < 2) return;
            const connectionDist = getConnectionDistance();
            const candidates = [];

            for (let i = 0; i < particles.length; i++) {
                const p1 = particles[i];
                if (p1.tier === 'matrix') continue;
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < connectionDist) {
                        candidates.push({ from: p1, to: p2 });
                    }
                }
            }

            if (candidates.length > 0) {
                const pair = candidates[Math.floor(Math.random() * candidates.length)];
                const from = Math.random() > 0.5 ? pair.from : pair.to;
                const to = from === pair.from ? pair.to : pair.from;

                let color = 'rgba(255, 200, 110, 0.95)';
                let glowColor = 'rgba(255, 126, 41, 0.85)';

                if (from.tier === 'critic' || to.tier === 'critic') {
                    color = 'rgba(216, 180, 254, 0.95)';
                    glowColor = 'rgba(168, 85, 247, 0.8)';
                } else if (from.tier === 'verifier' || to.tier === 'verifier') {
                    color = 'rgba(125, 245, 240, 0.95)';
                    glowColor = 'rgba(20, 184, 166, 0.8)';
                } else if (from.tier === 'solar_beacon' || to.tier === 'solar_beacon') {
                    color = 'rgba(255, 220, 130, 0.98)';
                    glowColor = 'rgba(255, 155, 50, 0.9)';
                }

                pulses.push({
                    from, to,
                    progress: 0,
                    speed: Math.random() * 0.012 + 0.010,
                    color, glowColor,
                    size: Math.random() * 0.6 + 1.8
                });
            }
        }

        function draw() {
            if (canvas.width <= 10 || canvas.height <= 10) {
                resize();
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            globalTick++;

            const connectionDist = getConnectionDistance();

            // Smooth physics interpolation for interactive cursor glow
            if (mouse.active && mouse.x !== null) {
                if (smoothMouse.x === null) {
                    smoothMouse.x = mouse.x;
                    smoothMouse.y = mouse.y;
                } else {
                    smoothMouse.x += (mouse.x - smoothMouse.x) * 0.16;
                    smoothMouse.y += (mouse.y - smoothMouse.y) * 0.16;
                }
                mouseIntensity += (1 - mouseIntensity) * 0.08;
            } else {
                mouseIntensity += (0 - mouseIntensity) * 0.05;
                if (mouseIntensity < 0.005) {
                    smoothMouse.x = null;
                    smoothMouse.y = null;
                }
            }

            // 1. Ambient Orange Aurora Glow Following Cursor
            if (mouseIntensity > 0.01 && smoothMouse.x !== null) {
                const lanternRadius = 240;
                const lanternGrad = ctx.createRadialGradient(
                    smoothMouse.x, smoothMouse.y, 0,
                    smoothMouse.x, smoothMouse.y, lanternRadius
                );
                lanternGrad.addColorStop(0, `rgba(255, 140, 50, ${(0.18 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(0.35, `rgba(255, 105, 30, ${(0.09 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(0.65, `rgba(139, 92, 246, ${(0.04 * mouseIntensity).toFixed(4)})`);
                lanternGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');

                ctx.save();
                ctx.fillStyle = lanternGrad;
                ctx.beginPath();
                ctx.arc(smoothMouse.x, smoothMouse.y, lanternRadius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // Warm glowing cursor starlight anchor
                ctx.save();
                ctx.beginPath();
                ctx.arc(smoothMouse.x, smoothMouse.y, 2.6, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 225, 150, ${(0.92 * mouseIntensity).toFixed(3)})`;
                ctx.shadowColor = 'rgba(255, 140, 50, 0.85)';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            // 2. Multi-Agent Synaptic Lattice Filaments
            for (let i = 0; i < particles.length; i++) {
                const p1 = particles[i];
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < connectionDist) {
                        const alphaFactor = 1 - (dist / connectionDist);

                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);

                        if (p1.tier === 'critic' || p2.tier === 'critic') {
                            ctx.strokeStyle = `rgba(168, 85, 247, ${(alphaFactor * 0.26).toFixed(3)})`;
                            ctx.lineWidth = 0.8;
                        } else if (p1.tier === 'verifier' || p2.tier === 'verifier') {
                            ctx.strokeStyle = `rgba(45, 212, 191, ${(alphaFactor * 0.24).toFixed(3)})`;
                            ctx.lineWidth = 0.8;
                        } else if (p1.tier === 'solar_beacon' || p2.tier === 'solar_beacon') {
                            ctx.strokeStyle = `rgba(255, 155, 60, ${(alphaFactor * 0.32).toFixed(3)})`;
                            ctx.lineWidth = 0.95;
                        } else {
                            ctx.strokeStyle = `rgba(255, 165, 85, ${(alphaFactor * 0.20).toFixed(3)})`;
                            ctx.lineWidth = 0.7;
                        }
                        ctx.stroke();
                    }
                }
            }

            // 3. Mouse Proximity Synaptic Glow Connections
            if (mouseIntensity > 0.01 && smoothMouse.x !== null && canvas.width > 768) {
                const mouseRange = 145;
                for (let i = 0; i < particles.length; i++) {
                    const p = particles[i];
                    const dx = p.x - smoothMouse.x;
                    const dy = p.y - smoothMouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouseRange) {
                        const mAlpha = (1 - dist / mouseRange) * mouseIntensity;
                        ctx.beginPath();
                        ctx.moveTo(smoothMouse.x, smoothMouse.y);
                        ctx.lineTo(p.x, p.y);
                        const lineAlpha = p.tier === 'matrix' ? mAlpha * 0.24 : mAlpha * 0.38;
                        ctx.strokeStyle = `rgba(255, 160, 60, ${lineAlpha.toFixed(3)})`;
                        ctx.lineWidth = 0.95;
                        ctx.stroke();
                    }
                }
            }

            // 4. Dynamic Multi-Agent Signal Pulses
            pulseTimer++;
            if (pulseTimer % 24 === 0) {
                spawnSignalPulse();
            }

            for (let i = pulses.length - 1; i >= 0; i--) {
                const pulse = pulses[i];
                pulse.progress += pulse.speed;

                if (pulse.progress >= 1) {
                    pulses.splice(i, 1);
                    continue;
                }

                const px = pulse.from.x + (pulse.to.x - pulse.from.x) * pulse.progress;
                const py = pulse.from.y + (pulse.to.y - pulse.from.y) * pulse.progress;

                ctx.save();
                ctx.beginPath();
                ctx.arc(px, py, pulse.size, 0, Math.PI * 2);
                ctx.fillStyle = pulse.color;
                ctx.shadowColor = pulse.glowColor;
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            // 5. Mouse Interactive Vortex / Swirl
            if (mouseIntensity > 0.01 && smoothMouse.x !== null && canvas.width > 768) {
                for (let i = 0; i < particles.length; i++) {
                    const pi = particles[i];
                    const dx = pi.x - smoothMouse.x;
                    const dy = pi.y - smoothMouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    const vortexRadius = 90;
                    const eyeRadius = 24;

                    if (dist < vortexRadius && dist > 1) {
                        const factor = (1 - dist / vortexRadius) * mouseIntensity;
                        const tangentX = -dy / dist;
                        const tangentY = dx / dist;
                        const swirlSpeed = factor * factor * 3.4;

                        let radialForce = 0;
                        if (dist > eyeRadius) {
                            radialForce = -factor * 1.5;
                        } else {
                            radialForce = ((eyeRadius - dist) / eyeRadius) * 2.2 * mouseIntensity;
                        }

                        pi.vx += tangentX * swirlSpeed + (dx / dist) * radialForce;
                        pi.vy += tangentY * swirlSpeed + (dy / dist) * radialForce;
                    }
                }
            }

            // 6. Update Particle Velocities & Draw Nodes
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];

                p.vx = p.vx * 0.93 + p.baseVx * 0.07;
                p.vy = p.vy * 0.93 + p.baseVy * 0.07;

                const curSpeed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                const maxSpeed = 4.2;
                if (curSpeed > maxSpeed) {
                    p.vx = (p.vx / curSpeed) * maxSpeed;
                    p.vy = (p.vy / curSpeed) * maxSpeed;
                }

                p.x += p.vx;
                p.y += p.vy;

                if (p.x < -18) p.x = canvas.width + 18;
                if (p.x > canvas.width + 18) p.x = -18;
                if (p.y < -18) p.y = canvas.height + 18;
                if (p.y > canvas.height + 18) p.y = -18;

                const pulse = Math.sin(globalTick * 0.025 + p.pulsePhase);
                const currentR = p.r + pulse * 0.25;
                const currentAlpha = p.opacity + pulse * 0.08;

                ctx.save();
                ctx.beginPath();
                ctx.arc(p.x, p.y, Math.max(0.4, currentR), 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${Math.min(1, Math.max(0, currentAlpha)).toFixed(3)})`;
                ctx.shadowColor = p.shadowColor;
                ctx.shadowBlur = p.shadowBlur;
                ctx.fill();
                ctx.restore();
            }

            animId = requestAnimationFrame(draw);
        }

        function start() {
            const modalEl = document.getElementById('running-modal');
            if (!modalEl || modalEl.classList.contains('hidden')) return;
            resize();
            if (!isRunning) {
                animId = requestAnimationFrame(draw);
                isRunning = true;
            }
        }

        function stop() {
            if (isRunning) {
                cancelAnimationFrame(animId);
                isRunning = false;
            }
        }

        window.addEventListener('resize', () => {
            if (isRunning) resize();
        });

        window.addEventListener('mousemove', (e) => {
            const modalEl = document.getElementById('running-modal');
            if (!modalEl || modalEl.classList.contains('hidden')) {
                mouse.active = false;
                return;
            }
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            mouse.active = true;
        });

        window.addEventListener('mouseleave', () => {
            mouse.active = false;
        });

        // Watch for modal visibility changes
        const modalEl = document.getElementById('running-modal');
        if (modalEl) {
            const observer = new MutationObserver(() => {
                if (modalEl.classList.contains('hidden')) {
                    stop();
                } else {
                    start();
                }
            });
            observer.observe(modalEl, { attributes: true, attributeFilter: ['class'] });
        }

        window.startModalNeuralCanvas = start;
        window.stopModalNeuralCanvas = stop;
    }

    // Initialize canvases
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initParticleCanvas();
            initStageNeuralCanvas();
            initModalNeuralCanvas();
        });
    } else {
        initParticleCanvas();
        initStageNeuralCanvas();
        initModalNeuralCanvas();
    }

    // -------------------------------------------------------------------------
    // State & Constants
    // -------------------------------------------------------------------------
    const SPINNER_MESSAGES = [
        'Planning focused research questions...',
        'Investigating sub-questions in parallel...',
        'Synthesizing raw findings into draft report...',
        'Evaluating draft and routing revisions...',
        'Independently cross-verifying key claims...'
    ];

    const state = {
        token: localStorage.getItem('rm_token') || null,
        history: JSON.parse(localStorage.getItem('rm_history') || '[]'),
        currentResults: null,
        running: false,
        timerInterval: null,
        statusInterval: null,
        startTime: null
    };

    // -------------------------------------------------------------------------
    // DOM Elements
    // -------------------------------------------------------------------------
    const dom = {
        // Screens
        viewLogin: document.getElementById('view-login'),
        viewAuth: document.getElementById('view-authenticated'),
        stageSearch: document.getElementById('stage-search'),
        stageResults: document.getElementById('stage-results'),

        // Login
        loginForm: document.getElementById('login-form'),
        usernameInput: document.getElementById('username'),
        passwordInput: document.getElementById('password'),
        loginError: document.getElementById('login-error'),
        loginSpinner: document.getElementById('login-spinner'),
        btnLoginSubmit: document.getElementById('btn-login-submit'),
        btnTogglePassword: document.getElementById('btn-toggle-password'),

        // Sidebar
        sidebar: document.getElementById('app-sidebar'),
        sidebarBackdrop: document.getElementById('sidebar-backdrop'),
        btnProminentOpenSidebar: document.getElementById('btn-prominent-open-sidebar'),
        btnCollapseSidebar: document.getElementById('btn-prominent-open-sidebar'),
        btnCollapseSidebarRail: document.getElementById('btn-collapse-sidebar-rail'),
        btnSidebarNewSearch: document.getElementById('btn-sidebar-new-search'),
        btnExpandSidebar: document.getElementById('btn-expand-sidebar'),
        btnExpandSidebarResults: document.getElementById('btn-expand-sidebar-results'),
        sidebarHistory: document.getElementById('sidebar-history-container'),
        historyList: document.getElementById('history-list'),
        historyCountBadge: document.getElementById('history-count-badge'),
        btnClearHistory: document.getElementById('btn-clear-history'),
        btnLogout: document.getElementById('btn-logout'),

        // Search Stage
        researchForm: document.getElementById('research-form'),
        topicInput: document.getElementById('research-topic'),
        btnClearTopic: document.getElementById('btn-clear-topic'),
        btnRunPipeline: document.getElementById('btn-run-pipeline'),
        sampleChips: document.querySelectorAll('.chip-btn'),
        mainStage: document.querySelector('.app-main-stage'),

        // Running Modal
        runningModal: document.getElementById('running-modal'),
        runningViewProgress: document.getElementById('running-view-progress'),
        runningViewClarify: document.getElementById('running-view-clarify'),
        runningTopicDisplay: document.getElementById('running-topic-display'),
        liveTimer: document.getElementById('live-timer'),
        runningStatusMessage: document.getElementById('running-status-message'),

        // Results Stage
        btnBackToSearch: document.getElementById('btn-back-to-search'),
        btnPrintReport: document.getElementById('btn-print-report'),
        resultsSynthesisStatusText: document.getElementById('results-synthesis-status-text'),
        reportPipelineTime: document.getElementById('report-pipeline-time'),
        reportPipelineTimeText: document.getElementById('report-pipeline-time-text'),
        clarifyingContainer: document.getElementById('clarifying-container'),
        clarifyingQuestionText: document.getElementById('clarifying-question-text'),
        btnClarifyTryAgain: document.getElementById('btn-clarify-try-again'),
        clarifyInlineTopicInput: document.getElementById('clarify-inline-topic-input'),
        btnClarifyInlineSubmit: document.getElementById('btn-clarify-inline-submit'),

        // Topic Clarification Elements (In-Card View)
        btnCloseClarifyModal: document.getElementById('btn-close-clarify-modal'),
        btnClarifyModalCancel: document.getElementById('btn-clarify-modal-cancel'),
        btnClarifyModalSubmit: document.getElementById('btn-clarify-modal-submit'),
        modalClarifyForm: document.getElementById('clarify-modal-form'),
        modalClarifyTopicInput: document.getElementById('modal-clarify-topic-input'),
        btnClearClarifyModalTopic: document.getElementById('btn-clear-clarify-modal-topic'),
        modalClarifyingQuestionText: document.getElementById('modal-clarifying-question-text'),

        reportPayloadContainer: document.getElementById('report-payload-container'),
        resultsTopicTitle: document.getElementById('results-topic-title'),
        metricScore: document.getElementById('metric-score'),
        metricVerification: document.getElementById('metric-verification'),
        metricTracks: document.getElementById('metric-tracks'),
        metricTokens: document.getElementById('metric-tokens'),
        metricIterations: document.getElementById('metric-iterations'),
        subquestionsContainer: document.getElementById('subquestions-container'),
        subquestionsToggleBtn: document.getElementById('subquestions-toggle-btn'),
        subquestionsCount: document.getElementById('subquestions-count'),
        subquestionsList: document.getElementById('subquestions-list'),

        // Report Launcher Bar & Modal Elements
        reportLauncherBar: document.getElementById('report-launcher-bar'),
        launcherWordCount: document.getElementById('launcher-word-count'),
        btnOpenReportModal: document.getElementById('btn-open-report-modal'),
        modalReportViewer: document.getElementById('modal-report-viewer'),
        modalReportCard: document.getElementById('report-modal-card'),
        modalReportTitle: document.getElementById('modal-report-title'),
        modalReportMeta: document.getElementById('modal-report-meta'),
        modalReportContent: document.getElementById('modal-report-rendered-content'),
        btnModalCopyMarkdown: document.getElementById('btn-modal-copy-markdown'),
        btnModalDownloadMarkdown: document.getElementById('btn-modal-download-markdown'),
        btnCloseReportModal: document.getElementById('btn-close-report-modal'),
        btnFooterCloseReportModal: document.getElementById('btn-footer-close-report-modal'),

        verificationContent: document.getElementById('verification-content'),
        criticContent: document.getElementById('critic-content'),
        reportRequestId: document.getElementById('report-request-id'),
        btnCopyMarkdown: document.getElementById('btn-copy-markdown'),
        btnDownloadMarkdown: document.getElementById('btn-download-markdown'),

        // Toast
        toast: document.getElementById('toast-notification')
    };

    // -------------------------------------------------------------------------
    // Initialization & Routing
    // -------------------------------------------------------------------------
    function init() {
        attachEventListeners();
        renderHistory();

        // Default sidebar to collapsed by default
        const savedCollapsed = localStorage.getItem('rm_sidebar_collapsed_v2');
        if (savedCollapsed === 'false') {
            toggleSidebar(false);
        } else {
            toggleSidebar(true);
        }

        updateRunButtonState();

        if (window.location.search.includes('mock=1') || window.location.hash === '#results') {
            state.token = 'demo-token';
            localStorage.setItem('rm_token', 'demo-token');
            const mockData = {
                topic: 'Fault-Tolerant Quantum Computing: Architectural Synthesis & Hardware Roadmaps (2025–2030)',
                report: '# Fault-Tolerant Quantum Computing\n\nExecutive research synthesis report content.',
                critic_score: 9.4,
                feedback: 'Score: 9.4/10\nRigorous technical depth across logical qubit topologies.',
                verification: '18/18 claims fully supported by arXiv and peer-reviewed literature.',
                sub_questions: [
                    'What are the latest coherence time breakthroughs in topological and cat-qubit systems?',
                    'How do surface code thresholds compare to bivariate bicycle LDPC error correction codes?',
                    'What are the current hardware roadmaps from Quantinuum, IBM, and Google Quantum AI for fault-tolerant logical qubits?'
                ],
                tokens_used: 14820,
                iteration_count: 1,
                execution_time_seconds: 20,
                request_id: 'req_sim_demo'
            };
            state.currentResults = mockData;
            showAuthenticatedView();
            renderResults(mockData);
            showResultsStage();
            return;
        }

        if (state.token) {
            showAuthenticatedView();
        } else {
            showLoginView();
        }
    }

    function toggleSidebar(forceState) {
        if (!dom.sidebar) return;
        const willCollapse = forceState !== undefined ? forceState : !dom.sidebar.classList.contains('collapsed');
        if (willCollapse) {
            dom.sidebar.classList.add('collapsed');
            document.body.classList.remove('sidebar-open');
            document.body.classList.add('sidebar-collapsed');
            if (dom.btnProminentOpenSidebar) {
                dom.btnProminentOpenSidebar.setAttribute('title', 'Expand Workspace (Ctrl+\\)');
                dom.btnProminentOpenSidebar.setAttribute('aria-label', 'Expand Workspace');
            }
            if (dom.btnExpandSidebar) dom.btnExpandSidebar.classList.remove('hidden');
            if (dom.btnExpandSidebarResults) dom.btnExpandSidebarResults.classList.remove('hidden');
            localStorage.setItem('rm_sidebar_collapsed_v2', 'true');
        } else {
            dom.sidebar.classList.remove('collapsed');
            document.body.classList.add('sidebar-open');
            document.body.classList.remove('sidebar-collapsed');
            if (dom.btnProminentOpenSidebar) {
                dom.btnProminentOpenSidebar.setAttribute('title', 'Collapse Workspace (Ctrl+\\)');
                dom.btnProminentOpenSidebar.setAttribute('aria-label', 'Collapse Workspace');
            }
            if (dom.btnExpandSidebar) dom.btnExpandSidebar.classList.add('hidden');
            if (dom.btnExpandSidebarResults) dom.btnExpandSidebarResults.classList.add('hidden');
            localStorage.setItem('rm_sidebar_collapsed_v2', 'false');
        }
    }

    function showLoginView() {
        dom.viewLogin.classList.remove('hidden');
        dom.viewAuth.classList.add('hidden');
        toggleSidebar(true);
    }

    async function fetchServerHistory() {
        if (!state.token || state.token === 'demo-token') return;
        try {
            const res = await fetch('/research/history', {
                headers: {
                    'Authorization': `Bearer ${state.token}`
                }
            });
            if (res.ok) {
                const list = await res.json();
                if (Array.isArray(list) && list.length > 0) {
                    state.history = list.map(item => ({
                        topic: item.topic || 'Untitled',
                        timestamp: item.timestamp || '',
                        results: item,
                        request_id: item.request_id || ''
                    }));
                    localStorage.setItem('rm_history', JSON.stringify(state.history));
                    renderHistory();
                }
            }
        } catch (e) {
            // Fall back gracefully
        }
    }

    function showAuthenticatedView() {
        dom.viewLogin.classList.add('hidden');
        dom.viewAuth.classList.remove('hidden');

        // Restore or initialize sidebar state so the open button / pull tab is always present
        const savedCollapsed = localStorage.getItem('rm_sidebar_collapsed_v2');
        if (savedCollapsed === 'false' && window.innerWidth > 768) {
            toggleSidebar(false);
        } else {
            toggleSidebar(true);
        }

        fetchServerHistory();

        const isResults = dom.stageResults && !dom.stageResults.classList.contains('hidden');
        if (isResults) {
            showResultsStage();
        } else {
            showSearchStage();
        }
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 50);
    }

    let isGuardingEmptyTopic = false;
    function triggerEmptyTopicGuard() {
        if (!dom.btnRunPipeline || !dom.topicInput) return;
        if (isGuardingEmptyTopic) return;
        isGuardingEmptyTopic = true;

        // 1. Haptic Micro-shake on the button
        dom.btnRunPipeline.classList.remove('shake-btn');
        void dom.btnRunPipeline.offsetWidth;
        dom.btnRunPipeline.classList.add('shake-btn');

        // 2. Neon Amber Attention Pulse on search input card
        if (dom.researchForm) {
            dom.researchForm.classList.remove('input-guard-pulse');
            void dom.researchForm.offsetWidth;
            dom.researchForm.classList.add('input-guard-pulse');
        }

        // 3. Focus input cursor
        dom.topicInput.focus({ preventScroll: true });

        // 4. Sleek guidance notification
        showToast('Please enter a research inquiry first');

        setTimeout(() => {
            if (dom.btnRunPipeline) dom.btnRunPipeline.classList.remove('shake-btn');
            if (dom.researchForm) dom.researchForm.classList.remove('input-guard-pulse');
            isGuardingEmptyTopic = false;
        }, 850);
    }

    function updateRunButtonState() {
        // Option 2: Run Pipeline button stays 100% vibrant, backed by interactive guard
        if (!dom.btnRunPipeline) return;
        dom.btnRunPipeline.disabled = false;
        dom.btnRunPipeline.classList.remove('btn-disabled');
    }

    function showSearchStage(shouldFocus = false) {
        dom.stageSearch.classList.remove('hidden');
        dom.stageResults.classList.add('hidden');
        if (dom.mainStage) {
            const origBehavior = dom.mainStage.style.scrollBehavior;
            dom.mainStage.style.scrollBehavior = 'auto';
            dom.mainStage.scrollTop = 0;
            dom.mainStage.classList.add('search-active');
            requestAnimationFrame(() => {
                dom.mainStage.scrollTop = 0;
                dom.mainStage.style.scrollBehavior = origBehavior;
            });
        }
        updateRunButtonState();
        if (shouldFocus && dom.topicInput) {
            dom.topicInput.focus({ preventScroll: true });
        }
        window.dispatchEvent(new Event('resize'));
    }

    function showResultsStage() {
        dom.stageSearch.classList.add('hidden');
        dom.stageResults.classList.remove('hidden');

        // Prevent browser from auto-scrolling to any previously focused element
        if (document.activeElement && typeof document.activeElement.blur === 'function') {
            document.activeElement.blur();
        }

        if (dom.mainStage) {
            dom.mainStage.classList.remove('search-active');
            
            // Temporarily disable smooth scroll so the jump to top is 100% instant and cannot be canceled
            const origBehavior = dom.mainStage.style.scrollBehavior;
            dom.mainStage.style.scrollBehavior = 'auto';
            dom.mainStage.scrollTop = 0;
            dom.mainStage.scrollTo({ top: 0, left: 0, behavior: 'instant' });

            requestAnimationFrame(() => {
                dom.mainStage.scrollTop = 0;
                dom.mainStage.scrollTo({ top: 0, left: 0, behavior: 'instant' });
                setTimeout(() => {
                    dom.mainStage.scrollTop = 0;
                    dom.mainStage.style.scrollBehavior = origBehavior;
                }, 60);
            });
        }

        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;

        window.dispatchEvent(new Event('resize'));
    }

    // -------------------------------------------------------------------------
    // Toast Notification
    // -------------------------------------------------------------------------
    let toastTimeout = null;
    function showToast(message) {
        clearTimeout(toastTimeout);
        dom.toast.textContent = message;
        dom.toast.classList.remove('hidden');
        toastTimeout = setTimeout(() => {
            dom.toast.classList.add('hidden');
        }, 3000);
    }

    // -------------------------------------------------------------------------
    // Event Listeners
    // -------------------------------------------------------------------------
    function attachEventListeners() {
        // Login Form
        dom.loginForm.addEventListener('submit', handleLogin);

        // Toggle Password Visibility
        if (dom.btnTogglePassword) {
            dom.btnTogglePassword.addEventListener('click', () => {
                const isPassword = dom.passwordInput.type === 'password';
                dom.passwordInput.type = isPassword ? 'text' : 'password';
                const eyeIcon = document.getElementById('eye-icon');
                if (eyeIcon) {
                    eyeIcon.innerHTML = isPassword
                        ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>'
                        : '<path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z"></path><circle cx="12" cy="12" r="3"></circle>';
                }
            });
        }

        // Multipurpose Sidebar Floating Dock Toggle (Open & Matching Close)
        if (dom.btnProminentOpenSidebar) {
            dom.btnProminentOpenSidebar.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleSidebar();
            });
        }
        if (dom.sidebarBackdrop) {
            dom.sidebarBackdrop.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleSidebar(true);
            });
        }
        if (dom.btnSidebarNewSearch) {
            dom.btnSidebarNewSearch.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    toggleSidebar(true);
                }
                showSearchStage(true);
            });
        }
        if (dom.btnExpandSidebar) {
            dom.btnExpandSidebar.addEventListener('click', () => toggleSidebar(false));
        }
        if (dom.btnExpandSidebarResults) {
            dom.btnExpandSidebarResults.addEventListener('click', () => toggleSidebar(false));
        }

        const btnMobileToggle = document.getElementById('btn-mobile-sidebar-toggle');
        if (btnMobileToggle) {
            btnMobileToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleSidebar();
            });
        }
        const btnMobileToggleResults = document.getElementById('btn-mobile-sidebar-toggle-results');
        if (btnMobileToggleResults) {
            btnMobileToggleResults.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleSidebar();
            });
        }

        // Close overlay sidebar when clicking outside the drawer
        document.addEventListener('click', (e) => {
            if (document.body.classList.contains('sidebar-open')) {
                if (dom.sidebar && !dom.sidebar.contains(e.target) && !e.target.closest('.btn-mobile-menu') && !e.target.closest('.btn-sidebar-toggle-top') && !e.target.closest('.btn-topbar-toggle') && !e.target.closest('#sidebar-bookmark-toggle') && !e.target.closest('#btn-prominent-open-sidebar')) {
                    toggleSidebar(true);
                }
            }
        });

        // Logout
        dom.btnLogout.addEventListener('click', handleLogout);

        // Research Form
        dom.researchForm.addEventListener('submit', handleRunPipeline);
        if (dom.btnRunPipeline) {
            dom.btnRunPipeline.addEventListener('click', (e) => {
                const topic = dom.topicInput ? dom.topicInput.value.trim() : '';
                if (!topic) {
                    e.preventDefault();
                    triggerEmptyTopicGuard();
                }
            });
        }

        // Topic input clear button handler, Enter key submission & reactive run button state
        if (dom.topicInput) {
            dom.topicInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (dom.btnRunPipeline) {
                        dom.btnRunPipeline.click();
                    } else if (dom.researchForm) {
                        dom.researchForm.requestSubmit();
                    }
                }
            });

            dom.topicInput.addEventListener('input', () => {
                const hasText = dom.topicInput.value.trim().length > 0;
                if (dom.btnClearTopic) {
                    if (hasText) {
                        dom.btnClearTopic.classList.remove('hidden');
                    } else {
                        dom.btnClearTopic.classList.add('hidden');
                    }
                }
                updateRunButtonState();
            });

            if (dom.btnClearTopic) {
                dom.btnClearTopic.addEventListener('click', () => {
                    dom.topicInput.value = '';
                    dom.btnClearTopic.classList.add('hidden');
                    updateRunButtonState();
                    dom.topicInput.focus();
                });
            }
        }

        // Sample Prompt & Topic Cards
        dom.sampleChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const topic = chip.getAttribute('data-topic');
                dom.topicInput.value = topic;
                if (dom.btnClearTopic) {
                    dom.btnClearTopic.classList.remove('hidden');
                }
                updateRunButtonState();
                dom.topicInput.focus({ preventScroll: true });
                // Smooth scroll to search form only if on narrow mobile screen
                if (window.innerWidth <= 768) {
                    dom.researchForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        });

        // Global Keyboard Shortcut:
        // - 'Ctrl+\' or 'Cmd+\' to toggle sidebar
        // - '/' or 'Cmd/Ctrl + K' to focus search
        document.addEventListener('keydown', (e) => {
            if (state.token) {
                if (e.key === '\\' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    toggleSidebar();
                    return;
                }

                if (!dom.stageSearch.classList.contains('hidden')) {
                    const isTargetInput = ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);
                    if (!isTargetInput && (e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey)))) {
                        e.preventDefault();
                        dom.topicInput.focus();
                        dom.topicInput.select();
                    }
                }
            }
        });

        // Results Actions
        dom.btnBackToSearch.addEventListener('click', showSearchStage);
        if (dom.btnClarifyTryAgain) {
            dom.btnClarifyTryAgain.addEventListener('click', () => {
                showSearchStage(true);
                if (dom.topicInput) {
                    dom.topicInput.select();
                }
            });
        }
        if (dom.btnClarifyInlineSubmit) {
            dom.btnClarifyInlineSubmit.addEventListener('click', handleClarifyInlineSubmit);
        }
        if (dom.clarifyInlineTopicInput) {
            dom.clarifyInlineTopicInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleClarifyInlineSubmit();
                }
            });
        }
        const btnBrandHome = document.getElementById('btn-brand-home');
        if (btnBrandHome) {
            btnBrandHome.addEventListener('click', () => showSearchStage());
        }
        dom.btnPrintReport.addEventListener('click', () => window.print());
        dom.btnCopyMarkdown.addEventListener('click', () => handleCopyMarkdown(dom.btnCopyMarkdown));
        dom.btnDownloadMarkdown.addEventListener('click', handleDownloadMarkdown);

        // Subquestions Accordion Toggle
        if (dom.subquestionsToggleBtn) {
            dom.subquestionsToggleBtn.addEventListener('click', toggleSubquestions);
            dom.subquestionsToggleBtn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSubquestions();
                }
            });
        }

        // Clarification Modal Handlers
        if (dom.btnCloseClarifyModal) {
            dom.btnCloseClarifyModal.addEventListener('click', closeClarifyModal);
        }
        if (dom.btnClarifyModalCancel) {
            dom.btnClarifyModalCancel.addEventListener('click', closeClarifyModal);
        }
        if (dom.modalClarifyForm) {
            dom.modalClarifyForm.addEventListener('submit', handleClarifyModalSubmit);
        }
        if (dom.modalClarifyTopicInput) {
            dom.modalClarifyTopicInput.addEventListener('input', () => {
                if (dom.btnClearClarifyModalTopic) {
                    dom.btnClearClarifyModalTopic.classList.toggle('hidden', !dom.modalClarifyTopicInput.value);
                }
            });
        }
        if (dom.btnClearClarifyModalTopic) {
            dom.btnClearClarifyModalTopic.addEventListener('click', () => {
                if (dom.modalClarifyTopicInput) {
                    dom.modalClarifyTopicInput.value = '';
                    dom.modalClarifyTopicInput.focus();
                }
                dom.btnClearClarifyModalTopic.classList.add('hidden');
            });
        }

        // Report Modal Launch & Close Handlers
        if (dom.btnOpenReportModal) {
            dom.btnOpenReportModal.addEventListener('click', openReportModal);
        }
        if (dom.reportLauncherBar) {
            dom.reportLauncherBar.addEventListener('click', (e) => {
                if (e.target.closest('#btn-copy-markdown') || e.target.closest('#btn-download-markdown')) {
                    return;
                }
                openReportModal();
            });
        }
        if (dom.btnCloseReportModal) {
            dom.btnCloseReportModal.addEventListener('click', closeReportModal);
        }
        if (dom.btnFooterCloseReportModal) {
            dom.btnFooterCloseReportModal.addEventListener('click', closeReportModal);
        }
        if (dom.btnModalCopyMarkdown) {
            dom.btnModalCopyMarkdown.addEventListener('click', () => handleCopyMarkdown(dom.btnModalCopyMarkdown));
        }
        if (dom.btnModalDownloadMarkdown) {
            dom.btnModalDownloadMarkdown.addEventListener('click', handleDownloadMarkdown);
        }
        if (dom.modalReportViewer) {
            dom.modalReportViewer.addEventListener('click', (e) => {
                if (e.target === dom.modalReportViewer) {
                    closeReportModal();
                }
            });
        }
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (dom.modalClarifyDialog && !dom.modalClarifyDialog.classList.contains('hidden')) {
                    closeClarifyModal();
                } else if (dom.modalReportViewer && !dom.modalReportViewer.classList.contains('hidden')) {
                    closeReportModal();
                }
            }
        });

        const btnCopyTopic = document.getElementById('btn-copy-topic');
        if (btnCopyTopic) {
            btnCopyTopic.addEventListener('click', () => {
                const topicText = (state.currentResults && state.currentResults.topic)
                    || (dom.resultsTopicTitle ? dom.resultsTopicTitle.textContent.trim() : '');
                if (!topicText) return;
                navigator.clipboard.writeText(topicText).then(() => {
                    showToast('Topic headline copied!');
                    const labelSpan = btnCopyTopic.querySelector('.copy-topic-text');
                    if (labelSpan) {
                        const origText = labelSpan.textContent;
                        labelSpan.textContent = 'Copied!';
                        btnCopyTopic.classList.add('copied');
                        setTimeout(() => {
                            labelSpan.textContent = origText;
                            btnCopyTopic.classList.remove('copied');
                        }, 1800);
                    }
                }).catch(() => {
                    showToast('Failed to copy topic headline');
                });
            });
        }

        const btnCopyReqId = document.getElementById('btn-copy-req-id');
        if (btnCopyReqId) {
            btnCopyReqId.addEventListener('click', () => {
                const reqId = dom.reportRequestId ? dom.reportRequestId.textContent.trim() : '';
                if (!reqId || reqId === '—') return;
                navigator.clipboard.writeText(reqId).then(() => {
                    showToast(`Copied Request ID: ${reqId}`);
                });
            });
        }

        // History Clear
        if (dom.btnClearHistory) {
            dom.btnClearHistory.addEventListener('click', async () => {
                if (!state.history || state.history.length === 0) return;
                state.history = [];
                localStorage.removeItem('rm_history');
                if (state.token && state.token !== 'demo-token') {
                    try {
                        await fetch('/research/history', {
                            method: 'DELETE',
                            headers: {
                                'Authorization': `Bearer ${state.token}`
                            }
                        });
                    } catch (e) {}
                }
                renderHistory();
                showToast('All recent enquiries cleared');
            });
        }
    }

    // -------------------------------------------------------------------------
    // Auth Handlers
    // -------------------------------------------------------------------------
    async function handleLogin(e) {
        e.preventDefault();
        const username = dom.usernameInput.value.trim();
        const password = dom.passwordInput.value;

        if (!username || !password) return;

        dom.loginError.classList.add('hidden');
        dom.loginSpinner.classList.remove('hidden');
        dom.btnLoginSubmit.querySelector('.btn-label').textContent = 'Signing in...';
        dom.btnLoginSubmit.disabled = true;

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const res = await fetch('/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            const data = await res.json();

            if (res.ok && data.access_token) {
                state.token = data.access_token;
                localStorage.setItem('rm_token', state.token);
                dom.usernameInput.value = '';
                dom.passwordInput.value = '';
                showAuthenticatedView();
                showToast('Signed in successfully');
            } else {
                showLoginError(data.detail || 'Invalid username or password.');
            }
        } catch (err) {
            showLoginError('Could not reach the server. Please try again.');
        } finally {
            dom.loginSpinner.classList.add('hidden');
            dom.btnLoginSubmit.querySelector('.btn-label').textContent = 'Sign In';
            dom.btnLoginSubmit.disabled = false;
        }
    }

    function showLoginError(msg) {
        dom.loginError.textContent = msg;
        dom.loginError.classList.remove('hidden');
    }

    function handleLogout() {
        state.token = null;
        state.currentResults = null;
        localStorage.removeItem('rm_token');
        if (dom.topicInput) {
            dom.topicInput.value = '';
        }
        if (dom.btnClearTopic) {
            dom.btnClearTopic.classList.add('hidden');
        }
        updateRunButtonState();
        toggleSidebar(true);
        showLoginView();
        showToast('Signed out');
    }

    // -------------------------------------------------------------------------
    // Research Execution Handlers
    // -------------------------------------------------------------------------
    function parseReportMarkdown(rawText) {
        const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;
        const match = rawText.match(frontmatterRegex);
        if (!match) {
            return { meta: {}, markdown: rawText };
        }
        const yamlBlock = match[1];
        const markdown = match[2];
        const meta = {};
        const lines = yamlBlock.split(/\r?\n/);
        let currentArrayKey = null;

        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('#')) continue;

            if (trimmed.startsWith('- ') && currentArrayKey) {
                meta[currentArrayKey].push(trimmed.substring(2).replace(/^["']|["']$/g, '').trim());
                continue;
            }

            const colonIdx = line.indexOf(':');
            if (colonIdx !== -1) {
                const key = line.substring(0, colonIdx).trim();
                let val = line.substring(colonIdx + 1).trim();
                val = val.replace(/\\n/g, '\n').replace(/^["']|["']$/g, '');
                if (val === '') {
                    currentArrayKey = key;
                    meta[key] = [];
                } else {
                    currentArrayKey = null;
                    meta[key] = isNaN(val) ? val : Number(val);
                }
            }
        }
        return { meta, markdown };
    }

    async function handleMockPipeline(topic) {
        // Start 20s mock simulation with 4s stage message interval
        startRunningState(topic, 4000);

        let reportText = '';
        let meta = {};
        try {
            const res = await fetch('/static/data/default_report.md');
            if (res.ok) {
                const raw = await res.text();
                const parsed = parseReportMarkdown(raw);
                meta = parsed.meta;
                reportText = parsed.markdown;
            }
        } catch (e) {
            console.warn('Could not fetch default_report.md:', e);
        }

        if (!reportText) {
            reportText = '# Default Research Report\n\nSimulation completed successfully.';
        }

        // Wait for exactly 20 seconds
        await new Promise(resolve => setTimeout(resolve, 20000));

        // Construct mock result payload matching live schema
        const mockData = {
            topic: meta.topic || (topic.charAt(0).toUpperCase() + topic.slice(1) + ': Autonomous Research Investigation'),
            report: reportText,
            critic_score: meta.critic_score != null ? meta.critic_score : 9.4,
            feedback: meta.critic_feedback || 'Score: 9.4/10\nRigorous technical depth across logical qubit topologies and error correction thresholds. Sources are thoroughly referenced and claims are substantiated.',
            verification: meta.verification || '18/18 claims fully supported by arXiv and peer-reviewed literature. Zero hallucinations detected. Citation cross-references confirmed.',
            sub_questions: meta.sub_questions || [
                'What are the latest coherence time breakthroughs in topological and cat-qubit systems?',
                'How do surface code thresholds compare to bivariate bicycle LDPC error correction codes?',
                'What are the current hardware roadmaps from Quantinuum, IBM, and Google Quantum AI for fault-tolerant logical qubits?'
            ],
            tokens_used: meta.tokens_used || 14820,
            iteration_count: meta.iteration_count || 1,
            execution_time_seconds: state.startTime ? Math.max(1, Math.round((Date.now() - state.startTime) / 1000)) : 20,
            request_id: 'req_sim_' + Math.random().toString(36).substring(2, 8)
        };

        state.currentResults = mockData;
        renderResults(mockData);
        showResultsStage();
        requestAnimationFrame(() => {
            stopRunningState(true);
        });
    }

    async function executeResearch(rawTopic) {
        const topic = (rawTopic || '').trim();
        if (!topic) {
            triggerEmptyTopicGuard();
            return;
        }

        // Check for mock keyword with ambiguous test flag "- A" (case-insensitive, e.g. "Test - A", "dEmO - a", "demo-a", "default - a")
        const mockAmbiguousMatch = topic.match(/^(default|demo|test)\s*-\s*a$/i);
        if (mockAmbiguousMatch) {
            const baseWord = mockAmbiguousMatch[1].charAt(0).toUpperCase() + mockAmbiguousMatch[1].slice(1).toLowerCase();
            const simulatedQuestion = `What specific dimension of ${baseWord} research should the multi-agent system investigate? For example: core theoretical foundations & mathematical formalisms, experimental benchmark metrics, real-world deployment challenges, or adversarial robustness & security models.`;
            
            // Brief 2.5s simulation: show running HUD with active neural canvas & stepper
            startRunningState(topic, 2500);
            await new Promise(resolve => setTimeout(resolve, 2500));

            // Morph modal card in-place to clarify view — zero modal hide/show, zero screen flicker!
            openClarifyModal(baseWord, simulatedQuestion);
            return;
        }

        // Lightweight client-side simulation shortcuts (default, demo, test)
        const MOCK_KEYWORDS = ['default', 'demo', 'test'];
        if (MOCK_KEYWORDS.includes(topic.toLowerCase())) {
            await handleMockPipeline(topic);
            return;
        }

        startRunningState(topic);

        try {
            const res = await fetch('/research/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${state.token}`
                },
                body: JSON.stringify({ topic })
            });

            const data = await res.json();

            if (res.status === 401) {
                handleLogout();
                showLoginError('Session expired. Please sign in again.');
                return;
            }

            if (!res.ok) {
                throw new Error(data.detail || 'Pipeline execution failed.');
            }

            // If the planner identified topic ambiguity, morph the modal in-place to the clarification view
            if (data.clarifying_question) {
                state.currentResults = data;
                renderResults(data);
                openClarifyModal(topic, data.clarifying_question);
                return;
            }

            // Record pipeline execution elapsed time
            data.execution_time_seconds = data.execution_time_seconds || (state.startTime ? Math.max(1, Math.round((Date.now() - state.startTime) / 1000)) : 20);

            // Save to state and history
            state.currentResults = data;
            saveToHistory(topic, data);
            renderResults(data);
            showResultsStage();
            requestAnimationFrame(() => {
                stopRunningState(true);
            });
        } catch (err) {
            stopRunningState(false);
            showToast(`Error: ${err.message}`);
            alert(`Research pipeline error: ${err.message}`);
        }
    }

    async function handleRunPipeline(e) {
        if (e && e.preventDefault) e.preventDefault();
        const topic = dom.topicInput ? dom.topicInput.value.trim() : '';
        await executeResearch(topic);
    }

    async function handleClarifyModalSubmit(e) {
        if (e && e.preventDefault) e.preventDefault();
        const refinedTopic = dom.modalClarifyTopicInput ? dom.modalClarifyTopicInput.value.trim() : '';
        if (!refinedTopic) {
            if (dom.modalClarifyTopicInput) dom.modalClarifyTopicInput.focus();
            return;
        }

        // Update search input in background
        if (dom.topicInput) {
            dom.topicInput.value = refinedTopic;
            if (dom.btnClearTopic) {
                dom.btnClearTopic.classList.remove('hidden');
            }
        }

        // Check if refined topic is mock keyword or mock ambiguous
        const isMockAmbiguous = refinedTopic.match(/^(default|demo|test)\s*-\s*a$/i);
        const MOCK_KEYWORDS = ['default', 'demo', 'test'];
        const isMockKeyword = MOCK_KEYWORDS.includes(refinedTopic.toLowerCase());

        // Instantly flip view back to progress in-place inside the SAME modal
        if (dom.runningViewClarify) {
            dom.runningViewClarify.classList.add('hidden');
        }
        if (dom.runningViewProgress) {
            dom.runningViewProgress.classList.remove('hidden');
        }

        // Start running state inside the already open modal
        startRunningState(refinedTopic, isMockKeyword ? 4000 : (isMockAmbiguous ? 2500 : 14000));

        // Delegate to appropriate research handler
        if (isMockAmbiguous) {
            await executeResearch(refinedTopic);
        } else if (isMockKeyword) {
            await handleMockPipeline(refinedTopic);
        } else {
            await executeResearch(refinedTopic);
        }
    }

    async function handleClarifyInlineSubmit() {
        const refinedTopic = dom.clarifyInlineTopicInput ? dom.clarifyInlineTopicInput.value.trim() : '';
        if (!refinedTopic) {
            if (dom.clarifyInlineTopicInput) dom.clarifyInlineTopicInput.focus();
            return;
        }
        if (dom.topicInput) {
            dom.topicInput.value = refinedTopic;
            if (dom.btnClearTopic) {
                dom.btnClearTopic.classList.remove('hidden');
            }
        }
        await executeResearch(refinedTopic);
    }

    function updateModalStepper(stepIndex) {
        const stepper = document.getElementById('modal-pipeline-stepper');
        if (!stepper) return;
        const steps = stepper.querySelectorAll('.stepper-step');
        steps.forEach((stepEl, idx) => {
            if (idx === stepIndex) {
                stepEl.classList.add('active');
                stepEl.classList.remove('completed');
            } else if (idx < stepIndex) {
                stepEl.classList.remove('active');
                stepEl.classList.add('completed');
            } else {
                stepEl.classList.remove('active');
                stepEl.classList.remove('completed');
            }
        });

        const tracks = stepper.querySelectorAll('.stepper-track-fill');
        tracks.forEach((trackEl, idx) => {
            if (idx < stepIndex) {
                trackEl.style.width = '100%';
            } else if (idx === stepIndex) {
                trackEl.style.width = '45%';
            } else {
                trackEl.style.width = '0%';
            }
        });
    }

    let fadeOutTimeout = null;

    function startRunningState(topic, statusIntervalMs = 14000) {
        if (fadeOutTimeout) {
            clearTimeout(fadeOutTimeout);
            fadeOutTimeout = null;
        }
        state.running = true;
        if (dom.runningModal) {
            dom.runningModal.classList.remove('modal-fade-out');
            dom.runningModal.classList.remove('hidden');
        }
        if (dom.runningViewClarify) {
            dom.runningViewClarify.classList.add('hidden');
        }
        if (dom.runningViewProgress) {
            dom.runningViewProgress.classList.remove('hidden');
        }
        dom.runningTopicDisplay.textContent = `"${topic}"`;
        dom.liveTimer.textContent = '00:00';
        dom.runningStatusMessage.textContent = SPINNER_MESSAGES[0];
        updateModalStepper(0);
        if (window.startModalNeuralCanvas) {
            window.startModalNeuralCanvas();
        }

        state.startTime = Date.now();
        clearInterval(state.timerInterval);
        state.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
            const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
            const s = String(elapsed % 60).padStart(2, '0');
            dom.liveTimer.textContent = `${m}:${s}`;
        }, 1000);

        let step = 0;
        clearInterval(state.statusInterval);
        state.statusInterval = setInterval(() => {
            step = (step + 1) % SPINNER_MESSAGES.length;
            dom.runningStatusMessage.textContent = SPINNER_MESSAGES[step];
            updateModalStepper(step);
        }, statusIntervalMs);
    }

    function stopRunningState(smoothFade = false) {
        state.running = false;
        clearInterval(state.timerInterval);
        clearInterval(state.statusInterval);
        if (fadeOutTimeout) {
            clearTimeout(fadeOutTimeout);
            fadeOutTimeout = null;
        }

        if (smoothFade && dom.runningModal) {
            dom.runningModal.classList.remove('hidden');
            dom.runningModal.classList.add('modal-fade-out');
            fadeOutTimeout = setTimeout(() => {
                if (dom.runningModal) {
                    dom.runningModal.classList.add('hidden');
                    dom.runningModal.classList.remove('modal-fade-out');
                }
                if (window.stopModalNeuralCanvas) {
                    window.stopModalNeuralCanvas();
                }
                updateModalStepper(0);
                const stepper = document.getElementById('modal-pipeline-stepper');
                if (stepper) {
                    const tracks = stepper.querySelectorAll('.stepper-track-fill');
                    tracks.forEach(trackEl => { trackEl.style.width = '0%'; });
                }
                fadeOutTimeout = null;
            }, 320);
        } else {
            if (dom.runningModal) {
                dom.runningModal.classList.add('hidden');
                dom.runningModal.classList.remove('modal-fade-out');
            }
            if (window.stopModalNeuralCanvas) {
                window.stopModalNeuralCanvas();
            }
            updateModalStepper(0);
            const stepper = document.getElementById('modal-pipeline-stepper');
            if (stepper) {
                const tracks = stepper.querySelectorAll('.stepper-track-fill');
                tracks.forEach(trackEl => { trackEl.style.width = '0%'; });
            }
        }
    }

    // -------------------------------------------------------------------------
    // Render Results View
    // -------------------------------------------------------------------------
    function renderResults(data) {
        dom.resultsTopicTitle.textContent = data.topic;

        // Check if clarifying question is returned
        if (data.clarifying_question) {
            dom.clarifyingContainer.classList.remove('hidden');
            dom.reportPayloadContainer.classList.add('hidden');
            dom.clarifyingQuestionText.textContent = data.clarifying_question;
            if (dom.clarifyInlineTopicInput) {
                dom.clarifyInlineTopicInput.value = data.topic || '';
            }
            return;
        }

        dom.clarifyingContainer.classList.add('hidden');
        dom.reportPayloadContainer.classList.remove('hidden');

        // Executive Metrics
        // 1. Quality score
        let scoreDisplay = 'Passed';
        if (data.critic_score != null) {
            scoreDisplay = data.critic_score <= 1.0 ? `${(data.critic_score * 10).toFixed(1)} / 10` : `${data.critic_score.toFixed(1)} / 10`;
        } else if (data.feedback) {
            const match = data.feedback.match(/Score:\s*(\d+(?:\.\d+)?)\/10/i);
            if (match) scoreDisplay = `${match[1]} / 10`;
        }
        dom.metricScore.textContent = scoreDisplay;

        // 2. Fact-Check Status
        const verifText = data.verification || 'Verification complete.';
        const claimMatch = verifText.match(/(\d+\/\d+)\s+claims\s+fully\s+supported/i);
        dom.metricVerification.textContent = claimMatch ? `${claimMatch[1]} Verified` : 'Fact-Checked';

        // 3. Depth (Tracks)
        const subQuestions = data.sub_questions || [];
        dom.metricTracks.textContent = subQuestions.length > 0 ? `${subQuestions.length} Tracks` : 'Deep Search';

        // Duration Calculation
        const durationSec = data.execution_time_seconds || 20;
        const durationText = formatDuration(durationSec);

        // 4. Compute Tokens
        dom.metricTokens.textContent = data.tokens_used ? `${data.tokens_used.toLocaleString()} Tokens` : 'Standard';
        const iterCount = data.iteration_count || 1;
        if (dom.metricIterations) {
            dom.metricIterations.innerHTML = `
                <span class="metric-status-dot dot-violet"></span>
                <span>${iterCount} Reflection Iteration${iterCount > 1 ? 's' : ''}</span>
            `;
        }

        // Pipeline Runtime Meta Chip (Hero Strip beside reading time)
        if (dom.reportPipelineTimeText) {
            dom.reportPipelineTimeText.textContent = `${durationText} Pipeline Time`;
        }

        // Chrome Telemetry Status Pill (Clean Synthesis Complete)
        if (dom.resultsSynthesisStatusText) {
            dom.resultsSynthesisStatusText.textContent = 'Synthesis Complete';
        }

        // Sub-Questions Accordion
        if (dom.subquestionsContainer) {
            dom.subquestionsContainer.classList.remove('is-open');
        }
        if (dom.subquestionsToggleBtn) {
            dom.subquestionsToggleBtn.setAttribute('aria-expanded', 'false');
        }
        if (subQuestions.length > 0) {
            dom.subquestionsCount.textContent = subQuestions.length;
            dom.subquestionsList.innerHTML = subQuestions.map((q, idx) => `
                <div class="track-item">
                    <div class="track-left-group">
                        <span class="track-num">TRACK 0${idx + 1}</span>
                        <span class="track-query">${escapeHtml(q)}</span>
                    </div>
                    <span class="track-source-pill">Tavily · arXiv</span>
                </div>
            `).join('');
            dom.subquestionsContainer.classList.remove('hidden');
        } else {
            dom.subquestionsContainer.classList.add('hidden');
        }

        // Reading Time & Word Count Calculation
        const wordCount = data.report ? data.report.trim().split(/\s+/).length : 0;
        const readingTimeMinutes = Math.max(1, Math.round(wordCount / 220));
        const readingTimeEl = document.getElementById('report-reading-time');
        const readMetaText = `~${wordCount.toLocaleString()} Words · ${readingTimeMinutes} Min Read`;
        if (readingTimeEl) {
            readingTimeEl.innerHTML = `
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>${readMetaText}</span>
            `;
        }
        if (dom.launcherWordCount) {
            dom.launcherWordCount.textContent = readMetaText;
        }
        if (dom.modalReportMeta) {
            dom.modalReportMeta.textContent = readMetaText;
        }
        if (dom.modalReportTitle) {
            dom.modalReportTitle.textContent = data.topic ? data.topic : 'Executive Research Synthesis';
        }

        // Markdown Report Parsing (via marked.js) into Modal Body
        if (data.report && dom.modalReportContent) {
            dom.modalReportContent.innerHTML = marked.parse(data.report);

            // Wrap tables in .table-responsive-wrapper for mobile swipeable scroll
            const tables = dom.modalReportContent.querySelectorAll('table');
            tables.forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive-wrapper')) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'table-responsive-wrapper';
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
            });
        } else if (dom.modalReportContent) {
            dom.modalReportContent.innerHTML = '<p>No report text available.</p>';
        }

        // Verification Panel
        dom.verificationContent.textContent = verifText;

        // Critic Review Panel
        dom.criticContent.textContent = data.feedback || 'No feedback recorded.';

        // Footer Request ID
        dom.reportRequestId.textContent = data.request_id || '—';
    }

    // -------------------------------------------------------------------------
    // Report Modal Open / Close Controls
    // -------------------------------------------------------------------------
    function openReportModal() {
        if (!dom.modalReportViewer) return;
        dom.modalReportViewer.classList.remove('hidden');
        const scrollEl = document.getElementById('report-modal-scroll');
        if (scrollEl) scrollEl.scrollTop = 0;
        document.body.style.overflow = 'hidden';
    }

    function closeReportModal() {
        if (!dom.modalReportViewer) return;
        dom.modalReportViewer.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // -------------------------------------------------------------------------
    // Topic Clarification Modal Open / Close Controls
    // -------------------------------------------------------------------------
    function openClarifyModal(topic, clarifyingQuestion) {
        // Ensure running modal is active and visible
        if (dom.runningModal) {
            dom.runningModal.classList.remove('modal-fade-out');
            dom.runningModal.classList.remove('hidden');
        }
        document.body.style.overflow = 'hidden';

        // Switch internal card views smoothly in-place
        if (dom.runningViewProgress) {
            dom.runningViewProgress.classList.add('hidden');
        }
        if (dom.runningViewClarify) {
            dom.runningViewClarify.classList.remove('hidden');
        }

        if (dom.modalClarifyingQuestionText) {
            dom.modalClarifyingQuestionText.textContent = clarifyingQuestion;
        }
        if (dom.modalClarifyTopicInput) {
            dom.modalClarifyTopicInput.value = topic || '';
            if (dom.btnClearClarifyModalTopic) {
                dom.btnClearClarifyModalTopic.classList.toggle('hidden', !topic);
            }
        }
        setTimeout(() => {
            if (dom.modalClarifyTopicInput) {
                dom.modalClarifyTopicInput.focus();
                dom.modalClarifyTopicInput.select();
            }
        }, 80);
    }

    function closeClarifyModal() {
        stopRunningState(false);
        if (dom.runningViewClarify) {
            dom.runningViewClarify.classList.add('hidden');
        }
        if (dom.runningViewProgress) {
            dom.runningViewProgress.classList.remove('hidden');
        }
        document.body.style.overflow = '';
        if (dom.topicInput) {
            dom.topicInput.focus();
        }
    }

    function toggleSubquestions() {
        if (!dom.subquestionsContainer) return;
        const isOpen = dom.subquestionsContainer.classList.toggle('is-open');
        if (dom.subquestionsToggleBtn) {
            dom.subquestionsToggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }
    }

    // -------------------------------------------------------------------------
    // Report Actions (Copy & Download)
    // -------------------------------------------------------------------------
    function handleCopyMarkdown(triggerBtn) {
        if (!state.currentResults || !state.currentResults.report) return;
        const targetBtn = triggerBtn || dom.btnCopyMarkdown;
        navigator.clipboard.writeText(state.currentResults.report).then(() => {
            showToast('Full report copied to clipboard!');
            if (targetBtn) {
                const originalHtml = targetBtn.innerHTML;
                const isSquare = targetBtn.classList.contains('btn-icon-square');
                targetBtn.classList.add('copied');
                if (isSquare) {
                    targetBtn.innerHTML = `
                        <svg class="action-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    `;
                } else {
                    targetBtn.innerHTML = `
                        <svg class="action-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        <span>✓ Copied!</span>
                    `;
                }
                setTimeout(() => {
                    targetBtn.classList.remove('copied');
                    targetBtn.innerHTML = originalHtml;
                }, 2200);
            }
        }).catch(() => {
            showToast('Failed to copy to clipboard.');
        });
    }

    function handleDownloadMarkdown() {
        if (!state.currentResults || !state.currentResults.report) return;
        const r = state.currentResults;
        const frontmatter = [
            '---',
            `title: "${r.topic}"`,
            `request_id: "${r.request_id || ''}"`,
            `critic_score: "${dom.metricScore.textContent}"`,
            `date: "${new Date().toISOString()}"`,
            'pipeline: "ResearchMind Multi-Agent LangGraph"',
            '---',
            '',
            r.report
        ].join('\n');

        const blob = new Blob([frontmatter], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research_report_${Date.now()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Download started');
    }

    // -------------------------------------------------------------------------
    // History Persistence
    // -------------------------------------------------------------------------
    function saveToHistory(topic, results) {
        if (!results) return;
        // Never store simulated mock/demo pipeline runs in recent enquiry history
        if (results.request_id && String(results.request_id).startsWith('req_sim_')) return;
        if (/^(default|demo|test)(\s*-\s*a)?$/i.test((topic || '').trim())) return;

        const item = {
            topic,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            results,
            request_id: results.request_id || ''
        };
        state.history.unshift(item);
        if (state.history.length > 8) state.history.pop();
        localStorage.setItem('rm_history', JSON.stringify(state.history));
        renderHistory();
    }

    function renderHistory() {
        if (!dom.sidebarHistory || !dom.historyList) return;

        // Keep container visible with breathing room as part of modern cockpit
        dom.sidebarHistory.classList.remove('hidden');

        const count = state.history ? state.history.length : 0;
        if (dom.historyCountBadge) {
            dom.historyCountBadge.textContent = count;
        }

        if (count === 0) {
            if (dom.btnClearHistory) {
                dom.btnClearHistory.disabled = true;
                dom.btnClearHistory.classList.add('disabled');
            }
            dom.historyList.innerHTML = `
                <div class="history-empty-state">
                    <div class="empty-state-icon">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="12" y1="18" x2="12" y2="12"></line>
                            <line x1="9" y1="15" x2="15" y2="15"></line>
                        </svg>
                    </div>
                    <div class="empty-state-title">No Recent Enquiries</div>
                    <div class="empty-state-subtitle">Dispatched research dossiers appear here</div>
                </div>
            `;
            return;
        }

        if (dom.btnClearHistory) {
            dom.btnClearHistory.disabled = false;
            dom.btnClearHistory.classList.remove('disabled');
        }
        dom.historyList.innerHTML = '';

        state.history.forEach((h, index) => {
            const row = document.createElement('div');
            row.className = 'history-item-row';

            // Clickable dossier item button
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'history-item-btn';
            btn.title = `Load research: ${h.topic}`;
            btn.innerHTML = `
                <div class="history-item-icon">
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <line x1="10" y1="9" x2="8" y2="9"></line>
                    </svg>
                </div>
                <div class="history-item-details">
                    <span class="history-item-topic">${escapeHtml(h.topic)}</span>
                    ${h.timestamp ? `<span class="history-item-time">${escapeHtml(h.timestamp)}</span>` : ''}
                </div>
            `;
            btn.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    toggleSidebar(true);
                }
                state.currentResults = h.results;
                renderResults(h.results);
                showResultsStage();
            });

            // Individual delete action button
            const delBtn = document.createElement('button');
            delBtn.type = 'button';
            delBtn.className = 'history-item-delete-btn';
            delBtn.title = 'Remove enquiry';
            delBtn.setAttribute('aria-label', `Remove ${h.topic}`);
            delBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            `;
            delBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const reqId = h.request_id || (h.results && h.results.request_id);
                state.history.splice(index, 1);
                localStorage.setItem('rm_history', JSON.stringify(state.history));
                renderHistory();

                if (reqId && state.token && state.token !== 'demo-token') {
                    try {
                        await fetch(`/research/history/${encodeURIComponent(reqId)}`, {
                            method: 'DELETE',
                            headers: {
                                'Authorization': `Bearer ${state.token}`
                            }
                        });
                    } catch (err) {
                        console.error('Failed to delete item from server:', err);
                    }
                }
            });

            row.appendChild(btn);
            row.appendChild(delBtn);
            dom.historyList.appendChild(row);
        });
    }

    // Utility: Format seconds into clean readable duration (e.g. "20s", "1m 15s")
    function formatDuration(totalSeconds) {
        const sec = Math.max(1, Math.round(Number(totalSeconds) || 20));
        if (sec < 60) {
            return `${sec}s`;
        }
        const mins = Math.floor(sec / 60);
        const remSec = sec % 60;
        return remSec > 0 ? `${mins}m ${remSec}s` : `${mins}m`;
    }

    // Utility: HTML escape
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Initialize application on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

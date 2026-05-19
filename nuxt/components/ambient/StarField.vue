<template>
  <canvas ref="canvasRef" class="starfield" />
</template>

<script setup lang="ts">
import * as THREE from 'three'

const canvasRef = ref<HTMLCanvasElement | null>(null)

onMounted(() => {
  const canvas = canvasRef.value!
  let w = window.innerWidth
  let h = window.innerHeight

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false })
  renderer.setSize(w, h, false)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setClearColor(0x000000, 0)

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(70, w / h, 0.1, 300)
  camera.position.z = 60

  // ── Star textures ─────────────────────────────────────────────────────────
  // Dim stars: pure soft radial glow
  const dimTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 32
    const ctx = c.getContext('2d')!
    const g = ctx.createRadialGradient(16, 16, 0, 16, 16, 16)
    g.addColorStop(0,    'rgba(255,255,255,1)')
    g.addColorStop(0.2,  'rgba(255,255,255,0.85)')
    g.addColorStop(0.55, 'rgba(255,255,255,0.08)')
    g.addColorStop(1,    'rgba(255,255,255,0)')
    ctx.fillStyle = g; ctx.fillRect(0, 0, 32, 32)
    return new THREE.CanvasTexture(c)
  })()

  // Bright stars: soft glow + 4-point diffraction cross
  const brightTex = (() => {
    const S = 128, C = 64
    const c = document.createElement('canvas'); c.width = c.height = S
    const ctx = c.getContext('2d')!

    // Radial glow
    const g = ctx.createRadialGradient(C, C, 0, C, C, C)
    g.addColorStop(0,    'rgba(255,255,255,1)')
    g.addColorStop(0.08, 'rgba(255,255,255,0.95)')
    g.addColorStop(0.3,  'rgba(255,255,255,0.25)')
    g.addColorStop(0.7,  'rgba(255,255,255,0.04)')
    g.addColorStop(1,    'rgba(255,255,255,0)')
    ctx.fillStyle = g; ctx.fillRect(0, 0, S, S)

    // 4-point diffraction spikes
    ctx.globalCompositeOperation = 'screen'
    const drawSpike = (x1: number, y1: number, x2: number, y2: number) => {
      const sg = ctx.createLinearGradient(x1, y1, x2, y2)
      sg.addColorStop(0,    'rgba(255,255,255,0)')
      sg.addColorStop(0.45, 'rgba(255,255,255,0.65)')
      sg.addColorStop(0.5,  'rgba(255,255,255,0.9)')
      sg.addColorStop(0.55, 'rgba(255,255,255,0.65)')
      sg.addColorStop(1,    'rgba(255,255,255,0)')
      ctx.strokeStyle = sg; ctx.lineWidth = 1.5
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke()
    }
    drawSpike(0, C, S, C)       // horizontal
    drawSpike(C, 0, C, S)       // vertical
    drawSpike(C - 40, C - 40, C + 40, C + 40) // diagonal ↘
    drawSpike(C + 40, C - 40, C - 40, C + 40) // diagonal ↙

    return new THREE.CanvasTexture(c)
  })()

  // ── Realistic stellar color distribution ─────────────────────────────────
  function starColor(): THREE.Color {
    const r = Math.random()
    if (r < 0.04) return new THREE.Color().setHSL(0.62, 0.75, 0.94) // O/B blue-white
    if (r < 0.14) return new THREE.Color().setHSL(0.60, 0.35, 0.91) // A white-blue
    if (r < 0.42) return new THREE.Color().setHSL(0.13, 0.20, 0.89) // F/G yellow-white
    if (r < 0.70) return new THREE.Color().setHSL(0.08, 0.45, 0.82) // K yellow-orange
    return new THREE.Color().setHSL(0.04, 0.62, 0.74)               // M orange-red
  }

  // Power-law size: most stars tiny, few large (realistic luminosity function)
  function starSize(bias = 1): number {
    const u = Math.random()
    return (0.12 + Math.pow(u, 2.8) * 1.8) * bias
  }

  // ── Ambient background stars (sphere, 8 twinkling groups) ────────────────
  const GROUPS = 8
  const PER_GROUP = 380
  const starGroups: Array<{ mat: THREE.PointsMaterial; phase: number }> = []

  for (let g = 0; g < GROUPS; g++) {
    const positions = new Float32Array(PER_GROUP * 3)
    for (let i = 0; i < PER_GROUP; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi   = Math.acos(2 * Math.random() - 1)
      const r     = 42 + Math.random() * 90
      positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = r * Math.cos(phi)
    }
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))

    const mat = new THREE.PointsMaterial({
      color: starColor(),
      size: starSize(),
      map: dimTex,
      alphaTest: 0.001,
      transparent: true,
      opacity: 0.45 + Math.random() * 0.4,
      sizeAttenuation: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
    scene.add(new THREE.Points(geo, mat))
    starGroups.push({ mat, phase: (g / GROUPS) * Math.PI * 2 })
  }

  // ── Prominent bright stars (scattered near-sphere, with spike texture) ────
  const BRIGHT_COUNT = 28
  const brightPositions = new Float32Array(BRIGHT_COUNT * 3)
  const brightSizesArr  = new Float32Array(BRIGHT_COUNT)
  for (let i = 0; i < BRIGHT_COUNT; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi   = Math.acos(2 * Math.random() - 1)
    const r     = 38 + Math.random() * 55
    brightPositions[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
    brightPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    brightPositions[i * 3 + 2] = r * Math.cos(phi)
    brightSizesArr[i] = 0.7 + Math.random() * 1.4
  }
  const brightGeo = new THREE.BufferGeometry()
  brightGeo.setAttribute('position', new THREE.BufferAttribute(brightPositions, 3))
  const brightMat = new THREE.PointsMaterial({
    color: new THREE.Color(0xdde8ff),
    size: 1.2,
    map: brightTex,
    alphaTest: 0.001,
    transparent: true,
    opacity: 0.85,
    sizeAttenuation: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  })
  const brightPts = new THREE.Points(brightGeo, brightMat)
  scene.add(brightPts)

  // ── Foreground reactive stars (shader, mouse proximity glow) ─────────────
  const FG_COUNT = 260
  const fgPos   = new Float32Array(FG_COUNT * 3)
  const fgSizes = new Float32Array(FG_COUNT)
  for (let i = 0; i < FG_COUNT; i++) {
    fgPos[i * 3]     = (Math.random() - 0.5) * 175
    fgPos[i * 3 + 1] = (Math.random() - 0.5) * 110
    fgPos[i * 3 + 2] = -20 - Math.random() * 28
    fgSizes[i] = (0.4 + Math.random() * 0.9) * Math.min(window.devicePixelRatio, 1.5)
  }
  const fgGeo = new THREE.BufferGeometry()
  fgGeo.setAttribute('position', new THREE.BufferAttribute(fgPos, 3))
  fgGeo.setAttribute('size',     new THREE.BufferAttribute(fgSizes, 1))

  const mouseNDC = new THREE.Vector2(0, 0)

  const fgMat = new THREE.ShaderMaterial({
    uniforms: {
      uMouse: { value: mouseNDC },
      uTime:  { value: 0.0 },
    },
    vertexShader: /* glsl */`
      attribute float size;
      uniform vec2  uMouse;
      uniform float uTime;
      varying float vProximity;
      varying float vPhase;
      void main() {
        vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
        vec4 clip  = projectionMatrix * mvPos;
        vec2 ndc   = clip.xy / clip.w;
        float dist = length(ndc - uMouse);
        vProximity = 1.0 - smoothstep(0.0, 0.38, dist);
        vPhase     = position.x * 0.09 + position.y * 0.06;
        float breath = 1.0 + sin(uTime * 0.8 + vPhase * 6.28) * 0.18;
        gl_PointSize = size * (1.0 + vProximity * 4.2) * breath;
        gl_Position  = clip;
      }
    `,
    fragmentShader: /* glsl */`
      varying float vProximity;
      varying float vPhase;
      uniform float uTime;
      void main() {
        vec2  uv   = gl_PointCoord - 0.5;
        float r    = length(uv);
        if (r > 0.5) discard;
        float soft  = 1.0 - smoothstep(0.0, 0.5, r);
        float pulse = 0.38 + sin(uTime * 1.1 + vPhase * 6.28) * 0.14;
        float alpha = soft * (pulse + vProximity * 0.62);
        vec3 color  = mix(vec3(1.0), vec3(0.78, 0.55, 1.0), vProximity * 0.65);
        gl_FragColor = vec4(color, alpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  })
  scene.add(new THREE.Points(fgGeo, fgMat))

  // ── Burst particles (click anywhere) ─────────────────────────────────────
  interface Burst { x: number; y: number; z: number; vx: number; vy: number; life: number; maxLife: number; size: number }
  const bursts: Burst[] = []
  const MAX_BURST = 400
  const burstPos   = new Float32Array(MAX_BURST * 3).fill(9999)
  const burstSizes = new Float32Array(MAX_BURST)
  const burstGeo   = new THREE.BufferGeometry()
  burstGeo.setAttribute('position', new THREE.BufferAttribute(burstPos, 3))
  burstGeo.setAttribute('size',     new THREE.BufferAttribute(burstSizes, 1))
  const burstMat = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: /* glsl */`
      attribute float size; varying float vSize;
      void main() { vSize = size; gl_PointSize = size; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
    `,
    fragmentShader: /* glsl */`
      varying float vSize;
      void main() {
        vec2 uv = gl_PointCoord - 0.5; float r = length(uv); if (r > 0.5) discard;
        gl_FragColor = vec4(1.0, 1.0, 1.0, (1.0 - r * 2.0) * clamp(vSize / 10.0, 0.0, 1.0));
      }
    `,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  })
  scene.add(new THREE.Points(burstGeo, burstMat))

  function screenTo3D(cx: number, cy: number) {
    const v = new THREE.Vector3((cx / w) * 2 - 1, -(cy / h) * 2 + 1, 0.5).unproject(camera)
    const dir  = v.sub(camera.position).normalize()
    const dist = (-20 - camera.position.z) / dir.z
    return camera.position.clone().add(dir.multiplyScalar(dist))
  }

  const onClick = (e: MouseEvent) => {
    const p = screenTo3D(e.clientX, e.clientY)
    const n = 20 + Math.floor(Math.random() * 12)
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + Math.random() * 0.4
      const s = 0.10 + Math.random() * 0.22
      const l = 1.0 + Math.random() * 1.0
      bursts.push({ x: p.x, y: p.y, z: p.z, vx: Math.cos(a)*s, vy: Math.sin(a)*s, life: l, maxLife: l, size: 4 + Math.random() * 6 })
    }
  }
  document.addEventListener('click', onClick)

  // ── Shooting stars ────────────────────────────────────────────────────────
  interface Shooter { x: number; y: number; z: number; vx: number; vy: number; life: number; maxLife: number; trail: [number, number, number][] }
  const shooters: Shooter[] = []
  const MAX_TRAIL = 28
  const shooterPos   = new Float32Array(MAX_TRAIL * 3).fill(9999)
  const shooterSizes = new Float32Array(MAX_TRAIL)
  const shooterGeo   = new THREE.BufferGeometry()
  shooterGeo.setAttribute('position', new THREE.BufferAttribute(shooterPos, 3))
  shooterGeo.setAttribute('size',     new THREE.BufferAttribute(shooterSizes, 1))
  const shooterMat = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: /* glsl */`
      attribute float size; varying float vSize;
      void main() { vSize = size; gl_PointSize = size; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
    `,
    fragmentShader: /* glsl */`
      varying float vSize;
      void main() {
        vec2 uv = gl_PointCoord - 0.5; float r = length(uv); if (r > 0.5) discard;
        gl_FragColor = vec4(0.92, 0.88, 1.0, (1.0 - r * 2.0) * clamp(vSize / 12.0, 0.0, 1.0));
      }
    `,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  })
  scene.add(new THREE.Points(shooterGeo, shooterMat))

  let nextShooter = 5 + Math.random() * 6, shooterTimer = 0
  function spawnShooter() {
    const side = Math.random() > 0.5 ? 1 : -1
    const x = side * (70 + Math.random() * 30), y = 28 + Math.random() * 32
    const spd = 1.5 + Math.random() * 1.2
    const l = 0.7 + Math.random() * 0.5
    shooters.push({ x, y, z: -14, vx: Math.cos(Math.PI + (Math.random()-0.5)*0.5)*spd*-side, vy: -Math.sin(Math.random()*0.4)*spd, life: l, maxLife: l, trail: [] })
  }

  // ── Input ─────────────────────────────────────────────────────────────────
  const mouse = { x: 0, y: 0 }; const camRot = { x: 0, y: 0 }
  const onMouseMove = (e: MouseEvent) => {
    mouse.x = (e.clientX / w - 0.5) * 2; mouse.y = (e.clientY / h - 0.5) * 2
    mouseNDC.set(mouse.x, -mouse.y)
  }
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  const onResize = () => { w = window.innerWidth; h = window.innerHeight; renderer.setSize(w, h, false); camera.aspect = w/h; camera.updateProjectionMatrix() }
  window.addEventListener('resize', onResize)

  // ── Render loop ───────────────────────────────────────────────────────────
  let rafId: number, t = 0

  const tick = () => {
    rafId = requestAnimationFrame(tick)
    t += 0.0006
    const sec = performance.now() * 0.001

    scene.rotation.y = t * 0.045
    scene.rotation.x = Math.sin(t * 0.2) * 0.014

    camRot.x += (mouse.y * 0.016 - camRot.x) * 0.045
    camRot.y += (mouse.x * 0.016 - camRot.y) * 0.045
    camera.rotation.x = camRot.x; camera.rotation.y = camRot.y

    for (const { mat, phase } of starGroups)
      mat.opacity = 0.35 + Math.sin(t * 1.3 + phase) * 0.30
    brightMat.opacity = 0.75 + Math.sin(t * 0.9) * 0.15

    fgMat.uniforms.uTime.value = sec

    // Bursts
    for (let i = bursts.length - 1; i >= 0; i--) {
      const b = bursts[i]
      b.x += b.vx; b.y += b.vy; b.vx *= 0.965; b.vy *= 0.965; b.life -= 0.016
      if (b.life <= 0) bursts.splice(i, 1)
    }
    const ab = Math.min(bursts.length, MAX_BURST)
    for (let i = 0; i < ab; i++) {
      const b = bursts[i]
      burstPos[i*3]=b.x; burstPos[i*3+1]=b.y; burstPos[i*3+2]=b.z
      burstSizes[i] = b.size * (b.life / b.maxLife)
    }
    for (let i = ab; i < MAX_BURST; i++) { burstPos[i*3]=9999; burstPos[i*3+1]=9999; burstPos[i*3+2]=9999; burstSizes[i]=0 }
    burstGeo.attributes.position.needsUpdate = true; burstGeo.attributes.size.needsUpdate = true

    // Shooters
    shooterTimer += 0.016
    if (shooterTimer >= nextShooter) { spawnShooter(); shooterTimer = 0; nextShooter = 4 + Math.random() * 9 }
    let ti = 0
    for (const s of shooters) {
      s.trail.unshift([s.x, s.y, s.z]); if (s.trail.length > MAX_TRAIL) s.trail.pop()
      s.x += s.vx; s.y += s.vy; s.life -= 0.016
      for (let j = 0; j < s.trail.length && ti < MAX_TRAIL; j++, ti++) {
        const [tx,ty,tz] = s.trail[j]
        const fade = (1 - j / s.trail.length) * (s.life / s.maxLife)
        shooterPos[ti*3]=tx; shooterPos[ti*3+1]=ty; shooterPos[ti*3+2]=tz; shooterSizes[ti]=fade*11
      }
    }
    for (let i = ti; i < MAX_TRAIL; i++) { shooterPos[i*3]=9999; shooterPos[i*3+1]=9999; shooterPos[i*3+2]=9999; shooterSizes[i]=0 }
    shooterGeo.attributes.position.needsUpdate = true; shooterGeo.attributes.size.needsUpdate = true
    for (let i = shooters.length-1; i>=0; i--) if (shooters[i].life <= 0) shooters.splice(i, 1)

    renderer.render(scene, camera)
  }
  tick()

  onUnmounted(() => {
    cancelAnimationFrame(rafId)
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('resize', onResize)
    document.removeEventListener('click', onClick)
    ;[fgGeo, burstGeo, shooterGeo, brightGeo].forEach(g => g.dispose())
    ;[fgMat, burstMat, shooterMat, brightMat].forEach(m => m.dispose())
    dimTex.dispose(); brightTex.dispose()
    renderer.dispose()
  })
})
</script>

<style scoped>
.starfield {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>

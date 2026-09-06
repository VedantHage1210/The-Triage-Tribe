import { useEffect, useRef } from "react";
import * as THREE from "three";

/**
 * Section 12.2 note: no stock "AI robot" imagery — this is a genuine
 * interactive 3D graphic instead: a stylized heart/pulse form built
 * entirely from code (extruded heart-curve geometry + a pulsing ring),
 * in the clinical teal palette, draggable to rotate.
 */
export default function Hero3D({ height = 280 }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const width = mount.clientWidth;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 9);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    // --- Build a heart shape via a parametric curve, then extrude it ---
    const heartShape = new THREE.Shape();
    const x = 0, y = 0;
    heartShape.moveTo(x + 0.25, y + 0.25);
    heartShape.bezierCurveTo(x + 0.25, y + 0.25, x + 0.2, y, x, y);
    heartShape.bezierCurveTo(x - 0.3, y, x - 0.3, y + 0.35, x - 0.3, y + 0.35);
    heartShape.bezierCurveTo(x - 0.3, y + 0.55, x - 0.1, y + 0.77, x + 0.25, y + 0.95);
    heartShape.bezierCurveTo(x + 0.6, y + 0.77, x + 0.8, y + 0.55, x + 0.8, y + 0.35);
    heartShape.bezierCurveTo(x + 0.8, y + 0.35, x + 0.8, y, x + 0.5, y);
    heartShape.bezierCurveTo(x + 0.35, y, x + 0.25, y + 0.25, x + 0.25, y + 0.25);

    const extrudeSettings = { depth: 0.35, bevelEnabled: true, bevelSegments: 4, bevelSize: 0.05, bevelThickness: 0.05 };
    const heartGeometry = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
    heartGeometry.center();
    heartGeometry.rotateZ(Math.PI); // point downward, upright orientation
    heartGeometry.scale(2.2, 2.2, 2.2);

    const heartMaterial = new THREE.MeshStandardMaterial({
      color: 0x0f766e, // clinical teal, Section 16.1
      roughness: 0.35,
      metalness: 0.15,
    });
    const heartMesh = new THREE.Mesh(heartGeometry, heartMaterial);
    scene.add(heartMesh);

    // --- A soft pulsing wireframe ring behind it, like an ECG halo ---
    const ringGeometry = new THREE.TorusGeometry(2.6, 0.02, 8, 100);
    const ringMaterial = new THREE.MeshBasicMaterial({ color: 0x1d4ed8, transparent: true, opacity: 0.35 });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = Math.PI / 2.3;
    scene.add(ring);

    // --- Lighting ---
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.1);
    keyLight.position.set(3, 4, 5);
    scene.add(keyLight);

    // --- Mouse-drag rotation (a genuine interactive touch, not just autoplay) ---
    let isDragging = false;
    let previousX = 0;
    let autoRotate = true;

    const onPointerDown = (e) => {
      isDragging = true;
      autoRotate = false;
      previousX = e.clientX ?? e.touches?.[0]?.clientX ?? 0;
    };
    const onPointerMove = (e) => {
      if (!isDragging) return;
      const clientX = e.clientX ?? e.touches?.[0]?.clientX ?? 0;
      const deltaX = clientX - previousX;
      heartMesh.rotation.y += deltaX * 0.01;
      previousX = clientX;
    };
    const onPointerUp = () => {
      isDragging = false;
    };

    renderer.domElement.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);

    // --- Animation loop: gentle autorotate + pulse scale + ring breathing ---
    let frameId;
    let t = 0;
    const animate = () => {
      t += 0.02;
      if (autoRotate) heartMesh.rotation.y += 0.006;

      const pulse = 1 + Math.sin(t * 2.2) * 0.04;
      heartMesh.scale.set(pulse, pulse, pulse);

      const ringPulse = 1 + Math.sin(t * 2.2 - 0.3) * 0.06;
      ring.scale.set(ringPulse, ringPulse, 1);
      ring.material.opacity = 0.25 + Math.sin(t * 2.2) * 0.1;

      renderer.render(scene, camera);
      frameId = requestAnimationFrame(animate);
    };
    animate();

    // --- Resize handling ---
    const handleResize = () => {
      const w = mount.clientWidth;
      camera.aspect = w / height;
      camera.updateProjectionMatrix();
      renderer.setSize(w, height);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.dispose();
      heartGeometry.dispose();
      heartMaterial.dispose();
      ringGeometry.dispose();
      ringMaterial.dispose();
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
  }, [height]);

  return <div ref={mountRef} style={{ width: "100%", height, cursor: "grab" }} />;
}

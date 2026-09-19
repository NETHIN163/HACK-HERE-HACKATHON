import React, { useEffect, useRef, useState } from 'react';
import '@tensorflow/tfjs';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import { Camera, Loader2, ScanLine, ShieldCheck, Square } from 'lucide-react';

const VEHICLE_LABELS = new Set(['car', 'truck', 'bus', 'motorcycle', 'bicycle']);
const DETECTION_LABELS = ['person', 'car', 'truck', 'bus', 'motorcycle', 'bicycle'];

export default function CameraDetection() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const modelRef = useRef(null);
  const animationRef = useRef(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [counts, setCounts] = useState({ vehicles: 0, pedestrians: 0, total: 0, labels: [], byClass: {} });
  const [modelStatus, setModelStatus] = useState('Model idle');
  const [peoplePerSecond, setPeoplePerSecond] = useState(0);
  const [crowdStatus, setCrowdStatus] = useState('No crowd signal');
  const peopleWindowRef = useRef({ startedAt: 0, peak: 0 });

  useEffect(() => () => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  const detectFrame = async () => {
    if (!videoRef.current || !canvasRef.current || !modelRef.current || videoRef.current.readyState < 2) {
      animationRef.current = requestAnimationFrame(detectFrame);
      return;
    }
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let predictions = [];
    try {
      predictions = await modelRef.current.detect(video, 20, 0.35);
    } catch (detectionError) {
      setError(`Detection paused: ${detectionError.message}`);
      animationRef.current = requestAnimationFrame(detectFrame);
      return;
    }
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    let vehicles = 0;
    let pedestrians = 0;
    const byClass = Object.fromEntries(DETECTION_LABELS.map((label) => [label, 0]));
    predictions.forEach((prediction) => {
      const [x, y, width, height] = prediction.bbox;
      const isPerson = prediction.class === 'person';
      if (isPerson) pedestrians += 1;
      if (VEHICLE_LABELS.has(prediction.class)) vehicles += 1;
      if (byClass[prediction.class] !== undefined) byClass[prediction.class] += 1;
      context.strokeStyle = isPerson ? '#a78bfa' : '#12b981';
      context.lineWidth = 3;
      context.strokeRect(x, y, width, height);
      context.fillStyle = isPerson ? '#a78bfa' : '#12b981';
      context.font = 'bold 15px sans-serif';
      context.fillText(`${prediction.class} ${Math.round(prediction.score * 100)}%`, x, Math.max(16, y - 6));
    });
    const labels = [...new Set(predictions.map((prediction) => prediction.class))];
    setCounts({ vehicles, pedestrians, total: predictions.length, labels, byClass });
    const now = performance.now();
    if (!peopleWindowRef.current.startedAt) peopleWindowRef.current.startedAt = now;
    peopleWindowRef.current.peak = Math.max(peopleWindowRef.current.peak, pedestrians);
    if (now - peopleWindowRef.current.startedAt >= 1000) {
      setPeoplePerSecond(peopleWindowRef.current.peak);
      peopleWindowRef.current = { startedAt: now, peak: pedestrians };
    }
    setCrowdStatus(pedestrians >= 8 ? 'Crowd detected' : pedestrians >= 3 ? 'People gathering' : pedestrians > 0 ? 'People detected' : 'No crowd signal');
    animationRef.current = requestAnimationFrame(detectFrame);
  };

  const startCamera = async () => {
    setError('');
    setLoading(true);
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera access requires localhost or HTTPS.');
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      setModelStatus('Loading COCO-SSD...');
      modelRef.current = modelRef.current || await cocoSsd.load({ base: 'mobilenet_v2' });
      setModelStatus('Model ready');
      setRunning(true);
      animationRef.current = requestAnimationFrame(detectFrame);
    } catch (cameraError) {
      setError(cameraError.message || 'Camera permission or model loading failed.');
      streamRef.current?.getTracks().forEach((track) => track.stop());
    } finally {
      setLoading(false);
    }
  };

  const stopCamera = () => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setRunning(false);
    setCounts({ vehicles: 0, pedestrians: 0, total: 0, labels: [], byClass: {} });
    setPeoplePerSecond(0);
    setCrowdStatus('No crowd signal');
    peopleWindowRef.current = { startedAt: 0, peak: 0 };
    setModelStatus('Model idle');
    const context = canvasRef.current?.getContext('2d');
    if (context && canvasRef.current) context.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
  };

  return (
    <section className="camera-page">
      <div className="page-heading-row">
        <div>
          <span className="eyebrow-label"><ScanLine size={13} /> LOCAL COMPUTER VISION</span>
          <h2>Camera detection</h2>
          <p>Use your system webcam for a privacy-first prototype count of vehicles and pedestrians.</p>
        </div>
        <div className="camera-privacy"><ShieldCheck size={16} /> Video stays in this browser</div>
      </div>
      <div className="camera-grid">
        <div className="camera-viewport">
          <video ref={videoRef} muted playsInline className="camera-video" />
          <canvas ref={canvasRef} className="camera-overlay" />
          {!running && <div className="camera-empty"><Camera size={32} /><strong>Camera is paused</strong><span>Start detection to request webcam access.</span></div>}
          <div className="camera-status"><span className={running ? 'status-live-dot' : 'status-idle-dot'} /> {running ? 'DETECTION LIVE' : 'READY'}</div>
        </div>
        <div className="camera-controls">
          <div className="camera-model-card"><Loader2 size={17} /><div><strong>COCO-SSD model</strong><span>{modelStatus} • browser inference / no API key</span></div></div>
          <div className="detection-metrics">
            <div><strong>{counts.vehicles}</strong><span>Vehicles</span></div>
            <div><strong>{counts.pedestrians}</strong><span>Pedestrians</span></div>
            <div><strong>{peoplePerSecond}</strong><span>People / second</span></div>
          </div>
          <div className={`crowd-status ${crowdStatus === 'Crowd detected' ? 'crowd-alert' : ''}`}><span />{crowdStatus}</div>
          <div className="class-count-grid">
            {DETECTION_LABELS.map((label) => <div key={label}><span>{label}</span><strong>{counts.byClass[label] || 0}</strong></div>)}
          </div>
          <div className="traffic-load-card"><span>Estimated traffic load</span><strong>{Math.min(100, counts.vehicles * 12 + counts.pedestrians * 4)}%</strong></div>
          <div className="detection-labels">Detected now: {counts.labels.length ? counts.labels.join(', ') : 'point the camera at a visible subject'}</div>
          {error && <div className="camera-error">{error}</div>}
          {!running ? (
            <button className="camera-action camera-action-primary" onClick={startCamera} disabled={loading}>
              {loading ? <Loader2 className="spin-icon" size={17} /> : <Camera size={17} />}
              {loading ? 'Loading model...' : 'Start camera detection'}
            </button>
          ) : (
            <button className="camera-action camera-action-stop" onClick={stopCamera}><Square size={17} /> Stop detection</button>
          )}
          <p className="camera-note">Best for a demo camera pointed at a road or room entrance. Counts are estimates, not certified traffic enforcement data.</p>
        </div>
      </div>
    </section>
  );
}

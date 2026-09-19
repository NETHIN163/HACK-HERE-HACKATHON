import React from 'react';

export default function WavyDivider() {
  return (
    <div style={{ position: 'relative', width: '100%', overflow: 'hidden', lineHeight: 0, margin: '40px 0' }}>
      <svg
        viewBox="0 0 1200 120"
        preserveAspectRatio="none"
        style={{ position: 'relative', display: 'block', width: 'calc(100% + 1.3px)', height: '80px' }}
      >
        <path
          d="M0,0 C150,90 350,-40 500,40 C650,120 900,10 1200,60 L1200,120 L0,120 Z"
          fill="rgba(139, 92, 246, 0.08)"
          className="wave-path-1"
        />
        <path
          d="M0,30 C200,110 450,10 700,70 C950,130 1100,20 1200,40 L1200,120 L0,120 Z"
          fill="rgba(6, 182, 212, 0.08)"
          className="wave-path-2"
        />
      </svg>
    </div>
  );
}

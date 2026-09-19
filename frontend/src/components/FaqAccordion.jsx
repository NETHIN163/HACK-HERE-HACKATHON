import React, { useState } from 'react';
import { Plus, Minus, HelpCircle } from 'lucide-react';

export default function FaqAccordion() {
  const [openIdx, setOpenIdx] = useState(0);

  const faqs = [
    {
      q: 'What is the Q-Flow Quantum-Assisted Traffic Platform?',
      a: 'Q-Flow is a next-generation urban traffic and emergency dispatch management platform. It models multi-intersection signal networks into QUBO (Quadratic Unconstrained Binary Optimization) matrices and runs QAOA variational quantum algorithms to optimize signal phase allocation and prioritize emergency green corridors in real time.',
    },
    {
      q: 'How does Q-Flow outperform classical fixed or rule-based traffic controllers?',
      a: 'Classical fixed-timer signals cannot adapt to sudden congestion surges, accidents, or emergency dispatch calls. Q-Flow dynamically re-evaluates signal phase durations sub-second, reducing ambulance travel times by 75% and cutting vehicle idle queue wait times by up to 97%.',
    },
    {
      q: 'What quantum hardware or simulators does Q-Flow use?',
      a: 'Q-Flow is built using Qiskit, Qiskit Aer, and PennyLane. It supports both execution on local high-performance statevector simulators and remote deployment to IBM Quantum noisy intermediate-scale quantum (NISQ) hardware QPUs.',
    },
    {
      q: 'How are emergency green corridors preempted safely?',
      a: 'When an emergency request is registered, Q-Flow locks the signals along the optimal calculated route to green 30 seconds prior to ambulance arrival while clearing side-street queues beforehand. Overlapping emergency conflicts are automatically resolved via a strict priority matrix.',
    },
    {
      q: 'Can Q-Flow integrate with existing municipal traffic camera & sensor infrastructure?',
      a: 'Yes. Q-Flow provides a standardized REST and WebSocket API layer that ingests live loop detector data, camera queue counters, and emergency vehicle GPS feeds seamlessly.',
    },
  ];

  return (
    <section id="faq" style={{ padding: '60px 32px 80px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div className="glass-pill" style={{ marginBottom: '16px' }}>
          <HelpCircle size={14} />
          <span>Got Questions?</span>
        </div>
        <h2 style={{ fontSize: '2.4rem', fontWeight: 800, color: '#1d1d1f' }}>
          Frequently Asked Questions
        </h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {faqs.map((item, idx) => {
          const isOpen = openIdx === idx;
          return (
            <div
              key={idx}
              className="glass-card-static"
              style={{
                borderRadius: '16px',
                padding: '20px 24px',
                border: isOpen ? '1px solid rgba(0, 113, 227, 0.3)' : '1px solid rgba(0, 0, 0, 0.08)',
                cursor: 'pointer',
                transition: 'all 0.25s ease',
              }}
              onClick={() => setOpenIdx(isOpen ? null : idx)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1d1d1f' }}>{item.q}</h3>
                <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(0, 0, 0, 0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {isOpen ? <Minus size={16} color="#0071e3" /> : <Plus size={16} color="#515154" />}
                </div>
              </div>

              {isOpen && (
                <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.06)', color: '#515154', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  {item.a}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

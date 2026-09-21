import React, { useState } from 'react';
import { Send, CheckCircle } from 'lucide-react';

export default function DemoForm({ isOpen, onClose }) {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    cityName: '',
    jobTitle: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      if (onClose) onClose();
    }, 2500);
  };

  return (
    <section id="demo" style={{ padding: '80px 32px 100px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
      <div className="glass-card-static" style={{ padding: '48px', borderRadius: '28px', border: '1px solid rgba(139, 92, 246, 0.3)', position: 'relative' }}>
        <div className="glass-pill-cyan" style={{ marginBottom: '16px' }}>
          <span>Schedule Live Technical Briefing</span>
        </div>

        <h2 style={{ fontSize: '2.6rem', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
          See TRAFFIQ In Action Today
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '1rem', marginBottom: '36px', maxWidth: '560px', margin: '0 auto 36px' }}>
          Maintain strong emergency corridor priority and sub-second signal coordination across all metropolitan traffic sectors.
        </p>

        {submitted ? (
          <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '16px', padding: '36px', textAlign: 'center' }}>
            <CheckCircle size={48} color="#10b981" style={{ margin: '0 auto 16px' }} />
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Demo Request Registered!
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem' }}>
              Our Quantum Mobility Engineering team will contact your department shortly with custom city simulation credentials.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', textAlign: 'left' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>First Name *</label>
              <input
                type="text"
                required
                className="glass-input"
                placeholder="Jane"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>Last Name *</label>
              <input
                type="text"
                required
                className="glass-input"
                placeholder="Doe"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>Work / Govt Email *</label>
              <input
                type="email"
                required
                className="glass-input"
                placeholder="jane.doe@city.gov"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>Phone Number</label>
              <input
                type="tel"
                className="glass-input"
                placeholder="+1 (555) 000-0000"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>Municipality / Organization *</label>
              <input
                type="text"
                required
                className="glass-input"
                placeholder="Metropolitan Transit Authority"
                value={formData.cityName}
                onChange={(e) => setFormData({ ...formData, cityName: e.target.value })}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>Job Title</label>
              <input
                type="text"
                className="glass-input"
                placeholder="Director of Traffic Operations"
                value={formData.jobTitle}
                onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
              />
            </div>

            <div style={{ gridColumn: 'span 2', marginTop: '12px' }}>
              <button className="btn-orchid-glow" type="submit" style={{ width: '100%', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Submit Demo Request</span>
                <Send size={16} />
              </button>
            </div>
          </form>
        )}
      </div>
    </section>
  );
}

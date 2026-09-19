import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import ImpactStats from './components/ImpactStats';
import HowItWorks from './components/HowItWorks';
import ComparisonToggle from './components/ComparisonToggle';
import SavingsCalculator from './components/SavingsCalculator';
import UseCasesGrid from './components/UseCasesGrid';
import FaqAccordion from './components/FaqAccordion';
import Footer from './components/Footer';
import OperationsCenter from './components/OperationsCenter';
import HorizontalTicker from './components/HorizontalTicker';
import WavyDivider from './components/WavyDivider';

export default function App() {
  const [activeView, setActiveView] = useState('landing'); // 'landing' or 'ops'

  return (
    <div style={{ position: 'relative', minHeight: '100vh', backgroundColor: '#0b0813', color: '#f8fafc', overflow: 'hidden' }}>
      {/* AR / VR Spatial Perspective Grid & Visor Scanlines */}
      <div className="ar-scanline" />
      <div className="bg-mesh-container ar-vr-perspective">
        <div className="ar-grid-3d" />
        <div className="orb-purple" />
        <div className="orb-cyan" />
        <div className="orb-rose" />
        <div className="bubble bubble-1" />
        <div className="bubble bubble-2" />
        <div className="bubble bubble-3" />
        <div className="bubble bubble-4" />
      </div>

      {/* Top Sticky Header */}
      <Navbar
        activeView={activeView}
        setActiveView={setActiveView}
      />

      {/* Infinite Horizontal Scrolling Ticker Marquee */}
      <HorizontalTicker />

      {/* Main View Router */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        {activeView === 'landing' ? (
          <>
            <HeroSection onExploreOps={() => setActiveView('ops')} />
            <WavyDivider />
            <ImpactStats />
            <WavyDivider />
            <HowItWorks />
            <ComparisonToggle />
            <WavyDivider />
            <SavingsCalculator onLaunchSimulator={() => setActiveView('ops')} />
            <UseCasesGrid onSelectUseCase={() => setActiveView('ops')} />
            <WavyDivider />
            <FaqAccordion />
          </>
        ) : (
          <OperationsCenter />
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

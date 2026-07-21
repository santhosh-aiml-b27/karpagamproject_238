import React from 'react';
import { TrafficCone, Zap, Clock, ShieldAlert, CheckCircle2, RotateCcw, AlertTriangle } from 'lucide-react';

export default function TrafficSignalStatus({ signals, onSignalOverride }) {
  return (
    <div className="card signal-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <TrafficCone size={20} />
          </div>
          <div>
            <h2 className="card-title">Live Traffic Signal Status & AI Controller</h2>
            <p className="card-subtitle">Real-time intersection light state, timers & override switches</p>
          </div>
        </div>
        <div className="header-meta-pill">
          <Zap size={14} className="text-emerald" />
          <span>5 Intersections Synchronized</span>
        </div>
      </div>

      {/* Signals Grid */}
      <div className="signals-grid">
        {signals.map((sig) => {
          const isGreen = sig.currentStatus === 'GREEN';
          const isYellow = sig.currentStatus === 'YELLOW';
          const isRed = sig.currentStatus === 'RED';

          return (
            <div key={sig.id} className="signal-card">
              <div className="sig-head">
                <div className="sig-info">
                  <h3 className="sig-name">{sig.name}</h3>
                  <span className="sig-loc">{sig.location} • {sig.id}</span>
                </div>
                <span className={`mode-chip ${sig.mode.includes('Manual') ? 'manual' : 'ai'}`}>
                  {sig.mode}
                </span>
              </div>

              {/* Traffic Light Visualizer */}
              <div className="light-visualizer">
                <div className={`light-circle red ${isRed ? 'active glow-red' : ''}`}></div>
                <div className={`light-circle yellow ${isYellow ? 'active glow-yellow' : ''}`}></div>
                <div className={`light-circle green ${isGreen ? 'active glow-green' : ''}`}></div>

                <div className="timer-box">
                  <div className="timer-count">{sig.timer}s</div>
                  <span className="timer-label">REMAINING</span>
                </div>
              </div>

              {/* Stats Row */}
              <div className="sig-stats-row">
                <div className="sig-stat">
                  <span className="stat-label">Congestion</span>
                  <span className={`stat-val ${sig.congestionLevel === 'High' ? 'red' : 'green'}`}>
                    {sig.congestionLevel}
                  </span>
                </div>
                <div className="sig-stat">
                  <span className="stat-label">Queue Count</span>
                  <span className="stat-val">{sig.vehicleQueue} vehicles</span>
                </div>
                <div className="sig-stat">
                  <span className="stat-label">AQI Zone</span>
                  <span className="stat-val">{sig.aqiImpact}</span>
                </div>
              </div>

              {/* Control Actions */}
              <div className="sig-actions">
                <button
                  className={`sig-btn green ${isGreen ? 'current' : ''}`}
                  onClick={() => onSignalOverride(sig.id, 'GREEN')}
                >
                  Force Green
                </button>
                <button
                  className={`sig-btn red ${isRed ? 'current' : ''}`}
                  onClick={() => onSignalOverride(sig.id, 'RED')}
                >
                  Force Red
                </button>
                <button
                  className="sig-btn outline"
                  onClick={() => onSignalOverride(sig.id, 'GREEN')}
                  title="Extend phase by 15 seconds"
                >
                  +15s Phase
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

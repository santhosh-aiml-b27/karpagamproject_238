import React from 'react';
import { Wind, AlertCircle, ShieldAlert, CheckCircle2, Info } from 'lucide-react';

export default function LiveAirQuality({ aqiData }) {
  const { aqi, status, statusColor, mainPollutant, pollutants, healthAdvisory } = aqiData;

  // Determine badge style
  const getBadgeClass = (stat) => {
    switch (stat?.toLowerCase()) {
      case 'good': return 'badge-good';
      case 'moderate': return 'badge-moderate';
      case 'poor': case 'unhealthy': return 'badge-poor';
      case 'hazardous': return 'badge-hazardous';
      default: return 'badge-moderate';
    }
  };

  return (
    <div className="card aqi-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <Wind size={20} />
          </div>
          <div>
            <h2 className="card-title">Live Air Quality Index (AQI)</h2>
            <p className="card-subtitle">Real-time IoT sensor network telemetry</p>
          </div>
        </div>
        <span className={`badge ${getBadgeClass(status)}`}>
          <span className="pulse-dot" style={{ background: statusColor }}></span>
          {status} Status
        </span>
      </div>

      <div className="aqi-body-grid">
        {/* Main AQI Gauge Card */}
        <div className="aqi-main-box" style={{ borderColor: `${statusColor}40` }}>
          <div className="aqi-gauge">
            <div className="aqi-number" style={{ color: statusColor }}>
              {aqi}
            </div>
            <div className="aqi-scale-label">AIR QUALITY INDEX</div>
          </div>

          <div className="aqi-meta">
            <div className="meta-pill">
              <span className="meta-label">Primary Pollutant:</span>
              <span className="meta-val">{mainPollutant}</span>
            </div>
            <div className="meta-pill">
              <span className="meta-label">Sensor Reliability:</span>
              <span className="meta-val green">99.8%</span>
            </div>
          </div>
        </div>

        {/* Breakdown of 6 Pollutants */}
        <div className="pollutants-grid">
          {pollutants.map((p) => (
            <div key={p.name} className="pollutant-card">
              <div className="pollutant-head">
                <span className="p-name">{p.name}</span>
                <span className="p-status" style={{ color: p.color }}>{p.status}</span>
              </div>
              <div className="p-value-row">
                <span className="p-val">{p.value}</span>
                <span className="p-unit">{p.unit}</span>
              </div>
              <div className="p-bar-bg">
                <div
                  className="p-bar-fill"
                  style={{ width: `${Math.min(p.percentage, 100)}%`, background: p.color }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Advisory Banner */}
      <div className="aqi-advisory-banner">
        <ShieldAlert size={20} className="advisory-icon" />
        <div className="advisory-content">
          <span className="advisory-title">Citizen Health Advisory</span>
          <p className="advisory-text">{healthAdvisory}</p>
        </div>
      </div>
    </div>
  );
}

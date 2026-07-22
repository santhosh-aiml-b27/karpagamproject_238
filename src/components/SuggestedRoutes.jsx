import React, { useState } from 'react';
import { Navigation, Clock, MapPin, Wind, Leaf, CheckCircle, Sparkles, ArrowRight } from 'lucide-react';

export default function SuggestedRoutes({ routes, onSelectRoute }) {
  const [selectedRouteId, setSelectedRouteId] = useState('route-ai');

  const handleApply = (route) => {
    setSelectedRouteId(route.id);
    onSelectRoute(route);
  };

  return (
    <div className="card routes-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <Navigation size={20} />
          </div>
          <div>
            <h2 className="card-title">AI Suggested Routes & Eco-Diversions</h2>
            <p className="card-subtitle">Real-time route optimization balancing travel time & air quality</p>
          </div>
        </div>

        <div className="header-badge-sparkle">
          <Sparkles size={15} className="text-cyan" />
          <span>Eco-Routing Engine v2.4</span>
        </div>
      </div>

      <div className="routes-grid">
        {routes.map((route) => {
          const isSelected = selectedRouteId === route.id;

          return (
            <div 
              key={route.id} 
              className={`route-card ${route.isRecommended ? 'recommended' : ''} ${isSelected ? 'active-selected' : ''}`}
            >
              {route.isRecommended && (
                <div className="recommended-ribbon">
                  <Sparkles size={13} /> AI RECOMMENDED ROUTE
                </div>
              )}

              <div className="route-head">
                <h3 className="route-name">{route.name}</h3>
                <span className="ai-score-pill">{route.aiScore}</span>
              </div>

              {/* Core Metrics Cards */}
              <div className="route-metrics">
                <div className="metric-box">
                  <Clock size={16} className="metric-icon text-cyan" />
                  <div>
                    <span className="metric-val">{route.estimatedTime}</span>
                    <span className="metric-sub">{route.savedTime}</span>
                  </div>
                </div>

                <div className="metric-box">
                  <MapPin size={16} className="metric-icon text-amber" />
                  <div>
                    <span className="metric-val">{route.distance}</span>
                    <span className="metric-sub" style={{ color: route.trafficColor }}>
                      {route.trafficLevel}
                    </span>
                  </div>
                </div>

                <div className="metric-box">
                  <Wind size={16} className="metric-icon text-emerald" />
                  <div>
                    <span className="metric-val" style={{ color: route.aqiColor }}>
                      {route.aqiLevel}
                    </span>
                    <span className="metric-sub">{route.emissionsSaved}</span>
                  </div>
                </div>
              </div>

              {/* Highlights List */}
              <div className="route-highlights">
                {route.highlights.map((h, i) => (
                  <div key={i} className="highlight-item">
                    <CheckCircle size={14} className="h-icon" />
                    <span>{h}</span>
                  </div>
                ))}
              </div>

              {/* Apply Action Button */}
              <button
                className={`btn ${route.isRecommended ? 'btn-primary' : 'btn-outline'} w-full mt-3`}
                onClick={() => handleApply(route)}
              >
                {isSelected ? (
                  <>
                    <CheckCircle size={16} /> Active on GIS Map
                  </>
                ) : (
                  <>
                    <span>Apply Diversion</span> <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

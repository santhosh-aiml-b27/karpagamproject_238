import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, LayerGroup } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Layers, TrafficCone, Wind, Navigation, AlertTriangle, ShieldCheck } from 'lucide-react';

// Custom Leaflet Icons using SVG Data URIs for crisp rendering
const createSignalIcon = (status) => {
  let color = '#10B981'; // Green
  if (status === 'RED') color = '#F43F5E';
  if (status === 'YELLOW') color = '#F59E0B';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="${color}" stroke="#0F172A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4" fill="#FFFFFF"/></svg>`;
  return L.icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  });
};

const createAqiSensorIcon = (aqi) => {
  let color = '#10B981';
  if (aqi > 100) color = '#F59E0B';
  if (aqi > 150) color = '#F43F5E';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="${color}" stroke="#0F172A" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="4"/><text x="12" y="16" font-size="9" font-weight="bold" fill="#000" text-anchor="middle">${aqi}</text></svg>`;
  return L.icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

export default function LiveTrafficMap({ 
  mapCenter, 
  markers, 
  polylines, 
  onSignalOverride 
}) {
  const [activeLayers, setActiveLayers] = useState({
    signals: true,
    aqiSensors: true,
    congestion: true,
    aiRoutes: true
  });

  const toggleLayer = (layerKey) => {
    setActiveLayers(prev => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  return (
    <div className="card map-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <MapPin size={20} />
          </div>
          <div>
            <h2 className="card-title">Live Traffic & AQI Interactive Map</h2>
            <p className="card-subtitle">Real-time GIS visualization & dynamic signal nodes</p>
          </div>
        </div>

        {/* Map Layer Controls */}
        <div className="map-layer-controls">
          <button 
            className={`layer-chip ${activeLayers.signals ? 'active' : ''}`}
            onClick={() => toggleLayer('signals')}
          >
            <TrafficCone size={14} /> Signals
          </button>
          <button 
            className={`layer-chip ${activeLayers.aqiSensors ? 'active' : ''}`}
            onClick={() => toggleLayer('aqiSensors')}
          >
            <Wind size={14} /> AQI Nodes
          </button>
          <button 
            className={`layer-chip ${activeLayers.congestion ? 'active' : ''}`}
            onClick={() => toggleLayer('congestion')}
          >
            <AlertTriangle size={14} /> Congestion
          </button>
          <button 
            className={`layer-chip ${activeLayers.aiRoutes ? 'active' : ''}`}
            onClick={() => toggleLayer('aiRoutes')}
          >
            <Navigation size={14} /> AI Routes
          </button>
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div className="map-container-wrapper">
        <MapContainer 
          center={mapCenter} 
          zoom={13} 
          scrollWheelZoom={true}
          style={{ height: '440px', width: '100%' }}
        >
          {/* CartoDB Dark Matter Map Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Congestion & AI Polylines */}
          {polylines.map((poly) => {
            if (poly.id === 'route-heavy' && !activeLayers.congestion) return null;
            if (poly.id === 'route-ai-recommended' && !activeLayers.aiRoutes) return null;

            return (
              <Polyline
                key={poly.id}
                positions={poly.positions}
                pathOptions={{
                  color: poly.color,
                  weight: poly.weight,
                  dashArray: poly.dashArray || null
                }}
              >
                <Popup>
                  <div className="map-popup-card">
                    <h4>{poly.name}</h4>
                    <p>Corridor Status: {poly.id === 'route-heavy' ? 'Heavy Congestion' : 'AI Green Bypass'}</p>
                  </div>
                </Popup>
              </Polyline>
            );
          })}

          {/* Signal & AQI Markers */}
          {markers.map((marker) => {
            if (marker.type === 'signal' && !activeLayers.signals) return null;
            if (marker.type === 'aqi-sensor' && !activeLayers.aqiSensors) return null;

            const icon = marker.type === 'signal' 
              ? createSignalIcon(marker.status) 
              : createAqiSensorIcon(marker.aqi);

            return (
              <Marker
                key={marker.id}
                position={[marker.lat, marker.lng]}
                icon={icon}
              >
                <Popup>
                  <div className="map-popup-card">
                    <div className="popup-title-row">
                      <h4>{marker.name}</h4>
                      <span className="popup-id">{marker.id}</span>
                    </div>

                    {marker.type === 'signal' ? (
                      <>
                        <div className="popup-stat-row">
                          <span>Status:</span>
                          <strong style={{ 
                            color: marker.status === 'GREEN' ? '#10B981' : marker.status === 'RED' ? '#F43F5E' : '#F59E0B' 
                          }}>
                            {marker.status} ({marker.timer}s)
                          </strong>
                        </div>
                        <div className="popup-stat-row">
                          <span>Vehicles Queued:</span>
                          <strong>{marker.vehiclesCount}</strong>
                        </div>
                        <div className="popup-stat-row">
                          <span>AQI Nearby:</span>
                          <strong>{marker.aqi}</strong>
                        </div>
                        <div className="popup-btn-row">
                          <button 
                            className="btn btn-primary btn-sm"
                            onClick={() => onSignalOverride(marker.id, 'GREEN')}
                          >
                            Force Green
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="popup-stat-row">
                          <span>AQI Score:</span>
                          <strong style={{ color: marker.aqi > 100 ? '#F59E0B' : '#10B981' }}>
                            {marker.aqi} ({marker.status})
                          </strong>
                        </div>
                        <p className="popup-desc">{marker.details}</p>
                      </>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}

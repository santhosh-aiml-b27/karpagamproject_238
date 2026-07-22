import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LiveAirQuality from './components/LiveAirQuality';
import LiveTrafficMap from './components/LiveTrafficMap';
import PollutionPrediction from './components/PollutionPrediction';
import TrafficSignalStatus from './components/TrafficSignalStatus';
import SuggestedRoutes from './components/SuggestedRoutes';
import ExplainableAI from './components/ExplainableAI';
import Analytics from './components/Analytics';
import NotificationModal from './components/NotificationModal';

import {
  INITIAL_AQI_DATA,
  MAP_CENTER,
  MAP_TRAFFIC_MARKERS,
  MAP_CONGESTION_POLYLINES,
  INITIAL_TRAFFIC_SIGNALS,
  POLLUTION_PREDICTION_DATA,
  SUGGESTED_ROUTES_DATA,
  EXPLAINABLE_AI_DATA,
  ANALYTICS_DATA,
  INITIAL_NOTIFICATIONS
} from './data/dummyData';
import { MockApiService } from './services/mockApi';

export default function App() {
  // Navigation & Drawer State
  const [activeTab, setActiveTab] = useState('overview');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Core Data States
  const [aqiData, setAqiData] = useState(INITIAL_AQI_DATA);
  const [mapMarkers, setMapMarkers] = useState(MAP_TRAFFIC_MARKERS);
  const [polylines, setPolylines] = useState(MAP_CONGESTION_POLYLINES);
  const [signals, setSignals] = useState(INITIAL_TRAFFIC_SIGNALS);
  const [routes, setRoutes] = useState(SUGGESTED_ROUTES_DATA);
  const [predictionData, setPredictionData] = useState(POLLUTION_PREDICTION_DATA);
  const [xaiData, setXaiData] = useState(EXPLAINABLE_AI_DATA);
  const [analyticsData, setAnalyticsData] = useState(ANALYTICS_DATA);
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  // Modals
  const [isNotifOpen, setIsNotifOpen] = useState(false);

  // Real-time interval for ticking signal countdowns & slight AQI jitter
  useEffect(() => {
    const timerInterval = setInterval(() => {
      setSignals((prevSignals) => MockApiService.tickSignalTimers(prevSignals));
    }, 1000);

    const aqiInterval = setInterval(() => {
      setAqiData((prev) => {
        const updated = MockApiService.getLatestAqi(prev.aqi);
        return {
          ...prev,
          ...updated
        };
      });
    }, 5000);

    return () => {
      clearInterval(timerInterval);
      clearInterval(aqiInterval);
    };
  }, []);

  // Handle Signal Manual Overrides
  const handleSignalOverride = (signalId, targetStatus) => {
    setSignals((prev) => MockApiService.overrideSignalStatus(prev, signalId, targetStatus));
    
    // Sync map marker
    setMapMarkers((prev) =>
      prev.map((m) => {
        if (m.id === signalId) {
          return { ...m, status: targetStatus, mode: 'Manual Override' };
        }
        return m;
      })
    );

    // Push new notification
    const newNotif = {
      id: Date.now(),
      title: 'Manual Signal Override',
      message: `Intersection ${signalId} set to ${targetStatus} by Municipal Command.`,
      type: 'warning',
      time: 'Just now',
      read: false
    };
    setNotifications((prev) => [newNotif, ...prev]);
  };

  // Handle Route Selection
  const handleSelectRoute = (selectedRoute) => {
    // Highlight selected route on map
    if (selectedRoute.id === 'route-ai') {
      setPolylines((prev) =>
        prev.map((p) =>
          p.id === 'route-ai-recommended' ? { ...p, weight: 8 } : { ...p, weight: 4 }
        )
      );
    }
  };

  // Manual Data Refresh Simulation
  const handleRefreshData = () => {
    setAqiData(MockApiService.getLatestAqi(135));
  };

  // Notifications Mark All Read
  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header
          notifications={notifications}
          onOpenNotifications={() => setIsNotifOpen(true)}
          onRefreshData={handleRefreshData}
        />

        <main className="content-body">
          {/* Overview Tab (Renders all key dashboard sections seamlessly) */}
          {activeTab === 'overview' && (
            <>
              {/* Row 1: Live Air Quality & Live Traffic Map */}
              <div className="dashboard-grid">
                <div className="col-5">
                  <LiveAirQuality aqiData={aqiData} />
                </div>
                <div className="col-7">
                  <LiveTrafficMap
                    mapCenter={MAP_CENTER}
                    markers={mapMarkers}
                    polylines={polylines}
                    onSignalOverride={handleSignalOverride}
                  />
                </div>
              </div>

              {/* Row 2: Traffic Signals & Suggested Routes */}
              <div className="dashboard-grid">
                <div className="col-7">
                  <TrafficSignalStatus
                    signals={signals}
                    onSignalOverride={handleSignalOverride}
                  />
                </div>
                <div className="col-5">
                  <SuggestedRoutes
                    routes={routes}
                    onSelectRoute={handleSelectRoute}
                  />
                </div>
              </div>

              {/* Row 3: Pollution Prediction & Explainable AI */}
              <div className="dashboard-grid">
                <div className="col-7">
                  <PollutionPrediction predictionData={predictionData} />
                </div>
                <div className="col-5">
                  <ExplainableAI xaiData={xaiData} />
                </div>
              </div>

              {/* Row 4: Visual Analytics Hub */}
              <div className="dashboard-grid">
                <div className="col-12">
                  <Analytics analyticsData={analyticsData} />
                </div>
              </div>
            </>
          )}

          {/* Individual Dedicated Tab Views */}
          {activeTab === 'air-quality' && <LiveAirQuality aqiData={aqiData} />}
          {activeTab === 'traffic-map' && (
            <LiveTrafficMap
              mapCenter={MAP_CENTER}
              markers={mapMarkers}
              polylines={polylines}
              onSignalOverride={handleSignalOverride}
            />
          )}
          {activeTab === 'pollution-pred' && (
            <PollutionPrediction predictionData={predictionData} />
          )}
          {activeTab === 'signal-status' && (
            <TrafficSignalStatus
              signals={signals}
              onSignalOverride={handleSignalOverride}
            />
          )}
          {activeTab === 'suggested-routes' && (
            <SuggestedRoutes routes={routes} onSelectRoute={handleSelectRoute} />
          )}
          {activeTab === 'explainable-ai' && <ExplainableAI xaiData={xaiData} />}
          {activeTab === 'analytics' && <Analytics analyticsData={analyticsData} />}
        </main>
      </div>

      {/* Notification Modal Popover */}
      {isNotifOpen && (
        <NotificationModal
          notifications={notifications}
          onClose={() => setIsNotifOpen(false)}
          onMarkAllRead={handleMarkAllRead}
        />
      )}
    </div>
  );
}

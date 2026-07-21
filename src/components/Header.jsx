import React, { useState, useEffect } from 'react';
import { Activity, Bell, Calendar, Clock, ShieldCheck, User, Search, RefreshCw, AlertTriangle } from 'lucide-react';

export default function Header({ notifications, onOpenNotifications, onRefreshData }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="header-container">
      {/* Brand Title & AI System Status */}
      <div className="header-brand">
        <div className="brand-logo">
          <Activity className="logo-icon" size={24} />
        </div>
        <div>
          <div className="title-row">
            <h1 className="brand-title">EcoTraffic AI</h1>
            <span className="system-pill">
              <span className="pulse-dot" style={{ background: '#10B981' }}></span>
              AI Core Active (99.4%)
            </span>
          </div>
          <p className="brand-sub">Smart Traffic & Air Quality Municipal Command Center</p>
        </div>
      </div>

      {/* Right Controls & Profile */}
      <div className="header-actions">
        {/* Live Clock */}
        <div className="time-display">
          <div className="time-item">
            <Calendar size={15} className="time-icon" />
            <span>{time.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</span>
          </div>
          <div className="time-divider">|</div>
          <div className="time-item highlight">
            <Clock size={15} className="time-icon" />
            <span>{time.toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Refresh Data Button */}
        <button className="icon-btn" onClick={onRefreshData} title="Refresh Live Sensors">
          <RefreshCw size={18} />
        </button>

        {/* Notifications Icon with Badge */}
        <button className="icon-btn notification-btn" onClick={onOpenNotifications} title="System Alerts">
          <Bell size={20} />
          {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
        </button>

        {/* User Profile */}
        <div className="user-profile">
          <div className="avatar">
            <User size={18} />
          </div>
          <div className="user-info">
            <span className="user-name">Officer M. Anand</span>
            <span className="user-role">Municipal Ops Command</span>
          </div>
        </div>
      </div>
    </header>
  );
}

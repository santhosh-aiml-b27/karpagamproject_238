import React from 'react';
import { 
  LayoutDashboard, 
  Wind, 
  MapPin, 
  TrendingUp, 
  TrafficCone, 
  Navigation, 
  BrainCircuit, 
  BarChart3,
  Sliders,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, isCollapsed, setIsCollapsed }) {
  const navItems = [
    { id: 'overview', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'air-quality', label: 'Live Air Quality', icon: Wind },
    { id: 'traffic-map', label: 'Live Traffic Map', icon: MapPin },
    { id: 'pollution-pred', label: 'Pollution Forecast', icon: TrendingUp },
    { id: 'signal-status', label: 'Traffic Signals', icon: TrafficCone },
    { id: 'suggested-routes', label: 'AI Routes', icon: Navigation },
    { id: 'explainable-ai', label: 'Explainable AI', icon: BrainCircuit },
    { id: 'analytics', label: 'Visual Analytics', icon: BarChart3 },
  ];

  return (
    <aside className={`sidebar-container ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-toggle" onClick={() => setIsCollapsed(!isCollapsed)}>
        {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </div>

      <div className="nav-group">
        <span className="nav-heading">{!isCollapsed && 'OPERATIONS COMMAND'}</span>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
              title={isCollapsed ? item.label : ''}
            >
              <Icon size={20} className="nav-icon" />
              {!isCollapsed && <span className="nav-label">{item.label}</span>}
              {isActive && <div className="active-indicator" />}
            </button>
          );
        })}
      </div>

      {!isCollapsed && (
        <div className="sidebar-footer">
          <div className="eco-score-card">
            <div className="eco-header">
              <span>Eco-Efficiency Index</span>
              <span className="eco-val">88/100</span>
            </div>
            <div className="eco-bar">
              <div className="eco-fill" style={{ width: '88%' }}></div>
            </div>
            <p className="eco-text">City emissions down 14.2% today</p>
          </div>
        </div>
      )}
    </aside>
  );
}

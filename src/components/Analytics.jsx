import React, { useState } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  PointElement, 
  LineElement, 
  ArcElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { BarChart3, Download, Calendar, Filter, PieChart, Activity } from 'lucide-react';
import { MockApiService } from '../services/mockApi';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Analytics({ analyticsData }) {
  const [timeRange, setTimeRange] = useState('7d');

  const { aqiTrends, trafficDensity, vehicleDistribution, zoneComparison } = analyticsData;

  const chartThemeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94A3B8', font: { family: 'Inter', size: 12 } }
      },
      tooltip: {
        backgroundColor: '#0F172A',
        borderColor: '#06B6D4',
        borderWidth: 1,
        titleColor: '#F8FAFC',
        bodyColor: '#94A3B8'
      }
    },
    scales: {
      x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748B' } },
      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748B' } }
    }
  };

  const handleExport = () => {
    MockApiService.exportAnalyticsReport('CSV');
  };

  return (
    <div className="card analytics-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <BarChart3 size={20} />
          </div>
          <div>
            <h2 className="card-title">Visual Analytics & Traffic Insights</h2>
            <p className="card-subtitle">Comprehensive data analytics on air quality trends, vehicle flow, and zone metrics</p>
          </div>
        </div>

        {/* Filter Controls & Export Button */}
        <div className="analytics-controls">
          <div className="time-filter-group">
            <button 
              className={`filter-btn ${timeRange === 'today' ? 'active' : ''}`}
              onClick={() => setTimeRange('today')}
            >
              Today
            </button>
            <button 
              className={`filter-btn ${timeRange === '7d' ? 'active' : ''}`}
              onClick={() => setTimeRange('7d')}
            >
              7 Days
            </button>
            <button 
              className={`filter-btn ${timeRange === '30d' ? 'active' : ''}`}
              onClick={() => setTimeRange('30d')}
            >
              30 Days
            </button>
          </div>

          <button className="btn btn-primary btn-sm" onClick={handleExport}>
            <Download size={15} /> Export Report
          </button>
        </div>
      </div>

      {/* 2x2 Visual Analytics Chart Grid */}
      <div className="analytics-grid">
        {/* Chart 1: AQI Trends */}
        <div className="analytics-chart-box">
          <h3 className="chart-box-title">
            <Activity size={16} className="text-cyan" /> Historical AQI Trends by District
          </h3>
          <div style={{ height: '240px', width: '100%' }}>
            <Line data={aqiTrends} options={chartThemeOptions} />
          </div>
        </div>

        {/* Chart 2: Hourly Traffic Density */}
        <div className="analytics-chart-box">
          <h3 className="chart-box-title">
            <BarChart3 size={16} className="text-emerald" /> Hourly Traffic Density (Vehicles/Hr)
          </h3>
          <div style={{ height: '240px', width: '100%' }}>
            <Bar data={trafficDensity} options={chartThemeOptions} />
          </div>
        </div>

        {/* Chart 3: Vehicle Type Doughnut Distribution */}
        <div className="analytics-chart-box">
          <h3 className="chart-box-title">
            <PieChart size={16} className="text-purple" /> Vehicle Classification & EV Share
          </h3>
          <div style={{ height: '240px', width: '100%' }}>
            <Doughnut 
              data={vehicleDistribution} 
              options={{
                ...chartThemeOptions,
                plugins: {
                  ...chartThemeOptions.plugins,
                  legend: { position: 'right', labels: { color: '#94A3B8' } }
                }
              }} 
            />
          </div>
        </div>

        {/* Chart 4: Zone Pollution Comparison */}
        <div className="analytics-chart-box">
          <h3 className="chart-box-title">
            <Filter size={16} className="text-amber" /> Zone Air Quality Comparison
          </h3>
          <div style={{ height: '240px', width: '100%' }}>
            <Bar data={zoneComparison} options={chartThemeOptions} />
          </div>
        </div>
      </div>
    </div>
  );
}

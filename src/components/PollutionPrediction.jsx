import React from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend, 
  Filler 
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { TrendingUp, TrendingDown, Clock, Lightbulb, AlertTriangle, ShieldCheck } from 'lucide-react';

// Register Chart.js elements
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function PollutionPrediction({ predictionData }) {
  const { 
    currentTrend, 
    trendPercentage, 
    peakWindow, 
    peakAqi, 
    aiRecommendation, 
    hourlyForecast, 
    chartData 
  } = predictionData;

  const isIncreasing = currentTrend === 'Increasing';

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#94A3B8',
          font: { family: 'Inter', size: 12 }
        }
      },
      tooltip: {
        backgroundColor: '#0F172A',
        titleColor: '#F8FAFC',
        bodyColor: '#94A3B8',
        borderColor: '#06B6D4',
        borderWidth: 1,
        padding: 10,
        displayColors: true
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#64748B' }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#64748B' },
        suggestedMin: 50,
        suggestedMax: 200
      }
    }
  };

  return (
    <div className="card pollution-pred-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <TrendingUp size={20} />
          </div>
          <div>
            <h2 className="card-title">Pollution Prediction & AI Forecast</h2>
            <p className="card-subtitle">24-hour predictive AQI modeling via neural networks</p>
          </div>
        </div>

        {/* Trend Pill */}
        <div className={`trend-badge ${isIncreasing ? 'trend-up' : 'trend-down'}`}>
          {isIncreasing ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          <span>{currentTrend} by {trendPercentage}%</span>
        </div>
      </div>

      {/* Main Grid */}
      <div className="pred-grid">
        {/* Line Chart */}
        <div className="chart-box">
          <div style={{ height: '280px', width: '100%' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        {/* Forecast Details & Cards */}
        <div className="pred-sidebar">
          {/* Peak Warning Box */}
          <div className="peak-alert-card">
            <div className="alert-head">
              <Clock size={16} className="text-amber" />
              <span>Predicted Peak Window</span>
            </div>
            <div className="peak-time">{peakWindow}</div>
            <div className="peak-val-row">
              <span>Expected Peak AQI:</span>
              <strong className="text-rose">{peakAqi} (Poor)</strong>
            </div>
          </div>

          {/* AI Recommendation Banner */}
          <div className="ai-rec-banner">
            <div className="rec-head">
              <Lightbulb size={18} className="rec-icon" />
              <span>AI Mitigation Strategy</span>
            </div>
            <p className="rec-desc">{aiRecommendation}</p>
          </div>
        </div>
      </div>

      {/* Hourly Cards Row */}
      <div className="hourly-cards-container">
        <h3 className="hourly-title">Hourly Telemetry Forecast</h3>
        <div className="hourly-scroll-grid">
          {hourlyForecast.map((h) => (
            <div key={h.time} className="hourly-card">
              <div className="h-time">{h.time}</div>
              <div className="h-aqi" style={{ color: h.aqi > 150 ? '#F43F5E' : h.aqi > 100 ? '#F59E0B' : '#10B981' }}>
                AQI {h.aqi}
              </div>
              <div className="h-vol">{h.trafficVolume}</div>
              <div className="h-conf">Conf: {h.confidence}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

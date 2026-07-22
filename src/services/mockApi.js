// Mock API Service for real-time interactions, signal controls, and dynamic data simulation

export class MockApiService {
  // Simulate fetching latest AQI reading with slight fluctuation
  static getLatestAqi(currentAqi) {
    const delta = (Math.random() * 4 - 2); // -2 to +2 jitter
    const newAqi = Math.max(20, Math.min(300, Math.round(currentAqi + delta)));
    
    let status = 'Good';
    let statusColor = '#10B981';
    
    if (newAqi > 200) {
      status = 'Hazardous';
      statusColor = '#F43F5E';
    } else if (newAqi > 100) {
      status = 'Poor';
      statusColor = '#F97316';
    } else if (newAqi > 50) {
      status = 'Moderate';
      statusColor = '#F59E0B';
    }

    return {
      aqi: newAqi,
      status,
      statusColor,
      lastUpdated: new Date().toLocaleTimeString()
    };
  }

  // Decrement countdown timers for active signals
  static tickSignalTimers(signals) {
    return signals.map((sig) => {
      let newTimer = sig.timer - 1;
      let newStatus = sig.currentStatus;

      if (newTimer <= 0) {
        if (sig.currentStatus === 'GREEN') {
          newStatus = 'YELLOW';
          newTimer = 5;
        } else if (sig.currentStatus === 'YELLOW') {
          newStatus = 'RED';
          newTimer = sig.cycleDuration || 30;
        } else {
          newStatus = 'GREEN';
          newTimer = sig.cycleDuration || 45;
        }
      }

      return {
        ...sig,
        timer: newTimer,
        currentStatus: newStatus
      };
    });
  }

  // Trigger manual override on a traffic signal
  static overrideSignalStatus(signals, signalId, targetStatus) {
    return signals.map((sig) => {
      if (sig.id === signalId) {
        return {
          ...sig,
          currentStatus: targetStatus,
          timer: targetStatus === 'GREEN' ? 60 : 30,
          mode: 'Manual Override (Officer)'
        };
      }
      return sig;
    });
  }

  // Simulating CSV report download for Analytics
  static exportAnalyticsReport(format = 'CSV') {
    const reportContent = `AI Traffic & AQI Report\nGenerated: ${new Date().toLocaleString()}\nAverage AQI: 142\nTotal Vehicle Flow: 14,850\nGreen Corridor Efficiency: 94.2%\nOptimal Route Usage: 78%`;
    const blob = new Blob([reportContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Traffic_AQI_Report_${Date.now()}.${format.toLowerCase()}`;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}

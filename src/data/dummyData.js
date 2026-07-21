// Central Dummy Dataset for AI-Based Smart Traffic & Air Quality Management System

export const INITIAL_AQI_DATA = {
  aqi: 142,
  status: 'Moderate', // Good (0-50), Moderate (51-100), Unhealthy/Poor (101-200), Hazardous (201+)
  statusColor: '#F59E0B',
  mainPollutant: 'PM2.5',
  lastUpdated: 'Just now',
  healthAdvisory: 'Sensitive groups should limit prolonged outdoor exertion near major arterial roads.',
  pollutants: [
    { name: 'PM2.5', value: 58.4, unit: 'µg/m³', status: 'Moderate', percentage: 65, color: '#F59E0B' },
    { name: 'PM10', value: 92.1, unit: 'µg/m³', status: 'Moderate', percentage: 55, color: '#F59E0B' },
    { name: 'NO2', value: 45.2, unit: 'ppb', status: 'Good', percentage: 38, color: '#10B981' },
    { name: 'CO2', value: 420, unit: 'ppm', status: 'Normal', percentage: 42, color: '#10B981' },
    { name: 'O3', value: 68.0, unit: 'ppb', status: 'Moderate', percentage: 50, color: '#F59E0B' },
    { name: 'SO2', value: 12.3, unit: 'ppb', status: 'Good', percentage: 20, color: '#10B981' },
  ],
};

// Leaflet Map Markers (Centered around Metropolitan City, e.g., Bangalore/San Francisco/London coordinates)
export const MAP_CENTER = [12.9716, 77.5946];

export const MAP_TRAFFIC_MARKERS = [
  {
    id: 'SIG-01',
    name: 'Central Junction & 5th Ave',
    lat: 12.9716,
    lng: 77.5946,
    status: 'RED',
    timer: 24,
    congestion: 'High',
    aqi: 158,
    type: 'signal',
    vehiclesCount: 142,
    mode: 'AI Dynamic Sync'
  },
  {
    id: 'SIG-02',
    name: 'Grand Metro Bypass (Exit 4)',
    lat: 12.9800,
    lng: 77.6000,
    status: 'GREEN',
    timer: 45,
    congestion: 'Low',
    aqi: 88,
    type: 'signal',
    vehiclesCount: 68,
    mode: 'AI Dynamic Sync'
  },
  {
    id: 'SIG-03',
    name: 'Tech Park Expressway Sector 7',
    lat: 12.9620,
    lng: 77.5850,
    status: 'YELLOW',
    timer: 5,
    congestion: 'Moderate',
    aqi: 124,
    type: 'signal',
    vehiclesCount: 110,
    mode: 'AI Dynamic Sync'
  },
  {
    id: 'SIG-04',
    name: 'Old Town Heritage Boulevard',
    lat: 12.9650,
    lng: 77.6100,
    status: 'GREEN',
    timer: 32,
    congestion: 'Low',
    aqi: 72,
    type: 'signal',
    vehiclesCount: 45,
    mode: 'Schedule Fixed'
  },
  {
    id: 'AQI-STN-1',
    name: 'Industrial Zone Air Monitor #3',
    lat: 12.9880,
    lng: 77.5750,
    aqi: 189,
    status: 'Poor',
    type: 'aqi-sensor',
    details: 'Heavy diesel transport emissions detected.'
  },
  {
    id: 'AQI-STN-2',
    name: 'Botanical Gardens Clean Zone',
    lat: 12.9520,
    lng: 77.5900,
    aqi: 42,
    status: 'Good',
    type: 'aqi-sensor',
    details: 'High oxygen density, low vehicular particulate.'
  }
];

export const MAP_CONGESTION_POLYLINES = [
  {
    id: 'route-heavy',
    name: '5th Ave Expressway',
    color: '#F43F5E', // Red for heavy congestion
    weight: 6,
    positions: [
      [12.9716, 77.5946],
      [12.9750, 77.5980],
      [12.9800, 77.6000]
    ]
  },
  {
    id: 'route-ai-recommended',
    name: 'Green Eco Bypass Route',
    color: '#10B981', // Emerald green for AI recommended route
    weight: 6,
    dashArray: '8, 8',
    positions: [
      [12.9716, 77.5946],
      [12.9650, 77.6100],
      [12.9800, 77.6000]
    ]
  }
];

export const INITIAL_TRAFFIC_SIGNALS = [
  {
    id: 'SIG-01',
    name: 'Central Junction & 5th Ave',
    location: 'Downtown North',
    currentStatus: 'RED',
    timer: 24,
    cycleDuration: 60,
    congestionLevel: 'High',
    mode: 'AI Dynamic Sync',
    vehicleQueue: 48,
    aqiImpact: 'High (158)'
  },
  {
    id: 'SIG-02',
    name: 'Grand Metro Bypass (Exit 4)',
    location: 'Outer Ring East',
    currentStatus: 'GREEN',
    timer: 45,
    cycleDuration: 90,
    congestionLevel: 'Low',
    mode: 'AI Dynamic Sync',
    vehicleQueue: 12,
    aqiImpact: 'Moderate (88)'
  },
  {
    id: 'SIG-03',
    name: 'Tech Park Expressway Sector 7',
    location: 'Innovation Hub',
    currentStatus: 'YELLOW',
    timer: 5,
    cycleDuration: 45,
    congestionLevel: 'Moderate',
    mode: 'AI Dynamic Sync',
    vehicleQueue: 28,
    aqiImpact: 'Moderate (124)'
  },
  {
    id: 'SIG-04',
    name: 'Old Town Heritage Boulevard',
    location: 'Civic Center',
    currentStatus: 'GREEN',
    timer: 32,
    cycleDuration: 60,
    congestionLevel: 'Low',
    mode: 'Fixed Schedule',
    vehicleQueue: 15,
    aqiImpact: 'Good (72)'
  },
  {
    id: 'SIG-05',
    name: 'Port Highway Corridor B',
    location: 'Logistics Freight Zone',
    currentStatus: 'RED',
    timer: 18,
    cycleDuration: 75,
    congestionLevel: 'High',
    mode: 'AI Dynamic Sync',
    vehicleQueue: 62,
    aqiImpact: 'Poor (175)'
  }
];

export const POLLUTION_PREDICTION_DATA = {
  currentTrend: 'Increasing',
  trendPercentage: 14,
  peakWindow: '17:00 - 19:30',
  peakAqi: 185,
  aiRecommendation: 'Extend Green Signal Phase on Ring Road by 18% during peak hours to prevent idling vehicle emissions near School Zone 3.',
  hourlyForecast: [
    { time: '08:00', aqi: 95, trafficVolume: '620 v/h', confidence: '98%' },
    { time: '10:00', aqi: 115, trafficVolume: '890 v/h', confidence: '96%' },
    { time: '12:00', aqi: 130, trafficVolume: '1050 v/h', confidence: '95%' },
    { time: '14:00', aqi: 142, trafficVolume: '1120 v/h', confidence: '94%' },
    { time: '16:00', aqi: 165, trafficVolume: '1480 v/h', confidence: '93%' },
    { time: '18:00', aqi: 185, trafficVolume: '1820 v/h', confidence: '91%' },
    { time: '20:00', aqi: 160, trafficVolume: '1350 v/h', confidence: '95%' },
    { time: '22:00', aqi: 125, trafficVolume: '810 v/h', confidence: '97%' }
  ],
  chartData: {
    labels: ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00', '00:00'],
    datasets: [
      {
        label: 'Actual AQI',
        data: [78, 95, 115, 130, 142, null, null, null, null, null],
        borderColor: '#06B6D4',
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'AI Predicted AQI (Next 12h)',
        data: [null, null, null, 130, 142, 165, 185, 160, 125, 90],
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderDash: [6, 6],
        tension: 0.4,
        fill: true
      }
    ]
  }
};

export const SUGGESTED_ROUTES_DATA = [
  {
    id: 'route-ai',
    name: 'AI Eco Bypass Corridor',
    isRecommended: true,
    estimatedTime: '16 mins',
    savedTime: '8 mins faster',
    distance: '7.8 km',
    trafficLevel: 'Low Congestion',
    trafficColor: '#10B981',
    aqiLevel: 'AQI 74 (Good)',
    aqiColor: '#10B981',
    emissionsSaved: '32% Less Emissions',
    aiScore: '96% Optimal',
    highlights: ['Bypasses Central Congestion', 'Synchronized Green Signals', 'Low Emission Zone']
  },
  {
    id: 'route-standard',
    name: 'Standard Arterial Highway 5',
    isRecommended: false,
    estimatedTime: '24 mins',
    savedTime: 'Base time',
    distance: '6.4 km',
    trafficLevel: 'Heavy Delay',
    trafficColor: '#F43F5E',
    aqiLevel: 'AQI 158 (Poor)',
    aqiColor: '#F43F5E',
    emissionsSaved: 'High Idling',
    aiScore: '62% Optimal',
    highlights: ['3 Construction Bottlenecks', 'Long Signal Queues', 'High Particulate Density']
  },
  {
    id: 'route-alt',
    name: 'Ring Road Freight Diversion',
    isRecommended: false,
    estimatedTime: '19 mins',
    savedTime: '5 mins faster',
    distance: '9.1 km',
    trafficLevel: 'Moderate',
    trafficColor: '#F59E0B',
    aqiLevel: 'AQI 102 (Moderate)',
    aqiColor: '#F59E0B',
    emissionsSaved: '15% Less Emissions',
    aiScore: '84% Optimal',
    highlights: ['Slightly Longer Distance', 'Smooth Flowing Traffic', 'Ideal for Heavy Vehicles']
  }
];

export const EXPLAINABLE_AI_DATA = {
  confidenceScore: 94,
  modelName: 'DeepTraffic-AQI Net v3.2',
  lastOptimizationTime: '2 mins ago',
  decisionFactors: [
    {
      title: 'Less Traffic Volume',
      impact: '-35% Idling Delay',
      weight: 85,
      description: 'Diverts 420 vehicles/hour away from overloaded 5th Ave intersection.',
      iconName: 'Car'
    },
    {
      title: 'Lower AQI & Particulate Mitigation',
      impact: '-22% AQI Emission Spike',
      weight: 78,
      description: 'Prevents heavy PM2.5 accumulation near St. Mary Hospital & School Zone.',
      iconName: 'Wind'
    },
    {
      title: 'Shorter Waiting Time',
      impact: '-4.2 min Waiting Reduction',
      weight: 90,
      description: 'Dynamic green phase expansion syncs 4 consecutive signals.',
      iconName: 'Clock'
    },
    {
      title: 'Emergency Priority Clearance',
      impact: '0 Delay for Ambulance #A-12',
      weight: 95,
      description: 'Pre-cleared green corridor active on East Arterial.',
      iconName: 'Zap'
    }
  ],
  decisionLogs: [
    { id: 1, time: '11:55:12', action: 'Extended Signal SIG-02 Green Light by +15s', reason: 'High queue buildup detected on Ring Road East.' },
    { id: 2, time: '11:50:40', action: 'Triggered Dynamic Route Diversion #R-2', reason: 'AQI near Hospital Zone exceeded threshold 140.' },
    { id: 3, time: '11:42:05', action: 'Emergency Vehicle Corridor Activated', reason: 'Ambulance GPS priority ping received.' }
  ]
};

export const ANALYTICS_DATA = {
  aqiTrends: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Commercial District AQI',
        data: [130, 145, 160, 142, 175, 120, 110],
        borderColor: '#F43F5E',
        backgroundColor: 'rgba(244, 63, 94, 0.1)',
        fill: true,
        tension: 0.3
      },
      {
        label: 'Residential Zone AQI',
        data: [75, 82, 90, 88, 95, 65, 58],
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.3
      }
    ]
  },
  trafficDensity: {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'Vehicles / Hour',
        data: [250, 180, 1450, 1200, 1850, 980],
        backgroundColor: 'rgba(6, 182, 212, 0.7)',
        borderColor: '#06B6D4',
        borderRadius: 6
      }
    ]
  },
  vehicleDistribution: {
    labels: ['Electric Vehicles (EV)', 'Passenger Cars', 'Public Buses', 'Commercial Trucks', 'Two-Wheelers'],
    datasets: [
      {
        data: [22, 42, 12, 8, 16],
        backgroundColor: ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#06B6D4'],
        borderWidth: 0
      }
    ]
  },
  zoneComparison: {
    labels: ['Industrial Belt', 'City Center', 'Tech Corridor', 'Suburban West', 'Green Haven Park'],
    datasets: [
      {
        label: 'Avg AQI Level',
        data: [185, 142, 108, 68, 38],
        backgroundColor: ['#F43F5E', '#F97316', '#F59E0B', '#10B981', '#06B6D4'],
        borderRadius: 6
      }
    ]
  }
};

export const INITIAL_NOTIFICATIONS = [
  {
    id: 1,
    title: 'Emergency Vehicle Priority',
    message: 'Ambulance #A-12 requested green corridor on 5th Ave.',
    type: 'critical',
    time: '2 mins ago',
    read: false
  },
  {
    id: 2,
    title: 'Air Quality Alert (AQI 158)',
    message: 'PM2.5 spike detected in Sector 4 Downtown.',
    type: 'warning',
    time: '8 mins ago',
    read: false
  },
  {
    id: 3,
    title: 'AI Signal Sync Active',
    message: 'Signal #SIG-01 timing adjusted to reduce queue delay.',
    type: 'info',
    time: '15 mins ago',
    read: true
  }
];

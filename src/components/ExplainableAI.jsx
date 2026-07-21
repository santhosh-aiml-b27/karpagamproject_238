import React from 'react';
import { BrainCircuit, Car, Wind, Clock, Zap, ShieldCheck, CheckCircle2, History, ChevronRight } from 'lucide-react';

const iconMap = {
  Car: Car,
  Wind: Wind,
  Clock: Clock,
  Zap: Zap
};

export default function ExplainableAI({ xaiData }) {
  const { confidenceScore, modelName, lastOptimizationTime, decisionFactors, decisionLogs } = xaiData;

  return (
    <div className="card xai-section-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">
            <BrainCircuit size={20} />
          </div>
          <div>
            <h2 className="card-title">Explainable AI (XAI) Rationale Engine</h2>
            <p className="card-subtitle">Transparent justification breakdown of automated signal & route decisions</p>
          </div>
        </div>

        {/* Confidence Pill */}
        <div className="confidence-pill">
          <ShieldCheck size={16} className="text-emerald" />
          <span>Model Confidence: <strong>{confidenceScore}%</strong></span>
        </div>
      </div>

      <div className="xai-main-grid">
        {/* Left Column: Decision Factors */}
        <div className="xai-factors-col">
          <div className="xai-intro-banner">
            <div className="intro-title">Why did the AI optimize current traffic flows?</div>
            <p className="intro-desc">
              The neural model evaluates multi-sensor telemetry every 10 seconds to balance road throughput and citizen air quality exposure.
            </p>
          </div>

          <div className="factors-list">
            {decisionFactors.map((factor) => {
              const IconComponent = iconMap[factor.iconName] || Car;

              return (
                <div key={factor.title} className="factor-card">
                  <div className="factor-head">
                    <div className="factor-title-group">
                      <div className="factor-icon-bg">
                        <IconComponent size={18} />
                      </div>
                      <div>
                        <h4 className="factor-title">{factor.title}</h4>
                        <span className="factor-impact">{factor.impact}</span>
                      </div>
                    </div>
                    <span className="weight-badge">{factor.weight}% Weight</span>
                  </div>

                  <p className="factor-desc">{factor.description}</p>

                  <div className="factor-bar-bg">
                    <div
                      className="factor-bar-fill"
                      style={{ width: `${factor.weight}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Decision Logs & Model Info */}
        <div className="xai-logs-col">
          <div className="model-info-box">
            <div className="model-row">
              <span className="model-lbl">Active Architecture:</span>
              <span className="model-val">{modelName}</span>
            </div>
            <div className="model-row">
              <span className="model-lbl">Last Sync Cycle:</span>
              <span className="model-val">{lastOptimizationTime}</span>
            </div>
            <div className="model-row">
              <span className="model-lbl">Safety Constraints:</span>
              <span className="model-val green">Strictly Enforced (100%)</span>
            </div>
          </div>

          {/* Real-time Decision Log Timeline */}
          <div className="decision-logs-card">
            <div className="logs-head">
              <History size={16} className="text-cyan" />
              <span>Real-Time Decision Log</span>
            </div>

            <div className="timeline-list">
              {decisionLogs.map((log) => (
                <div key={log.id} className="timeline-item">
                  <div className="timeline-dot"></div>
                  <div className="timeline-content">
                    <div className="timeline-time">{log.time}</div>
                    <div className="timeline-action">{log.action}</div>
                    <div className="timeline-reason">Reason: {log.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

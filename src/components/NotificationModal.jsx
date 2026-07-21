import React from 'react';
import { Bell, AlertTriangle, ShieldAlert, Info, CheckCircle, X } from 'lucide-react';

export default function NotificationModal({ notifications, onClose, onMarkAllRead }) {
  return (
    <div className="notification-popover-overlay" onClick={onClose}>
      <div className="notification-popover" onClick={(e) => e.stopPropagation()}>
        <div className="popover-head">
          <div className="popover-title-row">
            <Bell size={18} className="text-cyan" />
            <span>System Notifications & Alerts</span>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="popover-body">
          {notifications.length === 0 ? (
            <div className="empty-notif">No new alerts at this time.</div>
          ) : (
            notifications.map((n) => (
              <div key={n.id} className={`notif-item ${n.type} ${n.read ? 'read' : 'unread'}`}>
                <div className="notif-icon">
                  {n.type === 'critical' ? (
                    <ShieldAlert size={18} className="text-rose" />
                  ) : n.type === 'warning' ? (
                    <AlertTriangle size={18} className="text-amber" />
                  ) : (
                    <Info size={18} className="text-cyan" />
                  )}
                </div>

                <div className="notif-content">
                  <div className="notif-title">{n.title}</div>
                  <div className="notif-msg">{n.message}</div>
                  <div className="notif-time">{n.time}</div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="popover-footer">
          <button className="btn btn-outline btn-sm w-full" onClick={onMarkAllRead}>
            Mark All as Read
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * ConnectionStatus Component
 * Displays API and WebSocket connection statuses cleanly with visual badges.
 */

import React from 'react';
import { useAppState } from '../context/AppContext';
import { WS_STATUS } from '../services/websocket';

export default function ConnectionStatus() {
  const { wsStatus, apiConnected } = useAppState();

  const getWsBadge = () => {
    switch (wsStatus) {
      case WS_STATUS.CONNECTED:
        return (
          <span className="badge badge-connected">
            <span className="dot-indicator dot-connected"></span>
            WS Connected
          </span>
        );
      case WS_STATUS.CONNECTING:
        return (
          <span className="badge badge-connecting">
            <span className="dot-indicator dot-connecting"></span>
            WS Reconnecting...
          </span>
        );
      case WS_STATUS.DISCONNECTED:
      default:
        return (
          <span className="badge badge-disconnected">
            <span className="dot-indicator dot-disconnected"></span>
            WS Offline
          </span>
        );
    }
  };

  const getApiBadge = () => {
    if (apiConnected) {
      return (
        <span className="badge badge-connected">
          <span className="dot-indicator dot-connected"></span>
          API Online
        </span>
      );
    }
    return (
      <span className="badge badge-disconnected">
        <span className="dot-indicator dot-disconnected"></span>
        API Unavailable
      </span>
    );
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
      {getApiBadge()}
      {getWsBadge()}
    </div>
  );
}

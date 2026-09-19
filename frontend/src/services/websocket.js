/**
 * Reusable WebSocket Client for Real-time Backend Event Stream
 */

import { WS_URL } from '../utils/constants.js';

export const WS_STATUS = {
  DISCONNECTED: 'DISCONNECTED',
  CONNECTING: 'CONNECTING',
  CONNECTED: 'CONNECTED',
};

class WebSocketManager {
  constructor(url = WS_URL) {
    this.url = url;
    this.socket = null;
    this.status = WS_STATUS.DISCONNECTED;
    this.listeners = new Set();
    this.statusListeners = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectDelay = 10000;
    this.reconnectTimer = null;
    this.isExplicitClose = false;
  }

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isExplicitClose = false;
    this.setStatus(WS_STATUS.CONNECTING);

    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.setStatus(WS_STATUS.CONNECTED);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', event.data, err);
        }
      };

      this.socket.onerror = (err) => {
        console.error('[WebSocket] Error:', err);
      };

      this.socket.onclose = () => {
        this.setStatus(WS_STATUS.DISCONNECTED);
        if (!this.isExplicitClose) {
          this.scheduleReconnect();
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection failed:', err);
      this.setStatus(WS_STATUS.DISCONNECTED);
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.isExplicitClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.setStatus(WS_STATUS.DISCONNECTED);
  }

  scheduleReconnect() {
    if (this.reconnectTimer) return;

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts - 1), this.maxReconnectDelay);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  setStatus(newStatus) {
    this.status = newStatus;
    this.statusListeners.forEach((cb) => cb(newStatus));
  }

  subscribeStatus(callback) {
    this.statusListeners.add(callback);
    callback(this.status);
    return () => this.statusListeners.delete(callback);
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(eventData) {
    this.listeners.forEach((cb) => cb(eventData));
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }
}

export const wsManager = new WebSocketManager();
export default wsManager;

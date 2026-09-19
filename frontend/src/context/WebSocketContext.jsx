/**
 * WebSocket Context Provider connecting WebSocket Manager to App Context
 */

import React, { createContext, useContext, useEffect } from 'react';
import wsManager, { WS_STATUS } from '../services/websocket';
import { useAppDispatch } from './AppContext';

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Subscribe to status changes
    const unsubStatus = wsManager.subscribeStatus((status) => {
      dispatch({ type: 'SET_WS_STATUS', payload: status });
    });

    // Subscribe to incoming WS messages
    const unsubMessages = wsManager.subscribe((eventData) => {
      dispatch({ type: 'HANDLE_WS_EVENT', payload: eventData });
    });

    // Auto-connect
    wsManager.connect();

    return () => {
      unsubStatus();
      unsubMessages();
      wsManager.disconnect();
    };
  }, [dispatch]);

  const value = {
    wsManager,
    connect: () => wsManager.connect(),
    disconnect: () => wsManager.disconnect(),
    send: (data) => wsManager.send(data),
  };

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}

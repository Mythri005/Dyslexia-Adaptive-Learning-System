class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.messageHandlers = new Map();
    this.connectionHandlers = new Map();
    this.isConnected = false;
  }

  connect(url) {
    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(url);
        
        this.socket.onopen = (event) => {
          console.log('WebSocket connected successfully');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.notifyConnectionHandlers('connected', event);
          resolve(event);
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected');
          this.isConnected = false;
          this.notifyConnectionHandlers('disconnected', event);
          this.handleReconnection(url);
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.notifyConnectionHandlers('error', error);
          reject(error);
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

      } catch (error) {
        console.error('WebSocket connection failed:', error);
        reject(error);
      }
    });
  }

  handleReconnection(url) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(url).catch(error => {
          console.error('Reconnection failed:', error);
        });
      }, this.reconnectInterval * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      this.notifyConnectionHandlers('reconnection_failed');
    }
  }

  handleMessage(data) {
    const { type, payload } = data;
    
    // Notify specific handlers for this message type
    if (this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type);
      handlers.forEach(handler => {
        try {
          handler(payload);
        } catch (error) {
          console.error('Error in message handler:', error);
        }
      });
    }
    
    // Notify global handlers
    if (this.messageHandlers.has('*')) {
      const handlers = this.messageHandlers.get('*');
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in global message handler:', error);
        }
      });
    }
  }

  sendMessage(type, payload) {
    if (!this.isConnected || !this.socket) {
      console.warn('WebSocket not connected. Message not sent:', type);
      return false;
    }

    try {
      const message = JSON.stringify({ type, payload, timestamp: Date.now() });
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  // Message handling
  onMessage(type, handler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type).add(handler);
    
    // Return unsubscribe function
    return () => {
      this.offMessage(type, handler);
    };
  }

  offMessage(type, handler) {
    if (this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type);
      handlers.delete(handler);
      
      if (handlers.size === 0) {
        this.messageHandlers.delete(type);
      }
    }
  }

  // Connection event handling
  onConnectionEvent(eventType, handler) {
    if (!this.connectionHandlers.has(eventType)) {
      this.connectionHandlers.set(eventType, new Set());
    }
    this.connectionHandlers.get(eventType).add(handler);
    
    // Return unsubscribe function
    return () => {
      this.offConnectionEvent(eventType, handler);
    };
  }

  offConnectionEvent(eventType, handler) {
    if (this.connectionHandlers.has(eventType)) {
      const handlers = this.connectionHandlers.get(eventType);
      handlers.delete(handler);
      
      if (handlers.size === 0) {
        this.connectionHandlers.delete(eventType);
      }
    }
  }

  notifyConnectionHandlers(eventType, data) {
    if (this.connectionHandlers.has(eventType)) {
      const handlers = this.connectionHandlers.get(eventType);
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in connection handler:', error);
        }
      });
    }
  }

  // Specific message types for our application
  sendStressUpdate(stressData) {
    return this.sendMessage('stress_update', stressData);
  }

  sendAttentionUpdate(attentionData) {
    return this.sendMessage('attention_update', attentionData);
  }

  sendPulseUpdate(pulseData) {
    return this.sendMessage('pulse_update', pulseData);
  }

  sendVoiceUpdate(voiceData) {
    return this.sendMessage('voice_update', voiceData);
  }

  sendHelpRequest(helpData) {
    return this.sendMessage('help_request', helpData);
  }

  sendProgressUpdate(progressData) {
    return this.sendMessage('progress_update', progressData);
  }

  // Subscribe to specific data types
  onStressUpdate(handler) {
    return this.onMessage('stress_update', handler);
  }

  onAttentionUpdate(handler) {
    return this.onMessage('attention_update', handler);
  }

  onPulseUpdate(handler) {
    return this.onMessage('pulse_update', handler);
  }

  onVoiceUpdate(handler) {
    return this.onMessage('voice_update', handler);
  }

  onHelpResponse(handler) {
    return this.onMessage('help_response', handler);
  }

  onProgressUpdate(handler) {
    return this.onMessage('progress_update', handler);
  }

  // Connection management
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
    this.messageHandlers.clear();
    this.connectionHandlers.clear();
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts
    };
  }

  // Ping service to keep connection alive
  startHeartbeat(interval = 30000) {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.sendMessage('ping', { timestamp: Date.now() });
      }
    }, interval);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// Create a singleton instance
const webSocketService = new WebSocketService();

// Default connection URL (can be overridden)
const DEFAULT_WS_URL = 'wss://ai-powered-adaptive-learning-system-i87g.onrender.com/ws';

// Export both the class and singleton instance
export { WebSocketService };
export default webSocketService;

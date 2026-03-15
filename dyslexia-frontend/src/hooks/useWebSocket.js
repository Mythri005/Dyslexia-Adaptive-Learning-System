import { useState, useEffect, useRef } from 'react';

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    if (!url) return;

    const connect = () => {
      try {
        ws.current = new WebSocket(url);
        
        ws.current.onopen = () => {
          setIsConnected(true);
          setError(null);
          console.log('WebSocket connected');
        };

        ws.current.onclose = () => {
          setIsConnected(false);
          console.log('WebSocket disconnected');
          
          // Attempt to reconnect after 5 seconds
          setTimeout(() => {
            connect();
          }, 5000);
        };

        ws.current.onerror = (event) => {
          setError('WebSocket error');
          console.error('WebSocket error:', event);
        };

        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLastMessage(data);
            onMessage && onMessage(data);
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };
      } catch (err) {
        setError(err.message);
      }
    };

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url, onMessage]);

  const sendMessage = (message) => {
    if (ws.current && isConnected) {
      try {
        const messageString = typeof message === 'string' ? message : JSON.stringify(message);
        ws.current.send(messageString);
        return true;
      } catch (err) {
        setError('Failed to send message');
        return false;
      }
    }
    return false;
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close();
    }
  };

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    disconnect
  };
};

export default useWebSocket;
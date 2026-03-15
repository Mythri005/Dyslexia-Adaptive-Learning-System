import React, { useRef, useEffect, useState } from 'react';
import cameraService from '../../services/cameraService';
import './CameraFeed.css';

const CameraFeed = ({ onAnalysisUpdate, resetSerialTrigger }) => {
  const videoRef = useRef(null);
  const serialPortRef = useRef(null);
  const readerRef = useRef(null);
  const stopReadingRef = useRef(false);

  const [analysis, setAnalysis] = useState(null);
  const [serialConnected, setSerialConnected] = useState(false);

  useEffect(() => {
    startCamera();

    return () => {
      cameraService.stopCamera();
      disconnectSerialPort();
    };
  }, []);

  // ✅ Reset serial when parent triggers
  useEffect(() => {
    if (resetSerialTrigger > 0) {
      disconnectSerialPort();
    }
  }, [resetSerialTrigger]);

  const startCamera = async () => {
    try {
      await cameraService.startCamera(videoRef.current);
    } catch (err) {
      console.error('Camera error:', err);
    }
  };

  const connectSerialPort = async () => {
    stopReadingRef.current = false;

    try {
      // ✅ Prevent reopening if already connected
      if (serialPortRef.current) {
        console.warn("Serial port already connected — skipping open");
        return;
      }

      const port = await navigator.serial.requestPort();

      // ✅ Open only if not already open
      if (!port.readable) {
        await port.open({ baudRate: 9600 });
      }

      serialPortRef.current = port;
      setSerialConnected(true);

      const textDecoder = new TextDecoderStream();

      port.readable.pipeTo(textDecoder.writable).catch(() => {});

      const reader = textDecoder.readable.getReader();
      readerRef.current = reader;

      let buffer = '';

      while (!stopReadingRef.current) {
        let result;
        try {
          result = await reader.read();
        } catch {
          break;
        }

        const { value, done } = result;
        if (done) break;

        buffer += value;
        const parts = buffer.split(']');

        for (let i = 0; i < parts.length - 1; i++) {
          const part = parts[i] + ']';
          const match = part.match(/\d+/);
          const pulse = match ? parseInt(match[0], 10) : null;

          if (pulse !== null) {
            const newAnalysis = { pulse_rate: pulse };
            setAnalysis(newAnalysis);
            onAnalysisUpdate && onAnalysisUpdate(newAnalysis);
          }
        }

        buffer = parts[parts.length - 1];
      }

    } catch (err) {
      console.error('❌ Serial Port Error:', err);
      setSerialConnected(false);
    }
  };

  const disconnectSerialPort = async () => {
    stopReadingRef.current = true;

    if (readerRef.current) {
      try {
        await readerRef.current.cancel();
        readerRef.current.releaseLock();
      } catch {}
      readerRef.current = null;
    }

    if (serialPortRef.current) {
      try {
        await serialPortRef.current.close();
      } catch {}
      serialPortRef.current = null;
    }

    setSerialConnected(false);
  };

  return (
    <div className="camera-feed">
      <div className="camera-container">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="camera-video"
        />

        {analysis && (
          <div className="pulse-only-display">
            ❤️ Pulse: <strong>{analysis.pulse_rate || 0} BPM</strong>
          </div>
        )}

        <div style={{ marginTop: '10px' }}>
          <button
            onClick={connectSerialPort}
            disabled={serialConnected}
            style={{ padding: '8px 16px', fontSize: '16px', marginRight: '10px' }}
          >
            {serialConnected ? 'Serial Connected' : 'Connect Serial Port'}
          </button>

          {serialConnected && (
            <button
              onClick={disconnectSerialPort}
              style={{ padding: '8px 16px', fontSize: '16px' }}
            >
              Disconnect Serial Port
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;

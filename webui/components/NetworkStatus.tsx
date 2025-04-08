// NetworkStatus.tsx
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function NetworkStatus() {
  const [networkStatus, setNetworkStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchNetworkStatus = async () => {
      try {
        const responses = await Promise.all([
          axios.get('/api/workers/1/network_status'),
          axios.get('/api/workers/2/network_status'),
          axios.get('/api/workers/3/network_status')
        ]);
        
        setNetworkStatus(responses.map(res => res.data));
        setLoading(false);
      } catch (error) {
        console.error('Error fetching network status:', error);
      }
    };
    
    fetchNetworkStatus();
    const interval = setInterval(fetchNetworkStatus, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  if (loading) {
    return <div>Loading network status...</div>;
  }
  
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-3">Network Status</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {networkStatus.map((status) => (
          <div key={status.worker_id} className="border rounded-md p-3">
            <h3 className="font-medium">Worker {status.worker_id}</h3>
            
            <div className="mt-2 space-y-1 text-sm">
              <div className="flex justify-between">
                <span>Backend Latency:</span>
                <span className={status.backend_latency_ms > 100 ? 'text-red-500' : 'text-green-500'}>
                  {status.backend_latency_ms > 0 ? `${status.backend_latency_ms.toFixed(1)} ms` : 'N/A'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span>Packet Loss:</span>
                <span>
                  {status.network_stats.dropin + status.network_stats.dropout > 0 ? 
                    `${status.network_stats.dropin + status.network_stats.dropout} packets` : 
                    'None'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span>Network I/O:</span>
                <span>
                  {formatBytes(status.network_stats.bytes_recv)} in / 
                  {formatBytes(status.network_stats.bytes_sent)} out
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
import io from 'socket.io-client';

class WebSocketService {
  private socket: any = null;
  private url: string;

  constructor() {
    this.url = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
  }

  connect(token: string) {
    if (this.socket) {
      this.disconnect();
    }

    this.socket = io(this.url, {
      auth: {
        token,
      },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('connect_error', (error: any) => {
      console.error('WebSocket connection error:', error);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Subscribe to campaign updates
  subscribeToCampaignUpdates(campaignId: number, callback: (data: any) => void) {
    if (!this.socket) return;

    this.socket.emit('join_campaign', { campaign_id: campaignId });
    this.socket.on('campaign_update', callback);
  }

  unsubscribeFromCampaignUpdates(campaignId: number) {
    if (!this.socket) return;

    this.socket.emit('leave_campaign', { campaign_id: campaignId });
    this.socket.off('campaign_update');
  }

  // Subscribe to message updates
  subscribeToMessageUpdates(callback: (data: any) => void) {
    if (!this.socket) return;

    this.socket.on('message_update', callback);
  }

  unsubscribeFromMessageUpdates() {
    if (!this.socket) return;

    this.socket.off('message_update');
  }

  // Generic event listeners
  on(event: string, callback: (data: any) => void) {
    if (!this.socket) return;
    this.socket.on(event, callback);
  }

  off(event: string) {
    if (!this.socket) return;
    this.socket.off(event);
  }

  emit(event: string, data: any) {
    if (!this.socket) return;
    this.socket.emit(event, data);
  }
}

export const wsService = new WebSocketService();
export default wsService;

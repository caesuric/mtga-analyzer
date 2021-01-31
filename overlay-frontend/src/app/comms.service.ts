import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CommsService {
  socket: WebSocket;

  constructor() {
    this.socket = new WebSocket('ws://127.0.0.1:19019/socket')
    this.socket.onmessage = this.onMessage;
    this.socket.onopen = this.onOpen;
    this.socket.onclose = this.onClose;
  }

  onMessage(event: any) {
    console.log(event.data);
  }

  onOpen(event: any) {
    console.log('socket opened');
  }

  onClose(event: any) {
    setTimeout(() => {
      this.socket = new WebSocket('ws://localhost:19019/socket')
      this.socket.onmessage = this.onMessage;
      this.socket.onopen = this.onOpen;
      this.socket.onclose = this.onClose;
    }, 200);
  }
}

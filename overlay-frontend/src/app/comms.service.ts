import { EventEmitter, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CommsService {
  socket: WebSocket;
  data: any = null;
  dataUpdated: EventEmitter<any> = new EventEmitter<any>();

  constructor() {
    this.socket = new WebSocket('ws://127.0.0.1:19019/socket')
    this.socket.onmessage = (event: any) => this.onMessage(event);
    this.socket.onopen = (event: any) => this.onOpen(event);
    this.socket.onclose = (event: any) => this.onClose(event);
  }

  onMessage(event: any) {
    this.data = JSON.parse(event.data)['data'];
    this.dataUpdated.emit(this.data);
    console.log(this.data);
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

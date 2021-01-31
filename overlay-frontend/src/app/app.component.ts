import { Component } from '@angular/core';
import { CommsService } from './comms.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'overlay-frontend';

  constructor(private comms: CommsService) {}
}

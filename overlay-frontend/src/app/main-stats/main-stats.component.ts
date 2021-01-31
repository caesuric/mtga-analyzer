import { Component, OnInit } from '@angular/core';
import { CommsService } from '../comms.service';

@Component({
  selector: 'app-main-stats',
  templateUrl: './main-stats.component.html',
  styleUrls: ['./main-stats.component.scss']
})
export class MainStatsComponent implements OnInit {
  data: any = null;

  constructor(public comms: CommsService) { }

  ngOnInit(): void {
    this.comms.dataUpdated.subscribe((data: any) => {
      this.data = data;
      console.log('hit');
    });
  }

  formatNumber(inputNumber: number): string {
    return inputNumber.toFixed(2);
  }

}

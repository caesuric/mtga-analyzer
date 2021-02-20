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

  formatTime(inputMinutes: number): string {
    let hours = Math.floor(inputMinutes / 60);
    let minutes = Math.floor(inputMinutes - (hours * 60));
    if (hours > 0) return hours.toString() + 'h ' + minutes.toString() + 'm';
    else return minutes.toString() + 'm';
  }

  gamesToMythicNumbers(): number {
    let gap = 100 - this.data.mythicPercentile;
    let changePerGame = this.data.mythicPercentileChange;
    let games = gap / changePerGame;
    if (games <= 0 ) games = 0;
    return games;
  }

  timeToMythicNumbers(): string {
    let games = this.gamesToMythicNumbers();
    let timePerGame = this.data.deckTimePlayed / (this.data.winsWithDeck + this.data.lossesWithDeck);
    return this.formatTime(timePerGame * games);
  }

  gamesToSpecificMythicNumber(rank: number): number {
    let gap = rank - this.data.mythicRank;
    let changePerGame = this.data.mythicRankChange;
    let games = gap / changePerGame;
    if (games <= 0) games = 0;
    return games;
  }

  timeToSpecificMythicNumber(rank: number): string {
    let games = this.gamesToSpecificMythicNumber(rank);
    let timePerGame = this.data.deckTimePlayed / (this.data.winsWithDeck + this.data.lossesWithDeck);
    return this.formatTime(timePerGame * games);
  }
}

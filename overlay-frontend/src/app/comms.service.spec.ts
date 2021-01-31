import { TestBed } from '@angular/core/testing';

import { CommsService } from './comms.service';

describe('CommsService', () => {
  let service: CommsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CommsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

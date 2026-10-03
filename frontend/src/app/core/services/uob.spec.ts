import { TestBed } from '@angular/core/testing';

import { Uob } from './uob';

describe('Uob', () => {
  let service: Uob;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Uob);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

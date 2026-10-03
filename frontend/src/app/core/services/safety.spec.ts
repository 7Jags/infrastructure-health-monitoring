import { TestBed } from '@angular/core/testing';

import { Safety } from './safety';

describe('Safety', () => {
  let service: Safety;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Safety);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

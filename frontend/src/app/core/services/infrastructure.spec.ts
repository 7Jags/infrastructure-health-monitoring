import { TestBed } from '@angular/core/testing';

import { Infrastructure } from './infrastructure';

describe('Infrastructure', () => {
  let service: Infrastructure;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Infrastructure);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

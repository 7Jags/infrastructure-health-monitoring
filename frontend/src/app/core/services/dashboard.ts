import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { InfrastructureState } from './infrastructure';
import { VehicleState } from './vehicle';
import { SafetyAssessment } from './safety';
import { UobPacket } from './uob';

export interface DashboardSnapshot {
  infrastructure: InfrastructureState;
  vehicle: VehicleState;
  safety: SafetyAssessment;
  uob: UobPacket;
}

@Injectable({
  providedIn: 'root'
})
export class Dashboard {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/dashboard';

  getCurrentSnapshot(vehicleId: string): Observable<DashboardSnapshot> {
    return this.http.get<DashboardSnapshot>(
      `${this.apiUrl}/current/${vehicleId}`
    );
  }
}
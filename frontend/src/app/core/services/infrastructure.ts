import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface InfrastructureState {
  node_id: string;
  name: string;
  infrastructure_type: string;
  timestamp: string;

  load_percent: number;
  vibration_hz: number;
  strain: number;
  temperature_c: number;
  traffic_vehicles_per_hour: number;

  health: {
    health_percentage: number;
    risk_score: number;
    category: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class Infrastructure {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/infrastructure';

  // Generate a NEW simulated infrastructure reading
  getBridgeState(bridgeId: string): Observable<InfrastructureState> {
    return this.http.get<InfrastructureState>(
      `${this.apiUrl}/bridges/${bridgeId}/state`
    );
  }

  // Get the LAST infrastructure reading saved in the database
  getLatestBridgeState(bridgeId: string): Observable<InfrastructureState> {
    return this.http.get<InfrastructureState>(
      `${this.apiUrl}/bridges/${bridgeId}/latest`
    );
  }
}
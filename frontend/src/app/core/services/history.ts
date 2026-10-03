import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface InfrastructureHistory {
  id: number;
  node_id: string;
  recorded_at: string;
  load_percent: number;
  vibration_hz: number;
  strain: number;
  temperature_c: number;
  traffic_vehicles_per_hour: number;
  health_percentage: number;
  health_category: string;
}

@Injectable({
  providedIn: 'root'
})
export class History {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/history';

  getInfrastructureHistory(
    nodeId: string,
    limit: number = 50
  ): Observable<InfrastructureHistory[]> {

    return this.http.get<InfrastructureHistory[]>(
      `${this.apiUrl}/infrastructure/${nodeId}?limit=${limit}`
    );
  }
}
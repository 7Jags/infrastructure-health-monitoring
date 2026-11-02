import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

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

  private apiUrl = `${environment.apiUrl}/api/history`;

  getInfrastructureHistory(
    nodeId: string,
    limit: number = 50
  ): Observable<InfrastructureHistory[]> {

    return this.http.get<InfrastructureHistory[]>(
      `${this.apiUrl}/infrastructure/${nodeId}?limit=${limit}`
    );
  }
}
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UobPacket {
  packet_id: string;
  format_version: string;
  timestamp: string;
  source_node_id: string;
  target_vehicle_id: string;
  hazard_code: string;
  decision: 'green' | 'amber' | 'red';
  bridge_health_percentage: number;
  recommended_speed_kph: number;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class Uob {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/uob';

  /**
   * Get the current UOB packet without recording
   * a safety event in the database.
   */
  getCurrentUobPacket(
    vehicleId: string
  ): Observable<UobPacket> {

    return this.http.get<UobPacket>(
      `${this.apiUrl}/vehicles/${vehicleId}/current`
    );
  }

  /**
   * Get the UOB packet and record the associated
   * safety event in the database.
   */
  getLatestUobPacket(
    vehicleId: string
  ): Observable<UobPacket> {

    return this.http.get<UobPacket>(
      `${this.apiUrl}/vehicles/${vehicleId}/latest`
    );
  }
}
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface VehicleState {
  vehicle_id: string;
  vehicle_type: string;
  timestamp: string;
  approaching_node_id: string;
  speed_kph: number;
  mass_kg: number;
  road_friction: number;
  reaction_time_s: number;
}

@Injectable({
  providedIn: 'root'
})
export class Vehicle {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/vehicles';

  getVehicleState(vehicleId: string): Observable<VehicleState> {
    return this.http.get<VehicleState>(
      `${this.apiUrl}/${vehicleId}/state`
    );
  }
}
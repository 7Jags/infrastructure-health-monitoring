import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SafetyAssessment {
  decision: 'green' | 'amber' | 'red';
  recommended_speed_kph: number;
  stopping_distance_m: number;
  available_stopping_distance_m: number;
  safety_margin_m: number;
  message: string;
}

export interface SafetyVehicle {
  vehicle_id: string;
  vehicle_type: string;
  timestamp: string;
  approaching_node_id: string;
  speed_kph: number;
  mass_kg: number;
  road_friction: number;
  reaction_time_s: number;
}

export interface SafetyInfrastructure {
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

export interface VehicleSafetyResponse {
  vehicle: SafetyVehicle;
  infrastructure: SafetyInfrastructure;
  assessment: SafetyAssessment;
}

@Injectable({
  providedIn: 'root'
})
export class Safety {

  private http = inject(HttpClient);

  private apiUrl = 'http://127.0.0.1:8000/api/safety';

  getCurrentVehicleSafetyDecision(
    vehicleId: string
  ): Observable<VehicleSafetyResponse> {

    return this.http.get<VehicleSafetyResponse>(
      `${this.apiUrl}/vehicles/${vehicleId}/current`
    );
  }

  getVehicleSafetyDecision(
    vehicleId: string
  ): Observable<VehicleSafetyResponse> {

    return this.http.get<VehicleSafetyResponse>(
      `${this.apiUrl}/vehicles/${vehicleId}/decision`
    );
  }
}
import {
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit,
  inject
} from '@angular/core';

import {
  Dashboard as DashboardService,
  DashboardSnapshot
} from '../../core/services/dashboard';

import {
  History,
  InfrastructureHistory
} from '../../core/services/history';

@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit, OnDestroy {

  private dashboardService = inject(DashboardService);
  private historyService = inject(History);
  private cdr = inject(ChangeDetectorRef);

  private refreshInterval: ReturnType<typeof setInterval> | null = null;

  infrastructure: DashboardSnapshot['infrastructure'] | null = null;
  vehicle: DashboardSnapshot['vehicle'] | null = null;
  safety: DashboardSnapshot['safety'] | null = null;
  uob: DashboardSnapshot['uob'] | null = null;

  infrastructureHistory: InfrastructureHistory[] = [];

  analyticsView = false;

  get analyticsHistory(): InfrastructureHistory[] {
    return [...this.infrastructureHistory].reverse();
  }

  isDarkMode = false;
  activeSection = 'overview';
  selectedVehicleId = 'V-001';

  availableVehicles = [
    'V-001',
    'V-002',
    'V-003'
  ];

  ngOnInit(): void {
    console.log('Dashboard initialized');

    // Load the initial live dashboard state.
    this.refreshDashboard();

    // Load history once when the dashboard starts.
    this.loadInfrastructureHistory();

    // Continuously refresh only the live dashboard.
    this.refreshInterval = setInterval(() => {
      this.refreshDashboard();
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.refreshInterval !== null) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }

    console.log('Dashboard destroyed');
  }

  refreshDashboard(): void {
    this.loadCurrentSnapshot(this.selectedVehicleId);
  }

  loadCurrentSnapshot(vehicleId: string): void {
    this.dashboardService
      .getCurrentSnapshot(vehicleId)
      .subscribe({
        next: (data: DashboardSnapshot) => {

          this.infrastructure = data.infrastructure;
          this.vehicle = data.vehicle;
          this.safety = data.safety;
          this.uob = data.uob;

          console.log(
            'Unified dashboard snapshot:',
            data
          );

          this.cdr.detectChanges();
        },

        error: (error: unknown) => {
          console.error(
            'Dashboard snapshot API error:',
            error
          );

          this.infrastructure = null;
          this.vehicle = null;
          this.safety = null;
          this.uob = null;

          this.cdr.detectChanges();
        }
      });
  }

  loadInfrastructureHistory(): void {
    this.historyService
      .getInfrastructureHistory('BR-001', 50)
      .subscribe({
        next: (data) => {
          this.infrastructureHistory = data;

          console.log(
            'Infrastructure history loaded:',
            data
          );

          this.cdr.detectChanges();
        },

        error: (error: unknown) => {
          console.error(
            'Infrastructure history API error:',
            error
          );

          this.infrastructureHistory = [];

          this.cdr.detectChanges();
        }
      });
  }

  setActiveSection(section: string): void {
    this.activeSection = section;
    this.analyticsView = section === 'analytics';

    // Refresh history when Analytics is opened.
    if (this.analyticsView) {
      this.loadInfrastructureHistory();
    }
  }

  onVehicleChange(event: Event): void {
    const select = event.target as HTMLSelectElement;

    const vehicleId = select.value;

    console.log(
      'Vehicle selected:',
      vehicleId
    );

    this.selectedVehicleId = vehicleId;

    // Immediately load the complete snapshot
    // for the newly selected vehicle.
    this.loadCurrentSnapshot(vehicleId);
  }

  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
  }

  get healthGaugeAngle(): number {
    const health =
      this.infrastructure?.health?.health_percentage ?? 0;

    return Math.max(
      0,
      Math.min(100, health)
    ) * 3.6;
  }
}
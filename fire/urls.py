from django.urls import path
from . import views

app_name = 'fire'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/analytics/', views.DashboardAnalyticsView.as_view(), name='dashboard_analytics'),
    
    # Incidents
    path('incidents/', views.IncidentListView.as_view(), name='incident_list'),
    path('incidents/create/', views.IncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/', views.IncidentDetailView.as_view(), name='incident_detail'),
    path('incidents/<int:pk>/edit/', views.IncidentUpdateView.as_view(), name='incident_edit'),
    path('incidents/<int:pk>/delete/', views.IncidentDeleteView.as_view(), name='incident_delete'),
    
    # Fire Stations
    path('stations/', views.StationListView.as_view(), name='station_list'),
    path('stations/create/', views.StationCreateView.as_view(), name='station_create'),
    path('stations/<int:pk>/', views.StationDetailView.as_view(), name='station_detail'),
    path('stations/<int:pk>/edit/', views.StationUpdateView.as_view(), name='station_edit'),
    path('stations/<int:pk>/delete/', views.StationDeleteView.as_view(), name='station_delete'),
    
    # Firefighters
    path('firefighters/', views.FirefighterListView.as_view(), name='firefighter_list'),
    path('firefighters/create/', views.FirefighterCreateView.as_view(), name='firefighter_create'),
    path('firefighters/<int:pk>/', views.FirefighterDetailView.as_view(), name='firefighter_detail'),
    path('firefighters/<int:pk>/edit/', views.FirefighterUpdateView.as_view(), name='firefighter_edit'),
    path('firefighters/<int:pk>/delete/', views.FirefighterDeleteView.as_view(), name='firefighter_delete'),
    
    # Fire Trucks
    path('trucks/', views.FireTruckListView.as_view(), name='truck_list'),
    path('trucks/create/', views.FireTruckCreateView.as_view(), name='truck_create'),
    path('trucks/<int:pk>/', views.FireTruckDetailView.as_view(), name='truck_detail'),
    path('trucks/<int:pk>/edit/', views.FireTruckUpdateView.as_view(), name='truck_edit'),
    path('trucks/<int:pk>/delete/', views.FireTruckDeleteView.as_view(), name='truck_delete'),
    
    # Maps
    path('maps/stations/', views.StationsMapView.as_view(), name='stations_map'),
    path('maps/incidents/', views.IncidentsMapView.as_view(), name='incidents_map'),
    
    # Authentication
    path('logout/', views.logout_view, name='logout'),
    path('api/incident-trends/', views.incident_trends_api, name='incident_trends_api'),
] 
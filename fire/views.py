from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Incident, FireStation, Firefighters, FireTruck, WeatherConditions, Locations
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models.functions import TruncMonth, TruncDate, TruncWeek

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('fire:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'fire/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        context['total_incidents'] = Incident.objects.count()
        context['active_incidents'] = Incident.objects.filter(
            date_time__gte=timezone.now() - timedelta(days=1)
        ).count()
        context['total_stations'] = FireStation.objects.count()
        context['total_firefighters'] = Firefighters.objects.count()
        context['recent_incidents'] = Incident.objects.select_related('location').order_by('-date_time')[:5]
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        
        # Overview stats
        context['total_incidents'] = Incident.objects.count()
        context['total_stations'] = FireStation.objects.count()
        context['total_firefighters'] = Firefighters.objects.count()
        context['total_trucks'] = FireTruck.objects.count()
        
        # Recent incidents
        context['recent_incidents'] = Incident.objects.all().order_by('-date_time')[:5]
        
        # Incident Trends Chart Data
        last_6_months = timezone.now() - timedelta(days=180)
        monthly_incidents = Incident.objects.filter(
            date_time__gte=last_6_months
        ).annotate(
            month=TruncMonth('date_time')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Format incident trends data
        context['incident_trends'] = {
            'labels': [incident['month'].strftime('%b %Y') for incident in monthly_incidents],
            'data': [incident['count'] for incident in monthly_incidents]
        }
        
        # Severity Distribution Chart Data
        severity_data = Incident.objects.values('severity_level').annotate(
            count=Count('id')
        ).order_by('severity_level')
        
        context['severity_distribution'] = {
            'labels': [item['severity_level'] for item in severity_data],
            'data': [item['count'] for item in severity_data]
        }
        
        # Station Performance Chart Data
        station_performance = []
        for station in FireStation.objects.all():
            # Convert Decimal to float for calculations
            station_lat = float(station.latitude)
            station_lon = float(station.longitude)
            
            # Calculate incidents handled by this station
            nearby_incidents = Incident.objects.filter(
                location__latitude__range=(station_lat - 0.1, station_lat + 0.1),
                location__longitude__range=(station_lon - 0.1, station_lon + 0.1)
            )
            
            # Calculate performance metrics
            total_incidents = nearby_incidents.count()
            high_severity_incidents = nearby_incidents.filter(severity_level='HIGH').count()
            
            # Calculate performance score
            performance_score = 0
            if total_incidents > 0:
                base_score = min(total_incidents * 10, 100)
                severity_penalty = high_severity_incidents * 5
                performance_score = max(base_score - severity_penalty, 0)
            
            station_performance.append({
                'name': station.name,
                'performance': round(performance_score, 1)
            })
        
        context['station_performance'] = {
            'labels': [item['name'] for item in station_performance],
            'data': [item['performance'] for item in station_performance]
        }
        
        # Response Time Data (using time difference between created_at and date_time)
        response_time_data = []
        for station in FireStation.objects.all():
            station_lat = float(station.latitude)
            station_lon = float(station.longitude)
            
            nearby_incidents = Incident.objects.filter(
                location__latitude__range=(station_lat - 0.1, station_lat + 0.1),
                location__longitude__range=(station_lon - 0.1, station_lon + 0.1)
            )
            
            # Calculate average response time based on time difference
            total_time = timedelta()
            incident_count = 0
            
            for incident in nearby_incidents:
                if incident.created_at and incident.date_time:
                    time_diff = incident.created_at - incident.date_time
                    if time_diff.total_seconds() > 0:  # Only count positive time differences
                        total_time += time_diff
                        incident_count += 1
            
            avg_response_time = 0
            if incident_count > 0:
                avg_response_time = total_time.total_seconds() / incident_count / 60  # Convert to minutes
            
            response_time_data.append({
                'name': station.name,
                'time': round(avg_response_time, 1)
            })
        
        context['response_time_data'] = {
            'labels': [item['name'] for item in response_time_data],
            'data': [item['time'] for item in response_time_data]
        }
        
        return context

class DashboardAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/dashboard_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        
        # Overview stats
        context['total_incidents'] = Incident.objects.count()
        context['total_stations'] = FireStation.objects.count()
        context['total_firefighters'] = Firefighters.objects.count()
        context['total_trucks'] = FireTruck.objects.count()
        
        # Recent incidents
        context['recent_incidents'] = Incident.objects.all().order_by('-date_time')[:5]
        
        # Incident Trends Chart Data
        last_6_months = timezone.now() - timedelta(days=180)
        monthly_incidents = Incident.objects.filter(
            date_time__gte=last_6_months
        ).annotate(
            month=TruncMonth('date_time')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        context['incident_trends'] = {
            'labels': [incident['month'].strftime('%b %Y') for incident in monthly_incidents],
            'data': [incident['count'] for incident in monthly_incidents]
        }
        
        # Severity Distribution Chart Data
        severity_data = Incident.objects.values('severity_level').annotate(
            count=Count('id')
        ).order_by('severity_level')
        
        context['severity_distribution'] = {
            'labels': [item['severity_level'] for item in severity_data],
            'data': [item['count'] for item in severity_data]
        }
        
        # Station Performance Chart Data
        station_performance = []
        for station in FireStation.objects.all():
            # Convert Decimal to float for calculations
            station_lat = float(station.latitude)
            station_lon = float(station.longitude)
            
            # Calculate incidents handled by this station
            nearby_incidents = Incident.objects.filter(
                location__latitude__range=(station_lat - 0.1, station_lat + 0.1),
                location__longitude__range=(station_lon - 0.1, station_lon + 0.1)
            )
            
            # Calculate performance metrics
            total_incidents = nearby_incidents.count()
            high_severity_incidents = nearby_incidents.filter(severity_level='HIGH').count()
            
            # Calculate performance score
            performance_score = 0
            if total_incidents > 0:
                base_score = min(total_incidents * 10, 100)
                severity_penalty = high_severity_incidents * 5
                performance_score = max(base_score - severity_penalty, 0)
            
            station_performance.append({
                'name': station.name,
                'performance': round(performance_score, 1)
            })
        
        context['station_performance'] = {
            'labels': [item['name'] for item in station_performance],
            'data': [item['performance'] for item in station_performance]
        }
        
        # Response Time Data
        response_time_data = []
        for station in FireStation.objects.all():
            # Get incidents near this station
            station_lat = float(station.latitude)
            station_lon = float(station.longitude)
            
            nearby_incidents = Incident.objects.filter(
                location__latitude__range=(station_lat - 0.1, station_lat + 0.1),
                location__longitude__range=(station_lon - 0.1, station_lon + 0.1)
            )
            
            # Calculate average response time based on time difference
            total_time = timedelta()
            incident_count = 0
            
            for incident in nearby_incidents:
                if incident.created_at and incident.date_time:
                    time_diff = incident.created_at - incident.date_time
                    if time_diff.total_seconds() > 0:  # Only count positive time differences
                        total_time += time_diff
                        incident_count += 1
            
            avg_response_time = 0
            if incident_count > 0:
                avg_response_time = total_time.total_seconds() / incident_count / 60  # Convert to minutes
            
            response_time_data.append({
                'name': station.name,
                'time': round(avg_response_time, 1)
            })
        
        context['response_time_data'] = {
            'labels': [item['name'] for item in response_time_data],
            'data': [item['time'] for item in response_time_data]
        }
        
        return context

class StationListView(LoginRequiredMixin, ListView):
    model = FireStation
    template_name = 'fire/station_list.html'
    context_object_name = 'stations'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class StationDetailView(LoginRequiredMixin, DetailView):
    model = FireStation
    template_name = 'fire/station_detail.html'
    context_object_name = 'station'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class StationCreateView(LoginRequiredMixin, CreateView):
    model = FireStation
    template_name = 'fire/station_form.html'
    fields = ['name', 'address', 'contact_number', 'latitude', 'longitude']
    success_url = reverse_lazy('fire:station_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class StationUpdateView(LoginRequiredMixin, UpdateView):
    model = FireStation
    template_name = 'fire/station_form.html'
    fields = ['name', 'address', 'contact_number', 'latitude', 'longitude']
    success_url = reverse_lazy('fire:station_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class StationDeleteView(LoginRequiredMixin, DeleteView):
    model = FireStation
    template_name = 'fire/station_confirm_delete.html'
    success_url = reverse_lazy('fire:station_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class IncidentListView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'fire/incident_list.html'
    context_object_name = 'incidents'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context
    
    def get_queryset(self):
        return Incident.objects.select_related('location').order_by('-date_time')

class IncidentDetailView(LoginRequiredMixin, DetailView):
    model = Incident
    template_name = 'fire/incident_detail.html'
    context_object_name = 'incident'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = Incident
    template_name = 'fire/incident_form.html'
    fields = ['location', 'severity_level', 'description']
    success_url = reverse_lazy('fire:incident_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        # Get the date_time from the form data
        date_time = self.request.POST.get('date_time')
        if date_time:
            form.instance.date_time = date_time
        
        # Save the form first
        response = super().form_valid(form)
        
        # Only add the success message if the form was successfully saved
        if self.object:
            messages.success(self.request, 'Saved successfully', extra_tags='toast')
        
        return response

class IncidentUpdateView(LoginRequiredMixin, UpdateView):
    model = Incident
    template_name = 'fire/incident_form.html'
    fields = ['location', 'severity_level', 'description']
    success_url = reverse_lazy('fire:incident_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        # Get the date_time from the form data
        date_time = self.request.POST.get('date_time')
        if date_time:
            form.instance.date_time = date_time
        return super().form_valid(form)

class IncidentDeleteView(LoginRequiredMixin, DeleteView):
    model = Incident
    template_name = 'fire/incident_confirm_delete.html'
    success_url = reverse_lazy('fire:incident_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Deleted successfully', extra_tags='toast')
        return response

class FirefighterListView(LoginRequiredMixin, ListView):
    model = Firefighters
    template_name = 'fire/firefighter_list.html'
    context_object_name = 'firefighters'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class FirefighterDetailView(LoginRequiredMixin, DetailView):
    model = Firefighters
    template_name = 'fire/firefighter_detail.html'
    context_object_name = 'firefighter'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class FirefighterCreateView(LoginRequiredMixin, CreateView):
    model = Firefighters
    template_name = 'fire/firefighter_form.html'
    fields = ['name', 'rank', 'station', 'contact_number', 'email']
    success_url = reverse_lazy('fire:firefighter_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Firefighter {form.instance.name} was successfully created.', extra_tags='toast')
        return response

class FirefighterUpdateView(LoginRequiredMixin, UpdateView):
    model = Firefighters
    template_name = 'fire/firefighter_form.html'
    fields = ['name', 'rank', 'station', 'contact_number', 'email']
    success_url = reverse_lazy('fire:firefighter_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Firefighter {form.instance.name} was successfully updated.', extra_tags='toast')
        return response

class FirefighterDeleteView(LoginRequiredMixin, DeleteView):
    model = Firefighters
    template_name = 'fire/firefighter_confirm_delete.html'
    success_url = reverse_lazy('fire:firefighter_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class FireTruckListView(LoginRequiredMixin, ListView):
    model = FireTruck
    template_name = 'fire/truck_list.html'
    context_object_name = 'trucks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class FireTruckDetailView(LoginRequiredMixin, DetailView):
    model = FireTruck
    template_name = 'fire/truck_detail.html'
    context_object_name = 'truck'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class FireTruckCreateView(LoginRequiredMixin, CreateView):
    model = FireTruck
    template_name = 'fire/truck_form.html'
    fields = ['truck_number', 'station', 'status', 'capacity']
    success_url = reverse_lazy('fire:truck_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fire Truck {form.instance.truck_number} was successfully created.', extra_tags='toast')
        return response

class FireTruckUpdateView(LoginRequiredMixin, UpdateView):
    model = FireTruck
    template_name = 'fire/truck_form.html'
    fields = ['truck_number', 'station', 'status', 'capacity']
    success_url = reverse_lazy('fire:truck_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fire Truck {form.instance.truck_number} was successfully updated.', extra_tags='toast')
        return response

class FireTruckDeleteView(LoginRequiredMixin, DeleteView):
    model = FireTruck
    template_name = 'fire/truck_confirm_delete.html'
    success_url = reverse_lazy('fire:truck_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class LocationListView(LoginRequiredMixin, ListView):
    model = Locations
    template_name = 'fire/location_list.html'
    context_object_name = 'locations'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Locations
    template_name = 'fire/location_form.html'
    fields = ['name', 'address', 'latitude', 'longitude']
    success_url = reverse_lazy('fire:location_list')

class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Locations
    template_name = 'fire/location_form.html'
    fields = ['name', 'address', 'latitude', 'longitude']
    success_url = reverse_lazy('fire:location_list')

class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Locations
    template_name = 'fire/location_confirm_delete.html'
    success_url = reverse_lazy('fire:location_list')

class WeatherConditionListView(LoginRequiredMixin, ListView):
    model = WeatherConditions
    template_name = 'fire/weather_list.html'
    context_object_name = 'weather_conditions'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

class WeatherConditionCreateView(LoginRequiredMixin, CreateView):
    model = WeatherConditions
    template_name = 'fire/weather_form.html'
    fields = ['location', 'temperature', 'humidity', 'wind_speed', 'wind_direction', 'precipitation', 'date_time']
    success_url = reverse_lazy('fire:weather_list')

class WeatherConditionUpdateView(LoginRequiredMixin, UpdateView):
    model = WeatherConditions
    template_name = 'fire/weather_form.html'
    fields = ['location', 'temperature', 'humidity', 'wind_speed', 'wind_direction', 'precipitation', 'date_time']
    success_url = reverse_lazy('fire:weather_list')

class WeatherConditionDeleteView(LoginRequiredMixin, DeleteView):
    model = WeatherConditions
    template_name = 'fire/weather_confirm_delete.html'
    success_url = reverse_lazy('fire:weather_list')

class StationsMapView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/map_stations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        
        # Get all fire stations from the database
        fire_stations = FireStation.objects.all()
        
        # Prepare the stations data with their associated trucks
        stations_data = []
        for station in fire_stations:
            # Get all trucks associated with this station
            trucks = FireTruck.objects.filter(station=station)
            
            # Format truck data
            truck_data = [{
                'truck_number': truck.truck_number,
                'model': truck.model,
                'capacity': truck.capacity
            } for truck in trucks]
            
            # Create station dictionary with all required data
            station_data = {
                'name': station.name,
                'latitude': float(station.latitude) if station.latitude else 0,
                'longitude': float(station.longitude) if station.longitude else 0,
                'address': station.address,
                'phone': '(048) 434-7701',  
                'coverage': f'{station.city} Area',  
                'trucks': truck_data
            }
            stations_data.append(station_data)

        context['stations'] = stations_data
        return context

class IncidentsMapView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/incidents_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        context['incidents'] = Incident.objects.all()
        return context

@login_required
def incident_statistics(request):
    total_incidents = Incident.objects.count()
    active_incidents = Incident.objects.filter(status='ACTIVE').count()
    incidents_by_severity = Incident.objects.values('severity').annotate(count=Count('id'))
    incidents_by_status = Incident.objects.values('status').annotate(count=Count('id'))
    
    return JsonResponse({
        'total_incidents': total_incidents,
        'active_incidents': active_incidents,
        'by_severity': list(incidents_by_severity),
        'by_status': list(incidents_by_status)
    })

@login_required
def station_statistics(request):
    total_stations = FireStation.objects.count()
    total_firefighters = Firefighters.objects.count()
    
    # Count firefighters by station name
    firefighters_by_station = []
    for station in FireStation.objects.all():
        count = Firefighters.objects.filter(station=station.name).count()
        firefighters_by_station.append({
            'station_name': station.name,
            'count': count
        })
    
    return JsonResponse({
        'total_stations': total_stations,
        'total_firefighters': total_firefighters,
        'firefighters_by_station': firefighters_by_station
    })

@login_required
def weather_statistics(request):
    weather_data = WeatherConditions.objects.select_related('incident').order_by('-created_at')[:24]
    return JsonResponse({
        'weather_data': list(weather_data.values(
            'incident__location__name', 'temperature', 'humidity', 'wind_speed', 'wind_direction', 'precipitation', 'created_at'
        ))
    })

# API Views
@login_required
def incident_list(request):
    incidents = Incident.objects.all()
    data = [{
        'id': incident.id,
        'location': incident.location.name,
        'severity': incident.severity,
        'status': incident.status,
        'date_time': incident.date_time,
    } for incident in incidents]
    return JsonResponse(data, safe=False)

@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    data = {
        'id': incident.id,
        'location': incident.location.name,
        'severity': incident.severity,
        'status': incident.status,
        'date_time': incident.date_time,
        'description': incident.description,
    }
    return JsonResponse(data)

@login_required
def station_list(request):
    stations = FireStation.objects.all()
    data = [{
        'id': station.id,
        'name': station.name,
        'address': station.address,
        'latitude': station.latitude,
        'longitude': station.longitude,
    } for station in stations]
    return JsonResponse(data, safe=False)

@login_required
def station_detail(request, pk):
    station = get_object_or_404(FireStation, pk=pk)
    data = {
        'id': station.id,
        'name': station.name,
        'address': station.address,
        'latitude': station.latitude,
        'longitude': station.longitude,
        'contact_number': station.contact_number,
    }
    return JsonResponse(data)

@login_required
def firefighter_list(request):
    firefighters = Firefighters.objects.all()
    data = [{
        'id': firefighter.id,
        'name': firefighter.name,
        'rank': firefighter.rank,
        'station': firefighter.station,
    } for firefighter in firefighters]
    return JsonResponse(data, safe=False)

@login_required
def firefighter_detail(request, pk):
    firefighter = get_object_or_404(Firefighters, pk=pk)
    data = {
        'id': firefighter.id,
        'name': firefighter.name,
        'rank': firefighter.rank,
        'station': firefighter.station,
        'contact_number': firefighter.contact_number,
        'email': firefighter.email,
    }
    return JsonResponse(data)

@login_required
def truck_list(request):
    trucks = FireTruck.objects.all()
    data = [{
        'id': truck.id,
        'vehicle_number': truck.vehicle_number,
        'type': truck.type,
        'station': truck.station.name,
        'status': truck.status,
    } for truck in trucks]
    return JsonResponse(data, safe=False)

@login_required
def truck_detail(request, pk):
    truck = get_object_or_404(FireTruck, pk=pk)
    data = {
        'id': truck.id,
        'vehicle_number': truck.vehicle_number,
        'type': truck.type,
        'station': truck.station.name,
        'status': truck.status,
    }
    return JsonResponse(data)

@login_required
def weather_data(request):
    weather = WeatherConditions.objects.latest('created_at')
    data = {
        'temperature': weather.temperature,
        'humidity': weather.humidity,
        'wind_speed': weather.wind_speed,
        'wind_direction': weather.wind_direction,
        'timestamp': weather.created_at,
    }
    return JsonResponse(data)

def incident_trends_api(request):
    """API endpoint for incident trends data"""
    time_range = request.GET.get('time_range', 'month')
    end_date = timezone.now()
    
    # Calculate start date based on time range
    if time_range == 'week':
        start_date = end_date - timedelta(days=7)
        trunc_func = TruncDate
        format_str = '%Y-%m-%d'
    elif time_range == 'year':
        start_date = end_date - timedelta(days=365)
        trunc_func = TruncMonth
        format_str = '%Y-%m'
    else:  # month
        start_date = end_date - timedelta(days=30)
        trunc_func = TruncDate
        format_str = '%Y-%m-%d'

    # Get all fire stations
    stations = FireStation.objects.all()
    station_data = {}

    # Initialize data structure for each station
    for station in stations:
        station_data[station.name] = {
            'incidents': [],
            'response_times': []
        }

    # Query incidents within the date range
    incidents = Incident.objects.filter(
        date_time__range=(start_date, end_date)
    ).select_related('location').annotate(
        period=trunc_func('date_time')
    ).values('period', 'location__name').annotate(
        count=Count('id')
    ).order_by('period', 'location__name')

    # Create a dictionary of all possible periods
    period_data = {}
    current = start_date
    while current <= end_date:
        if time_range == 'week':
            period_key = current.strftime(format_str)
            period_data[period_key] = {station.name: 0 for station in stations}
            current += timedelta(days=1)
        elif time_range == 'year':
            period_key = current.strftime(format_str)
            period_data[period_key] = {station.name: 0 for station in stations}
            # Move to first day of next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)
        else:  # month
            period_key = current.strftime(format_str)
            period_data[period_key] = {station.name: 0 for station in stations}
            current += timedelta(days=1)

    # Update with actual incident counts
    for incident in incidents:
        period_key = incident['period'].strftime(format_str)
        station_name = incident['location__name']
        if period_key in period_data and station_name in period_data[period_key]:
            period_data[period_key][station_name] = incident['count']

    # Format data for chart
    labels = []
    datasets = []

    # Convert to lists for chart
    for period in sorted(period_data.keys()):
        if time_range == 'week':
            labels.append(datetime.strptime(period, format_str).strftime('%a'))
        elif time_range == 'year':
            labels.append(datetime.strptime(period, format_str).strftime('%b %Y'))
        else:  # month
            labels.append(datetime.strptime(period, format_str).strftime('%d %b'))

    # Create dataset for each station
    colors = ['#696cff', '#8592a3', '#71dd37', '#ff3e1d', '#03c3ec', '#ffab00']
    for i, station in enumerate(stations):
        station_counts = [period_data[period][station.name] for period in sorted(period_data.keys())]
        datasets.append({
            'label': station.name,
            'data': station_counts,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',  # Add transparency
            'tension': 0.4,
            'fill': False
        })

    return JsonResponse({
        'labels': labels,
        'datasets': datasets
    })

class ChartView(LoginRequiredMixin, TemplateView):
    template_name = 'fire/chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        
        # Get incident statistics for charts
        context['total_incidents'] = Incident.objects.count()
        context['total_stations'] = FireStation.objects.count()
        context['total_firefighters'] = Firefighters.objects.count()
        context['total_trucks'] = FireTruck.objects.count()
        
        # Get recent incidents
        context['recent_incidents'] = Incident.objects.all().order_by('-date_time')[:5]
        
        # Get incident statistics
        recent_incidents = Incident.objects.filter(
            date_time__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        incidents_by_severity = Incident.objects.values('severity_level').annotate(
            count=Count('id')
        ).order_by('severity_level')
        
        # Get incidents by date (last 30 days)
        incidents_by_date = Incident.objects.filter(
            date_time__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            date=TruncDate('date_time')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        context['incident_statistics'] = {
            'total_incidents': context['total_incidents'],
            'recent_incidents': recent_incidents,
            'by_severity': list(incidents_by_severity),
            'by_date': list(incidents_by_date)
        }
        
        return context
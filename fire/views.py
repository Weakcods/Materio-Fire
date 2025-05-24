from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Incident, FireStation, Firefighters, FireTruck, WeatherConditions, Locations
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages

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
        context['active_incidents'] = Incident.objects.filter(
            date_time__gte=timezone.now() - timedelta(days=1)
        ).count()
        context['total_stations'] = FireStation.objects.count()
        context['total_firefighters'] = Firefighters.objects.count()
        context['total_trucks'] = FireTruck.objects.count()
        
        # Recent incidents
        context['recent_incidents'] = Incident.objects.all().order_by('-date_time')[:5]
        
        # Recent firefighters
        context['recent_firefighters'] = Firefighters.objects.all().order_by('-id')[:5]
        
        # Recent trucks
        context['recent_trucks'] = FireTruck.objects.all().order_by('-id')[:5]
        
        # Weather data
        try:
            context['weather'] = WeatherConditions.objects.latest('created_at')
        except WeatherConditions.DoesNotExist:
            context['weather'] = {
                'temperature': 0,
                'condition': 'No data',
                'humidity': 0,
                'wind_speed': 0
            }
        
        # Statistics for charts
        context['incident_stats'] = Incident.objects.values('severity_level').annotate(
            count=Count('id')
        ).order_by('severity_level')
        
        # Get station statistics by counting firefighters assigned to each station
        station_stats = []
        for station in FireStation.objects.all():
            firefighter_count = Firefighters.objects.filter(station=station.name).count()
            station_stats.append({
                'name': station.name,
                'firefighters_count': firefighter_count
            })
        context['station_stats'] = station_stats
        
        context['firefighter_stats'] = Firefighters.objects.values('rank').annotate(
            count=Count('id')
        ).order_by('rank')
        
        # All stations for map
        context['stations'] = FireStation.objects.all()
        
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
        return super().form_valid(form)

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

class FirefighterUpdateView(LoginRequiredMixin, UpdateView):
    model = Firefighters
    template_name = 'fire/firefighter_form.html'
    fields = ['name', 'rank', 'station', 'contact_number', 'email']
    success_url = reverse_lazy('fire:firefighter_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

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

class FireTruckUpdateView(LoginRequiredMixin, UpdateView):
    model = FireTruck
    template_name = 'fire/truck_form.html'
    fields = ['truck_number', 'station', 'status', 'capacity']
    success_url = reverse_lazy('fire:truck_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['layout_path'] = 'layouts/master.html'
        return context

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
        context['stations'] = FireStation.objects.all()
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
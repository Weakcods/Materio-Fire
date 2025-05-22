from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.db import connection, models
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count, Q
from fire.models import Locations, Incident, FireStation, FireTruck
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberme')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'auth/login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Set session expiry based on remember me checkbox
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                # Add success message for toast
                messages.success(request, f'Welcome back, {user.username}! Login successful.')
                
                # Check if there's a next URL in the query parameters
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Your account is disabled')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

class HomePageView(LoginRequiredMixin, ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"
    login_url = '/login/'
    
class ChartView(LoginRequiredMixin, ListView):
    template_name = 'chart.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass
    
def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

@login_required(login_url='/login/')
def map_station(request):
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
            'phone': '(048) 434-7701',  # You might want to add a phone field to your FireStation model
            'coverage': f'{station.city} Area',  # Using city as coverage area
            'trucks': truck_data
        }
        stations_data.append(station_data)

    context = {
        'stations': stations_data,
    }

    return render(request, 'map_station.html', context)

@login_required(login_url='/login/')
def map_incidents(request):
    # Define Philippine cities (you can add more as needed)
    PHILIPPINE_CITIES = [
        'Puerto Princesa',
        'Manila',
        'Quezon City',
        'Davao City',
        'Cebu City',
        'Makati',
        'Taguig',
        'Pasig',
        'Mandaluyong',
        'Baguio'
    ]
    
    # Get the selected city from the query parameters
    selected_city = request.GET.get('city', '')
    
    # Get all cities that have incidents
    db_cities = set(Locations.objects.values_list('city', flat=True).distinct())
    
    # Combine database cities with predefined Philippine cities
    all_cities = sorted(set(PHILIPPINE_CITIES) | db_cities)
    
    # Base query
    incidents_query = Incident.objects.select_related('location')
    
    # Apply city filter if selected
    if selected_city:
        incidents_query = incidents_query.filter(location__city=selected_city)
    
    # Get the incidents data with all necessary information
    incidents = incidents_query.values(
        'location__latitude', 
        'location__longitude',
        'severity_level',
        'date_time',
        'location__city',
        'location__address',
        'description'
    ).order_by('-date_time')  # Most recent incidents first

    # Process the incidents data
    incidents_list = []
    for incident in incidents:
        incidents_list.append({
            'latitude': float(incident['location__latitude']),
            'longitude': float(incident['location__longitude']),
            'severity_level': incident['severity_level'],
            'date_time': incident['date_time'].strftime('%Y-%m-%d %H:%M:%S') if incident['date_time'] else 'Date not available',
            'city': incident['location__city'],
            'address': incident['location__address'],
            'description': incident['description']
        })

    context = {
        'incidents': incidents_list,
        'cities': all_cities,
        'selected_city': selected_city,
    }

    return render(request, 'map_incidents.html', context)
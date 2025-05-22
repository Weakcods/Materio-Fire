# Fire Management System

A comprehensive web-based fire management system built with Django and Materio UI template. This system helps manage fire incidents, fire stations, firefighters, and fire trucks efficiently.

## Features

### Dashboard
- Real-time overview of active incidents
- Weather conditions monitoring
- Fire station statistics
- Firefighter distribution
- Interactive maps for stations and incidents
- Recent incidents and activities tracking

### Incident Management
- Track and manage fire incidents
- Severity level classification
- Location-based incident mapping
- Detailed incident reporting
- Historical incident data

### Fire Station Management
- Manage multiple fire stations
- Station capacity tracking
- Location mapping
- Contact information management
- Resource allocation

### Firefighter Management
- Personnel tracking
- Rank management
- Station assignment
- Contact information
- Performance monitoring

### Fire Truck Management
- Vehicle tracking
- Maintenance status
- Capacity monitoring
- Station assignment
- Status updates

### Weather Monitoring
- Real-time weather conditions
- Temperature tracking
- Humidity monitoring
- Wind speed and direction
- Precipitation data

## Technical Stack

- **Backend**: Django 5.0
- **Frontend**: 
  - Materio UI Template
  - Bootstrap 5
  - ApexCharts for data visualization
  - Leaflet for interactive maps
- **Database**: SQLite (default) / PostgreSQL (recommended for production)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fire-management.git
cd fire-management
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
fire-management/
├── apps/
│   └── fire/
│       ├── models.py          # Database models
│       ├── views.py          # View logic
│       ├── urls.py           # URL routing
│       └── templates/        # HTML templates
├── config/                   # Project configuration
├── static/                   # Static files
├── templates/               # Base templates
└── manage.py               # Django management script
```

## Models

### Incident
- Location
- Severity Level
- Description
- Date/Time
- Status

### FireStation
- Name
- Address
- Contact Number
- Latitude/Longitude
- Capacity

### Firefighter
- Name
- Rank
- Station
- Contact Information
- Email

### FireTruck
- Truck Number
- Station
- Status
- Capacity
- Last Maintenance

### WeatherCondition
- Location
- Temperature
- Humidity
- Wind Speed
- Wind Direction
- Precipitation
- Timestamp

## Usage

1. Access the dashboard at `http://localhost:8000/fire/dashboard/`
2. Log in with your superuser credentials
3. Navigate through different sections using the sidebar menu
4. Monitor incidents, stations, and resources
5. Generate reports and analyze data

## API Endpoints

### Incidents
- `GET /api/incidents/` - List all incidents
- `GET /api/incidents/<id>/` - Get incident details
- `POST /api/incidents/` - Create new incident
- `PUT /api/incidents/<id>/` - Update incident
- `DELETE /api/incidents/<id>/` - Delete incident

### Fire Stations
- `GET /api/stations/` - List all stations
- `GET /api/stations/<id>/` - Get station details
- `POST /api/stations/` - Create new station
- `PUT /api/stations/<id>/` - Update station
- `DELETE /api/stations/<id>/` - Delete station

### Firefighters
- `GET /api/firefighters/` - List all firefighters
- `GET /api/firefighters/<id>/` - Get firefighter details
- `POST /api/firefighters/` - Create new firefighter
- `PUT /api/firefighters/<id>/` - Update firefighter
- `DELETE /api/firefighters/<id>/` - Delete firefighter

### Fire Trucks
- `GET /api/trucks/` - List all trucks
- `GET /api/trucks/<id>/` - Get truck details
- `POST /api/trucks/` - Create new truck
- `PUT /api/trucks/<id>/` - Update truck
- `DELETE /api/trucks/<id>/` - Delete truck

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@firemanagement.com or create an issue in the repository.

## Acknowledgments

- Materio UI Template for the beautiful interface
- Django community for the excellent framework
- All contributors who have helped shape this project

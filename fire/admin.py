from django.contrib import admin

from .models import Incident, Locations, Firefighters, FireStation, FireTruck, WeatherConditions

@admin.register(WeatherConditions)
class WeatherConditionsAdmin(admin.ModelAdmin):
    list_display = ('incident', 'temperature', 'humidity', 'wind_speed', 'weather_description', 'created_at')
    list_filter = ('created_at', 'weather_description')
    search_fields = ('weather_description', 'incident__description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Incident Information', {
            'fields': ('incident',)
        }),
        ('Weather Data', {
            'fields': ('temperature', 'humidity', 'wind_speed', 'weather_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Ensure decimal values are properly formatted
        if obj.temperature:
            obj.temperature = round(float(obj.temperature), 2)
        if obj.humidity:
            obj.humidity = round(float(obj.humidity), 2)
        if obj.wind_speed:
            obj.wind_speed = round(float(obj.wind_speed), 2)
        super().save_model(request, obj, form, change)

admin.site.register(Incident)
admin.site.register(Locations)
admin.site.register(Firefighters)
admin.site.register(FireStation)
admin.site.register(FireTruck)

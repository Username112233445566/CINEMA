from django.contrib import admin
from .models import Movie, CinemaHall, Screening, Seat, Booking

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration']
    search_fields = ['title']

@admin.register(CinemaHall)
class CinemaHallAdmin(admin.ModelAdmin):
    list_display = ['name', 'rows', 'seats_per_row', 'total_seats']

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ['movie', 'hall', 'start_time', 'end_time', 'price']
    list_filter = ['start_time', 'hall']
    date_hierarchy = 'start_time'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['hall', 'row', 'number']
    list_filter = ['hall']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'screening', 'seat', 'booked_at']
    list_filter = ['screening', 'booked_at']
    search_fields = ['user__username']
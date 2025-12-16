from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('screenings/', views.screening_list, name='screening_list'),
    path('screenings/<int:movie_id>/', views.screening_list, name='screening_list_by_movie'),
    path('screening/<int:screening_id>/seats/', views.seat_selection, name='seat_selection'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('register/', views.register, name='register'),
]
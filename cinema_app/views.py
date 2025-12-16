from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Movie, Screening, CinemaHall, Seat, Booking
from .forms import BookingForm

def home(request):
    today = timezone.now().date()
    screenings = Screening.objects.filter(
        start_time__date=today, 
        start_time__gte=timezone.now()
    ).select_related('movie', 'hall')
    return render(request, 'cinema_app/home.html', {
        'screenings': screenings,
        'today': today
    })

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'cinema_app/movie_list.html', {'movies': movies})

def screening_list(request, movie_id=None):
    screenings = Screening.objects.filter(start_time__gte=timezone.now())
    
    if movie_id:
        screenings = screenings.filter(movie_id=movie_id)
    
    screenings = screenings.select_related('movie', 'hall').order_by('start_time')
    
    paginator = Paginator(screenings, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cinema_app/screening_list.html', {
        'screenings': page_obj,
        'page_obj': page_obj
    })

@login_required
def seat_selection(request, screening_id):
    screening = get_object_or_404(Screening, id=screening_id)
    hall = screening.hall
    
    if screening.start_time <= timezone.now():
        messages.error(request, 'Этот сеанс уже начался или завершился!')
        return redirect('screening_list')
    
    booked_seats = Booking.objects.filter(screening=screening).values_list('seat_id', flat=True)
    
    seats = Seat.objects.filter(hall=hall).order_by('row', 'number')
    
    seats_matrix = []
    current_row = None
    row_seats = []
    
    for seat in seats:
        if seat.row != current_row:
            if current_row is not None:
                seats_matrix.append(row_seats)
            current_row = seat.row
            row_seats = []
        
        is_booked = seat.id in booked_seats
        row_seats.append({
            'seat': seat,
            'is_booked': is_booked
        })
    
    if row_seats:
        seats_matrix.append(row_seats)
    
    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        if seat_id:
            try:
                seat = Seat.objects.get(id=seat_id, hall=hall)
                
                if Booking.objects.filter(screening=screening, seat=seat).exists():
                    messages.error(request, 'Это место уже забронировано!')
                    return redirect('seat_selection', screening_id=screening_id)
                
                Booking.objects.create(
                    user=request.user,
                    screening=screening,
                    seat=seat
                )
                messages.success(request, f'Место {seat} успешно забронировано!')
                return redirect('booking_list')
                
            except Seat.DoesNotExist:
                messages.error(request, 'Выбранное место не существует!')
                return redirect('seat_selection', screening_id=screening_id)
    
    return render(request, 'cinema_app/seat_selection.html', {
        'screening': screening,
        'hall': hall,
        'seats_matrix': seats_matrix
    })

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related('screening', 'seat', 'screening__movie', 'screening__hall').order_by('-booked_at')
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cinema_app/booking_list.html', {
        'bookings': page_obj,
        'page_obj': page_obj
    })

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.screening.start_time <= timezone.now():
        messages.error(request, 'Нельзя отменить бронирование на начавшийся сеанс!')
        return redirect('booking_list')
    
    if request.method == 'POST':
        movie_title = booking.screening.movie.title
        booking.delete()
        messages.success(request, f'Бронирование на фильм "{movie_title}" отменено!')
        return redirect('booking_list')
    
    return render(request, 'cinema_app/cancel_confirm.html', {'booking': booking})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
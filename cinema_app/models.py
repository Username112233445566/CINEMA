from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Длительность в минутах")
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    
    def __str__(self):
        return self.title

class CinemaHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    seats_per_row = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    
    def total_seats(self):
        return self.rows * self.seats_per_row
    
    def __str__(self):
        return f"{self.name} ({self.rows}x{self.seats_per_row})"

class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"

class Seat(models.Model):
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    row = models.IntegerField()
    number = models.IntegerField()
    
    class Meta:
        unique_together = ['hall', 'row', 'number']
    
    def __str__(self):
        return f"Ряд {self.row}, Место {self.number}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['screening', 'seat']
    
    def __str__(self):
        return f"{self.user.username} - {self.screening} - {self.seat}"
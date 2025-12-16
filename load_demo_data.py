import os
import django
import requests
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
import time
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cinema_app.models import Movie, CinemaHall, Screening, Seat, Booking
from django.core.files import File

def download_poster(movie_title, movie_id):
    try:
        safe_title = "".join(c if c.isalnum() else "_" for c in movie_title[:50])
        filename = f"{movie_id}_{safe_title}.jpg"
        
        media_root = Path('media/posters/')
        media_root.mkdir(parents=True, exist_ok=True)
        filepath = media_root / filename
        
        seed_value = hash(movie_title) % 1000
        image_url = f"https://picsum.photos/seed/{seed_value}/300/450"
        
        fallback_urls = [
            "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&h=450&fit=crop",
            "https://images.unsplash.com/photo-1489599809516-9827b6d1cf13?w=300&h=450&fit=crop",
            "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=300&h=450&fit=crop",
            "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=300&h=450&fit=crop",
        ]
        
        try:
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
        except:
            fallback_url = random.choice(fallback_urls)
            response = requests.get(fallback_url, timeout=5)
            response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"    ✓ Загружено изображение для '{movie_title}'")
        return filepath
    except Exception as e:
        print(f"    ✗ Не удалось загрузить изображение для '{movie_title}': {str(e)[:100]}")
        return None

def create_demo_data():
    print("Очистка старых данных...")
    Screening.objects.all().delete()
    Seat.objects.all().delete()
    CinemaHall.objects.all().delete()
    Movie.objects.all().delete()

    print("\n1. Создание фильмов и загрузка постеров...")
    movies_data = [
        {
            'title': 'Аватар: Путь воды',
            'description': 'Продолжение эпической саги Джеймса Кэмерона о мире Пандоры.',
            'duration': 192,
            'genre': 'Фантастика'
        },
        {
            'title': 'Оппенгеймер',
            'description': 'История создания атомной бомбы режиссера Кристофера Нолана.',
            'duration': 180,
            'genre': 'Биография'
        },
        {
            'title': 'Барби',
            'description': 'Комедийный фильм о знаменитой кукле Барби.',
            'duration': 114,
            'genre': 'Комедия'
        },
        {
            'title': 'Дюна: Часть вторая',
            'description': 'Продолжение эпической фантастической саги по романам Фрэнка Герберта.',
            'duration': 166,
            'genre': 'Фантастика'
        },
        {
            'title': 'Джон Уик 4',
            'description': 'Четвертая часть боевика о наемном убийце Джоне Уике.',
            'duration': 169,
            'genre': 'Боевик'
        },
        {
            'title': 'Стражи Галактики: Часть 3',
            'description': 'Завершающая часть трилогии о команде супергероев из космоса.',
            'duration': 150,
            'genre': 'Фантастика'
        },
        {
            'title': 'Миссия невыполнима: Смертельная расплата',
            'description': 'Новая миссия Итана Ханта и команды IMF.',
            'duration': 163,
            'genre': 'Боевик'
        },
        {
            'title': 'Человек-паук: Паутина вселенных',
            'description': 'Мультфильм о мультивселенной Человека-паука.',
            'duration': 140,
            'genre': 'Мультфильм'
        },
        {
            'title': 'Трансформеры: Эпоха зверей',
            'description': 'Новая глава в истории трансформеров.',
            'duration': 127,
            'genre': 'Фантастика'
        },
        {
            'title': 'Элементарно',
            'description': 'Анимационный фильм о жителях элементах в большом городе.',
            'duration': 102,
            'genre': 'Мультфильм'
        },
        {
            'title': 'Индиана Джонс и колесо судьбы',
            'description': 'Новое приключение легендарного археолога.',
            'duration': 154,
            'genre': 'Приключения'
        },
        {
            'title': 'Флэш',
            'description': 'Фильм о самом быстром человеке на Земле.',
            'duration': 144,
            'genre': 'Фантастика'
        },
        {
            'title': 'Русалочка',
            'description': 'Экранизация классической сказки Диснея.',
            'duration': 135,
            'genre': 'Фэнтези'
        },
        {
            'title': 'Код 355',
            'description': 'Шпионский боевик о группе женщин-агентов.',
            'duration': 122,
            'genre': 'Боевик'
        },
        {
            'title': 'Не дыши 3',
            'description': 'Триллер о слепом ветеринаре и его дочери.',
            'duration': 98,
            'genre': 'Ужасы'
        },
    ]

    movie_objects = []
    for idx, data in enumerate(movies_data):
        movie = Movie.objects.create(
            title=data['title'],
            description=data['description'],
            duration=data['duration']
        )
        
        time.sleep(0.5)
        poster_path = download_poster(data['title'], movie.id)
        
        if poster_path:
            try:
                with open(poster_path, 'rb') as img_file:
                    movie.poster.save(os.path.basename(poster_path), File(img_file), save=True)
            except Exception as e:
                print(f"    ⚠ Ошибка сохранения постера: {e}")
        
        movie_objects.append(movie)
        print(f"  Создан фильм: {data['title']} ({data['genre']})")

    print("\n2. Создание кинозалов и мест...")
    halls_data = [
        {'name': 'Красный зал (IMAX)', 'rows': 12, 'seats_per_row': 16},
        {'name': 'Синий зал (3D)', 'rows': 10, 'seats_per_row': 14},
        {'name': 'Зеленый зал (VIP)', 'rows': 8, 'seats_per_row': 10},
        {'name': 'Желтый зал (Комфорт)', 'rows': 9, 'seats_per_row': 13},
        {'name': 'Фиолетовый зал (Детский)', 'rows': 7, 'seats_per_row': 12},
        {'name': 'Оранжевый зал (Стандарт)', 'rows': 11, 'seats_per_row': 15},
    ]
    
    hall_objects = []
    for hall_data in halls_data:
        hall = CinemaHall.objects.create(**hall_data)
        hall_objects.append(hall)
        
        seats_created = 0
        for row in range(1, hall.rows + 1):
            for seat_num in range(1, hall.seats_per_row + 1):
                Seat.objects.create(hall=hall, row=row, number=seat_num)
                seats_created += 1
        
        print(f"  Создан зал: {hall.name}, мест: {seats_created}")

    print("\n3. Создание сеансов на ближайшие 10 дней...")
    now = timezone.now()
    screenings_created = 0
    
    daily_slots = [
        {'hour': 9, 'minute': 30, 'price': 250, 'type': 'Утренний'},
        {'hour': 12, 'minute': 0, 'price': 350, 'type': 'Дневной'},
        {'hour': 15, 'minute': 0, 'price': 450, 'type': 'Дневной'},
        {'hour': 18, 'minute': 0, 'price': 550, 'type': 'Вечерний'},
        {'hour': 21, 'minute': 0, 'price': 600, 'type': 'Вечерний'},
    ]
    
    for day_offset in range(10):
        current_date = now + timedelta(days=day_offset)
        
        is_weekend = current_date.weekday() >= 5
        weekend_slots = daily_slots + [{'hour': 23, 'minute': 30, 'price': 500, 'type': 'Ночной'}] if is_weekend else daily_slots
        
        for slot in weekend_slots:
            for hall_idx, hall in enumerate(hall_objects):
                movie_idx = (day_offset * len(hall_objects) + hall_idx) % len(movie_objects)
                movie = movie_objects[movie_idx]
                
                start_time = current_date.replace(
                    hour=slot['hour'], 
                    minute=slot['minute'], 
                    second=0, 
                    microsecond=0
                )
                
                end_time = start_time + timedelta(minutes=movie.duration + 25)
                
                price_multiplier = 1.0
                if 'VIP' in hall.name:
                    price_multiplier = 1.5
                elif 'IMAX' in hall.name or '3D' in hall.name:
                    price_multiplier = 1.3
                elif 'Комфорт' in hall.name:
                    price_multiplier = 1.2
                
                final_price = int(slot['price'] * price_multiplier)
                
                Screening.objects.create(
                    movie=movie,
                    hall=hall,
                    start_time=start_time,
                    end_time=end_time,
                    price=final_price
                )
                screenings_created += 1
    
    print(f"\n{'='*50}")
    print("✅ ДЕМО-ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print(f"{'='*50}")
    print(f"   🎬 Фильмов: {len(movie_objects)}")
    print(f"   🏛️  Залов: {len(hall_objects)}")
    print(f"   💺 Общее количество мест: {sum(h.total_seats() for h in hall_objects)}")
    print(f"   🎟️  Сеансов создано: {screenings_created}")
    print(f"   📅 Расписание: на {10} дней вперед")
    print(f"   📁 Изображения сохранены в: media/posters/")
    print(f"{'='*50}")
    
    print("\n4. Создание тестовых бронирований...")
    from django.contrib.auth.models import User
    
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'password': 'testpass123'}
    )
    
    upcoming_screenings = Screening.objects.filter(start_time__gte=now).order_by('start_time')[:10]
    
    bookings_created = 0
    for screening in upcoming_screenings:
        booked_seats = Booking.objects.filter(screening=screening).values_list('seat_id', flat=True)
        available_seats = Seat.objects.filter(hall=screening.hall).exclude(id__in=booked_seats)[:5]
        
        for seat in available_seats:
            Booking.objects.create(
                user=test_user,
                screening=screening,
                seat=seat
            )
            bookings_created += 1
    
    print(f"   ✅ Создано тестовых бронирований: {bookings_created}")
    print(f"\n🔑 Тестовый пользователь: {test_user.username}")
    print(f"   Пароль: testpass123")

if __name__ == '__main__':
    create_demo_data()
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Meal
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create a verified seller
        seller, created = User.objects.get_or_create(
            username='chef_maria',
            defaults={
                'email': 'maria@example.com',
                'first_name': 'Maria',
                'last_name': 'Garcia'
            }
        )
        if created:
            seller.set_password('password123')
            seller.save()
            self.stdout.write(self.style.SUCCESS(f'Created seller: {seller.username}'))
        
        # Create or update profile
        profile, _ = UserProfile.objects.get_or_create(user=seller)
        profile.is_verified_seller = True
        profile.phone_number = '555-0123'
        profile.save()
        
        # Create sample meals with different locations around NYC (example coordinates)
        sample_meals = [
            {
                'title': 'Homemade Chicken Tikka Masala',
                'description': 'Authentic Indian curry with tender chicken pieces in a creamy tomato sauce. Served with basmati rice and naan bread.',
                'ingredients': 'Chicken, tomatoes, cream, garam masala, ginger, garlic, rice, naan',
                'price': Decimal('12.99'),
                'pickup_location': 'Student Center, Main Lobby',
                'pickup_latitude': 40.7128,
                'pickup_longitude': -74.0060,
            },
            {
                'title': 'Vegetarian Pad Thai',
                'description': 'Classic Thai noodle dish with tofu, bean sprouts, peanuts, and tangy tamarind sauce.',
                'ingredients': 'Rice noodles, tofu, bean sprouts, peanuts, eggs, tamarind, lime',
                'price': Decimal('10.50'),
                'pickup_location': 'Library, 1st Floor Cafe',
                'pickup_latitude': 40.7150,
                'pickup_longitude': -74.0080,
            },
            {
                'title': 'Italian Lasagna',
                'description': 'Layers of pasta, rich meat sauce, ricotta, and mozzarella cheese. Baked to perfection!',
                'ingredients': 'Pasta, ground beef, tomato sauce, ricotta, mozzarella, parmesan',
                'price': Decimal('14.00'),
                'pickup_location': 'Engineering Building, Room 101',
                'pickup_latitude': 40.7100,
                'pickup_longitude': -74.0040,
            },
            {
                'title': 'Fresh Greek Salad Bowl',
                'description': 'Crisp vegetables with feta cheese, olives, and homemade Greek dressing.',
                'ingredients': 'Lettuce, tomatoes, cucumber, feta cheese, olives, red onion, olive oil',
                'price': Decimal('8.99'),
                'pickup_location': 'Gym Building, Front Desk',
                'pickup_latitude': 40.7140,
                'pickup_longitude': -74.0020,
            },
            {
                'title': 'Korean Bibimbap',
                'description': 'Mixed rice bowl with seasoned vegetables, beef, fried egg, and spicy gochujang sauce.',
                'ingredients': 'Rice, beef, carrots, spinach, mushrooms, egg, gochujang, sesame oil',
                'price': Decimal('13.50'),
                'pickup_location': 'Arts Building, Main Entrance',
                'pickup_latitude': 40.7160,
                'pickup_longitude': -74.0070,
            },
        ]
        
        for meal_data in sample_meals:
            meal, created = Meal.objects.get_or_create(
                seller=seller,
                title=meal_data['title'],
                defaults=meal_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created meal: {meal.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Meal already exists: {meal.title}'))
        
        # Create a buyer account
        buyer, created = User.objects.get_or_create(
            username='student_john',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith'
            }
        )
        if created:
            buyer.set_password('password123')
            buyer.save()
            UserProfile.objects.get_or_create(user=buyer)
            self.stdout.write(self.style.SUCCESS(f'Created buyer: {buyer.username}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Created Successfully ==='))
        self.stdout.write(self.style.SUCCESS(f'Seller login: chef_maria / password123'))
        self.stdout.write(self.style.SUCCESS(f'Buyer login: student_john / password123'))

from django.core.management.base import BaseCommand
from accounts.models import Meal


class Command(BaseCommand):
    help = 'Updates existing sample meals with dietary tags for testing filters'

    def handle(self, *args, **kwargs):
        # Update meals with appropriate dietary tags
        meal_updates = {
            'Homemade Chicken Tikka Masala': 'halal',
            'Vegetarian Pad Thai': 'vegetarian',
            'Italian Lasagna': 'none',
            'Fresh Greek Salad Bowl': 'vegetarian',
            'Korean Bibimbap': 'none',
        }
        
        updated_count = 0
        for title, dietary_tag in meal_updates.items():
            meals = Meal.objects.filter(title=title)
            if meals.exists():
                meals.update(dietary_tags=dietary_tag)
                updated_count += meals.count()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated "{title}" to {dietary_tag}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Updated {updated_count} meal(s) with dietary tags')
        )

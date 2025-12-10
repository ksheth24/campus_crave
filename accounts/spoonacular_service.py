"""
Spoonacular API service for fetching nutrition information.

This module provides functions to interact with the Spoonacular API
to analyze ingredients and retrieve nutrition data, allergens, and dietary tags.
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SpoonacularService:
    """Service class for interacting with Spoonacular API."""
    
    def __init__(self):
        self.api_key = settings.SPOONACULAR_API_KEY
        self.base_url = settings.SPOONACULAR_API_BASE_URL
        
    def is_configured(self):
        """Check if API key is configured."""
        return bool(self.api_key)
    
    def analyze_ingredients(self, ingredients_text, servings=1):
        """
        Analyze ingredients text and return nutrition information.
        
        Args:
            ingredients_text (str): Comma-separated list of ingredients
            servings (int): Number of servings (default: 1)
            
        Returns:
            dict: Nutrition data including calories, allergens, and dietary info
                  Returns None if API call fails or is not configured
        """
        if not self.is_configured():
            logger.warning("Spoonacular API key not configured")
            return None
        
        try:
            # Parse ingredients into a list
            ingredient_list = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
            
            if not ingredient_list:
                logger.warning("No ingredients provided")
                return None
            
            # Call Spoonacular API to analyze ingredients
            url = f"{self.base_url}/recipes/parseIngredients"
            
            nutrition_data = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'allergens': [],
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'is_dairy_free': True,
            }
            
            # Analyze each ingredient
            for ingredient in ingredient_list:
                params = {
                    'ingredientList': ingredient,
                    'servings': servings,
                    'includeNutrition': 'true',
                    'apiKey': self.api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        ing_data = data[0]
                        
                        # Extract nutrition information
                        if 'nutrition' in ing_data:
                            nutrients = ing_data['nutrition'].get('nutrients', [])
                            for nutrient in nutrients:
                                name = nutrient.get('name', '').lower()
                                amount = nutrient.get('amount', 0)
                                
                                if 'calorie' in name:
                                    nutrition_data['calories'] += amount
                                elif 'protein' in name:
                                    nutrition_data['protein'] += amount
                                elif 'carbohydrate' in name:
                                    nutrition_data['carbs'] += amount
                                elif 'fat' in name and 'saturated' not in name:
                                    nutrition_data['fat'] += amount
                        
                        # Check dietary properties
                        if 'meta' in ing_data:
                            meta = ing_data.get('meta', [])
                            meta_lower = [m.lower() for m in meta]
                            
                            # Check for non-vegetarian/vegan items
                            non_veg_keywords = ['meat', 'chicken', 'beef', 'pork', 'fish', 'seafood', 'poultry']
                            if any(keyword in ing_data.get('name', '').lower() for keyword in non_veg_keywords):
                                nutrition_data['is_vegetarian'] = False
                                nutrition_data['is_vegan'] = False
                            
                            # Check for dairy
                            dairy_keywords = ['dairy', 'milk', 'cheese', 'butter', 'cream', 'yogurt']
                            if any(keyword in ing_data.get('name', '').lower() for keyword in dairy_keywords):
                                nutrition_data['is_dairy_free'] = False
                                nutrition_data['is_vegan'] = False
                            
                            # Check for eggs
                            if 'egg' in ing_data.get('name', '').lower():
                                nutrition_data['is_vegan'] = False
                            
                            # Check for gluten
                            gluten_keywords = ['wheat', 'flour', 'bread', 'pasta', 'barley', 'rye']
                            if any(keyword in ing_data.get('name', '').lower() for keyword in gluten_keywords):
                                nutrition_data['is_gluten_free'] = False
                        
                        # Extract allergens
                        allergens = self._extract_allergens(ing_data)
                        nutrition_data['allergens'].extend(allergens)
                
                elif response.status_code == 402:
                    logger.error("Spoonacular API quota exceeded")
                    return None
                else:
                    logger.warning(f"Spoonacular API returned status {response.status_code}")
            
            # Remove duplicate allergens
            nutrition_data['allergens'] = list(set(nutrition_data['allergens']))
            
            # Round nutrition values
            nutrition_data['calories'] = round(nutrition_data['calories'])
            nutrition_data['protein'] = round(nutrition_data['protein'], 1)
            nutrition_data['carbs'] = round(nutrition_data['carbs'], 1)
            nutrition_data['fat'] = round(nutrition_data['fat'], 1)
            
            return nutrition_data
            
        except requests.exceptions.Timeout:
            logger.error("Spoonacular API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Spoonacular API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing ingredients: {str(e)}")
            return None
    
    def _extract_allergens(self, ingredient_data):
        """
        Extract common allergens from ingredient data.
        
        Args:
            ingredient_data (dict): Parsed ingredient data from API
            
        Returns:
            list: List of allergen names
        """
        allergens = []
        ingredient_name = ingredient_data.get('name', '').lower()
        
        # Common allergen mapping
        allergen_keywords = {
            'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'whey', 'casein'],
            'eggs': ['egg'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'halibut'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'clam', 'oyster', 'mussel'],
            'tree nuts': ['almond', 'walnut', 'cashew', 'pecan', 'pistachio', 'hazelnut'],
            'peanuts': ['peanut'],
            'wheat': ['wheat', 'flour'],
            'soy': ['soy', 'tofu', 'edamame'],
        }
        
        for allergen, keywords in allergen_keywords.items():
            if any(keyword in ingredient_name for keyword in keywords):
                allergens.append(allergen)
        
        return allergens
    
    def suggest_dietary_tag(self, nutrition_data):
        """
        Suggest the most appropriate dietary tag based on nutrition data.
        
        Args:
            nutrition_data (dict): Nutrition data from analyze_ingredients
            
        Returns:
            str: Suggested dietary tag (matches Meal.DIETARY_CHOICES)
        """
        if not nutrition_data:
            return 'none'
        
        # Priority order for dietary tags
        if nutrition_data.get('is_vegan', False):
            return 'vegan'
        elif nutrition_data.get('is_vegetarian', False):
            return 'vegetarian'
        elif nutrition_data.get('is_gluten_free', False) and nutrition_data.get('is_dairy_free', False):
            return 'gluten_free'
        elif nutrition_data.get('is_dairy_free', False):
            return 'dairy_free'
        elif nutrition_data.get('is_gluten_free', False):
            return 'gluten_free'
        
        return 'none'


# Singleton instance
spoonacular_service = SpoonacularService()

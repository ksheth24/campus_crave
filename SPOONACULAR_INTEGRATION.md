# Spoonacular API Integration

## User Story
**As a seller, I want the Spoonacular API to automatically generate nutrition information (calories, allergens, dietary tags) based on my ingredients so that I can enrich my listing details.**

## Overview
This feature integrates the Spoonacular Food API to automatically analyze meal ingredients and generate comprehensive nutrition information including calories, macronutrients, allergens, and dietary classifications.

## Features Implemented

### 1. **Automatic Nutrition Analysis**
- ✅ Calories per serving
- ✅ Protein (grams)
- ✅ Carbohydrates (grams)
- ✅ Fat (grams)
- ✅ Allergen detection (dairy, eggs, nuts, gluten, etc.)
- ✅ Dietary tag suggestions (vegan, vegetarian, gluten-free, etc.)

### 2. **Smart Dietary Tag Auto-Suggestion**
The system automatically suggests the most appropriate dietary tag based on ingredients:
- **Vegan**: No animal products detected
- **Vegetarian**: No meat/fish but may contain dairy/eggs
- **Gluten-Free**: No wheat, barley, or rye detected
- **Dairy-Free**: No milk products detected
- Sellers can override auto-suggestions if needed

### 3. **Allergen Detection**
Automatically identifies common allergens:
- Dairy (milk, cheese, butter, cream)
- Eggs
- Fish
- Shellfish
- Tree nuts
- Peanuts
- Wheat/Gluten
- Soy

## How It Works

### For Sellers

#### Creating a New Meal
1. Navigate to "Create Meal Listing"
2. Fill in meal details including **ingredients** (comma-separated list)
3. Submit the form
4. **Automatic API Call**: System sends ingredients to Spoonacular API
5. **Nutrition Data Generated**: Calories, macros, and allergens are automatically populated
6. **Dietary Tag Suggested**: If you haven't selected a dietary tag, one is auto-suggested
7. Success message confirms nutrition info was generated

#### Editing an Existing Meal
1. Edit your meal listing
2. If you **change the ingredients**, the system automatically:
   - Re-analyzes the new ingredients
   - Updates nutrition information
   - Re-suggests dietary tags if set to "No Restrictions"
3. If ingredients unchanged, nutrition data remains the same

### For Buyers

#### Viewing Nutrition Information
- **Browse Page**: See calorie count on meal cards
- **Meal Detail Page**: View comprehensive nutrition panel with:
  - Calories (large, prominent display)
  - Protein, Carbs, Fat (in grams)
  - Allergen warnings (highlighted in orange)
  - API generation status message

## Technical Implementation

### 1. New Model Fields (Meal)
```python
calories = IntegerField(null=True, blank=True)
protein = DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
carbs = DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
fat = DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
allergens = TextField(blank=True)
nutrition_info = TextField(blank=True)  # Status message
```

### 2. Spoonacular Service Module
**File**: `accounts/spoonacular_service.py`

Key functions:
- `analyze_ingredients(ingredients_text, servings)`: Main API call
- `suggest_dietary_tag(nutrition_data)`: Auto-suggest dietary classification
- `_extract_allergens(ingredient_data)`: Identify allergens

### 3. API Configuration
**File**: `campuscrave/settings.py`

```python
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', '')
SPOONACULAR_API_BASE_URL = 'https://api.spoonacular.com'
```

### 4. View Integration
**File**: `accounts/views.py`

- `create_meal`: Calls API when creating new meals
- `edit_meal`: Re-calls API if ingredients change

### 5. Template Updates
- `meal_detail.html`: Comprehensive nutrition panel
- `browse_meals.html`: Calorie display on cards

## Setup Instructions

### 1. Get Spoonacular API Key
1. Visit: https://spoonacular.com/food-api/console#Dashboard
2. Sign up for a free account
3. Get your API key (free tier: 150 requests/day)

### 2. Configure API Key

**Option A: .env File (Recommended for Development)**
1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
SPOONACULAR_API_KEY=your_api_key_here
```

3. Restart the Django server to load the new configuration

**Option B: Environment Variable (Production)**
```bash
export SPOONACULAR_API_KEY='your_api_key_here'
python manage.py runserver
```

⚠️ **Never commit `.env` or API keys to version control!**
⚠️ **Make sure `.env` is in your `.gitignore` file**

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Test the Feature
1. Login as a verified seller (e.g., `chef_maria`)
2. Create a new meal with ingredients like: "chicken breast, rice, broccoli, olive oil"
3. Submit and check the nutrition information!

## API Behavior

### When API is Configured
- ✅ Automatic nutrition analysis on meal creation
- ✅ Automatic re-analysis when ingredients change
- ✅ Success messages with confirmation
- ✅ Dietary tag auto-suggestions

### When API is NOT Configured
- ⚠️ Meals can still be created normally
- ⚠️ Nutrition fields remain empty
- ⚠️ Info message: "Configure Spoonacular API for auto nutrition info"
- ⚠️ No dietary tag auto-suggestions

### When API Quota Exceeded
- ⚠️ Meal is created but nutrition info not populated
- ⚠️ Warning message: "Meal created, but nutrition info could not be generated"
- ⚠️ Status saved: "Nutrition info could not be generated (API limit or error)"

## Example Ingredient Lists

### Good Examples
```
chicken breast, rice, broccoli, olive oil
pasta, tomato sauce, mozzarella cheese, basil
tofu, soy sauce, vegetables, sesame oil
salmon, quinoa, asparagus, lemon
```

### Tips for Best Results
- ✅ Use common ingredient names
- ✅ Separate with commas
- ✅ Be specific (e.g., "chicken breast" not just "chicken")
- ✅ Include main ingredients only
- ❌ Avoid very long lists (API processes each ingredient)
- ❌ Avoid vague terms like "spices" or "seasonings"

## API Limits & Costs

### Free Tier
- **150 requests/day**
- **1 request per second**
- Perfect for development and small-scale use

### Paid Tiers
- More requests per day
- Higher rate limits
- See: https://spoonacular.com/food-api/pricing

### Optimization Tips
1. **Cache results**: Nutrition data is saved in database
2. **Only re-analyze on ingredient changes**: Not on every edit
3. **Batch testing**: Test with a few meals first
4. **Monitor usage**: Check your dashboard regularly

## Files Modified/Created

### Created
1. `accounts/spoonacular_service.py` - API service module
2. `accounts/migrations/0009_meal_allergens_meal_calories_meal_carbs_meal_fat_and_more.py` - Database migration
3. `SPOONACULAR_INTEGRATION.md` - This documentation

### Modified
1. `requirements.txt` - Added `requests>=2.31.0`
2. `campuscrave/settings.py` - Added API configuration
3. `accounts/models.py` - Added nutrition fields to Meal model
4. `accounts/views.py` - Integrated API calls in create/edit views
5. `templates/accounts/meal_detail.html` - Added nutrition display panel
6. `templates/accounts/browse_meals.html` - Added calorie display to cards

## Benefits

### For Sellers
- ⏱️ **Save Time**: No manual nutrition calculation
- 📊 **Professional Listings**: Comprehensive nutrition data
- 🎯 **Better Targeting**: Auto-suggested dietary tags help reach right buyers
- ✅ **Accuracy**: API-powered data more reliable than manual entry

### For Buyers
- 🔍 **Informed Decisions**: See nutrition before ordering
- ⚠️ **Safety**: Clear allergen warnings
- 🥗 **Dietary Needs**: Easy to find meals matching dietary restrictions
- 💪 **Health Goals**: Track calories and macros

### For Platform
- 🚀 **Competitive Advantage**: Professional nutrition data
- 📈 **Increased Trust**: Transparent, verified information
- 🎨 **Better UX**: Rich, detailed meal listings
- 🔄 **Automation**: Less manual data entry

## Troubleshooting

### Issue: "Nutrition info could not be generated"
**Causes:**
- API key not configured
- API quota exceeded
- Network/timeout issues
- Invalid ingredient format

**Solutions:**
1. Check API key is set correctly
2. Verify API quota on Spoonacular dashboard
3. Check ingredient format (comma-separated)
4. Try again later if quota exceeded

### Issue: Inaccurate nutrition data
**Causes:**
- Vague ingredient names
- Non-standard ingredient terms
- Complex recipes

**Solutions:**
1. Use common, specific ingredient names
2. List main ingredients only
3. Manually adjust dietary tags if needed

### Issue: API calls too slow
**Causes:**
- Multiple ingredients = multiple API calls
- Network latency

**Solutions:**
1. Keep ingredient lists concise
2. Results are cached after first generation
3. Consider upgrading API tier for faster limits

## Future Enhancements

### Potential Improvements
- [ ] Batch ingredient analysis (single API call)
- [ ] Serving size adjustments
- [ ] Micronutrient data (vitamins, minerals)
- [ ] Recipe scaling based on servings
- [ ] Nutrition label image generation
- [ ] Integration with other nutrition APIs (USDA, Edamam)
- [ ] Manual nutrition override option
- [ ] Nutrition comparison between meals
- [ ] Dietary goal tracking for buyers

## Security & Privacy

### Best Practices
- ✅ API key stored in environment variables
- ✅ Never commit keys to version control
- ✅ Use `.env` files (add to `.gitignore`)
- ✅ Rotate API keys periodically
- ✅ Monitor API usage for anomalies

### Data Privacy
- Ingredient data sent to Spoonacular API
- No personal user data transmitted
- Nutrition results stored in local database
- Complies with Spoonacular Terms of Service

## Support & Resources

### Spoonacular Documentation
- API Docs: https://spoonacular.com/food-api/docs
- Console: https://spoonacular.com/food-api/console
- Pricing: https://spoonacular.com/food-api/pricing

### CampusCrave Support
- Check application logs for API errors
- Review `accounts/spoonacular_service.py` for implementation details
- Test with sample ingredients before production use

---

**Implementation Date**: December 10, 2025
**Status**: ✅ Fully Implemented and Tested
**API Version**: Spoonacular Food API v1

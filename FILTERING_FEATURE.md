# Meal Filtering Feature Implementation

## User Story
**As a buyer, I want to filter meals by dietary preference (e.g., vegetarian, gluten-free) or price range so that I can easily find food that meets my needs.**

## Implementation Summary

### 1. Database Changes
- **Added `dietary_tags` field to Meal model** with the following options:
  - Vegetarian
  - Vegan
  - Gluten-Free
  - Dairy-Free
  - Halal
  - Kosher
  - Nut-Free
  - No Restrictions (default)
- **Migration created and applied**: `0007_meal_dietary_tags.py`

### 2. Form Updates

#### MealForm (for sellers)
- Added `dietary_tags` field to allow sellers to specify dietary category when creating/editing meals
- Field appears in create and edit meal forms

#### MealFilterForm (new - for buyers)
- Created new form with three filter fields:
  - **Dietary Preference**: Dropdown with all dietary options
  - **Min Price**: Decimal input for minimum price
  - **Max Price**: Decimal input for maximum price
- Includes validation to ensure min price ≤ max price

### 3. View Updates

#### browse_meals view
- Accepts GET parameters for filtering
- Applies filters to meal queryset:
  - Filters by dietary_tags if specified
  - Filters by price range (min/max) if specified
- Passes filter form and filtered meals to template

#### meals_api endpoint
- Updated to accept same filter parameters as browse_meals
- Returns filtered meals as JSON for map markers
- Includes dietary_tags in meal data response

### 4. Template Updates

#### browse_meals.html
- **Added filter section** with:
  - Clean, responsive filter form UI
  - Dietary preference dropdown
  - Min/Max price inputs
  - "Apply Filters" button
  - Results count display
- **Updated JavaScript**:
  - Dynamically loads filtered meals on map
  - Clears and redraws markers when filters change
  - Preserves filter parameters in API calls
- **Updated meal cards**:
  - Display dietary tag badge (if not "No Restrictions")
  - Shows with green color and salad emoji

#### meal_detail.html
- Added dietary category display section
- Shows dietary tag prominently if meal has specific dietary preference

### 5. Admin Updates
- Added `dietary_tags` to MealAdmin list display
- Added `dietary_tags` to admin filter sidebar
- Allows admins to filter meals by dietary preference in admin panel

### 6. Testing & Data
- Created management command `update_meal_dietary_tags.py`
- Updated existing sample meals with appropriate dietary tags:
  - Chicken Tikka Masala → Halal
  - Vegetarian Pad Thai → Vegetarian
  - Fresh Greek Salad Bowl → Vegetarian
  - Italian Lasagna → No Restrictions
  - Korean Bibimbap → No Restrictions

## How to Use

### For Buyers
1. Navigate to `/accounts/meals/browse/`
2. Use the filter section at the top:
   - Select a dietary preference from dropdown
   - Enter min/max price range
   - Click "Apply Filters"
3. View filtered results on both map and list
4. Results count updates automatically

### For Sellers
1. When creating/editing a meal listing
2. Select the appropriate dietary category from dropdown
3. Dietary tag will be displayed on meal cards and detail pages

### Filter Examples
- **Vegetarian meals only**: Select "Vegetarian" from dietary dropdown
- **Budget meals**: Set max price to $10.00
- **Premium vegetarian**: Select "Vegetarian" + set min price to $12.00
- **All gluten-free under $15**: Select "Gluten-Free" + max price $15.00

## Technical Details

### Files Modified
1. `accounts/models.py` - Added dietary_tags field to Meal model
2. `accounts/forms.py` - Updated MealForm, added MealFilterForm
3. `accounts/views.py` - Updated browse_meals and meals_api views
4. `accounts/admin.py` - Added dietary_tags to admin interface
5. `templates/accounts/browse_meals.html` - Added filter UI and updated JavaScript
6. `templates/accounts/meal_detail.html` - Added dietary tag display

### Files Created
1. `accounts/migrations/0007_meal_dietary_tags.py` - Database migration
2. `accounts/management/commands/update_meal_dietary_tags.py` - Data update script

### API Changes
**GET /accounts/api/meals/**
- New query parameters:
  - `dietary_tags`: Filter by dietary preference (e.g., "vegetarian")
  - `min_price`: Minimum price filter (e.g., "5.00")
  - `max_price`: Maximum price filter (e.g., "15.00")
- Response includes `dietary_tags` field for each meal

## Benefits
✅ Buyers can quickly find meals matching their dietary needs
✅ Price filtering helps budget-conscious students
✅ Reduces time spent browsing irrelevant meals
✅ Improves user experience and satisfaction
✅ Sellers can better market their meals to target audiences
✅ Increases likelihood of successful transactions

## Future Enhancements
- Multiple dietary tag selection (e.g., both Vegetarian AND Gluten-Free)
- Save filter preferences per user
- Advanced filters (cuisine type, spice level, portion size)
- Sort by price, rating, or distance
- Filter by pickup time/availability window

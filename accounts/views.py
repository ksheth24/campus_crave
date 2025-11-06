from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .forms import VerificationForm, UserRegistrationForm, MealForm
from .models import Meal, UserProfile, SellerVerificationApplication


def home(request):
    """Simple landing page for CampusCrave."""
    return render(request, 'home.html')


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def verification_apply(request):
    """Allow a seller to apply for verification by submitting ID and agreement."""
    # Check if user already has a verified profile
    try:
        if request.user.profile.is_verified_seller:
            messages.info(request, 'You are already a verified seller!')
            return redirect('accounts:create_meal')
    except UserProfile.DoesNotExist:
        pass
    
    # Check if user has a pending application
    if SellerVerificationApplication.objects.filter(user=request.user, status='pending').exists():
        messages.info(request, 'You already have a pending verification application. Please wait for admin review.')
        return redirect('accounts:my_meals')
    
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your verification application has been submitted. We will review it shortly.')
            return render(request, 'accounts/verification_success.html')
    else:
        form = VerificationForm(user=request.user)
    return render(request, 'accounts/verification_apply.html', {'form': form})


@login_required
def create_meal(request):
    """Create a new meal listing (verified sellers only)."""
    # Check if user is verified seller
    try:
        if not request.user.profile.is_verified_seller:
            messages.error(request, 'You must be a verified seller to create meal listings.')
            return redirect('accounts:verification_apply')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user)
        messages.error(request, 'You must be a verified seller to create meal listings.')
        return redirect('accounts:verification_apply')
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.seller = request.user
            meal.save()
            messages.success(request, 'Meal listing created successfully!')
            return redirect('accounts:my_meals')
    else:
        form = MealForm()
    return render(request, 'accounts/create_meal.html', {'form': form})


@login_required
def my_meals(request):
    """View and manage seller's own meal listings."""
    meals = Meal.objects.filter(seller=request.user)
    return render(request, 'accounts/my_meals.html', {'meals': meals})


@login_required
def edit_meal(request, meal_id):
    """Edit an existing meal listing."""
    meal = get_object_or_404(Meal, id=meal_id, seller=request.user)
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meal listing updated successfully!')
            return redirect('accounts:my_meals')
    else:
        form = MealForm(instance=meal)
    return render(request, 'accounts/edit_meal.html', {'form': form, 'meal': meal})


@login_required
def delete_meal(request, meal_id):
    """Delete a meal listing."""
    meal = get_object_or_404(Meal, id=meal_id, seller=request.user)
    if request.method == 'POST':
        meal.delete()
        messages.success(request, 'Meal listing deleted successfully!')
        return redirect('accounts:my_meals')
    return render(request, 'accounts/delete_meal_confirm.html', {'meal': meal})


def browse_meals(request):
    """Browse all available meals on an interactive map."""
    meals = Meal.objects.filter(is_available=True).select_related('seller')
    return render(request, 'accounts/browse_meals.html', {'meals': meals})


def meal_detail(request, meal_id):
    """View details of a specific meal."""
    meal = get_object_or_404(Meal, id=meal_id)
    return render(request, 'accounts/meal_detail.html', {'meal': meal})


def meals_api(request):
    """API endpoint to get all available meals as JSON for map markers."""
    meals = Meal.objects.filter(is_available=True).select_related('seller')
    meals_data = [{
        'id': meal.id,
        'title': meal.title,
        'price': str(meal.price),
        'pickup_location': meal.pickup_location,
        'latitude': meal.pickup_latitude,
        'longitude': meal.pickup_longitude,
        'seller': meal.seller.username,
        'photo_url': meal.photo.url if meal.photo else None,
    } for meal in meals]
    return JsonResponse({'meals': meals_data})

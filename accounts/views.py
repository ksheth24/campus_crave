from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from .forms import VerificationForm, UserRegistrationForm, MealForm, ReservationForm, ReviewForm, MealFilterForm
from .models import Meal, UserProfile, SellerVerificationApplication, Reservation, Review, Message


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


@login_required
def toggle_meal_availability(request, meal_id):
    """Toggle meal availability (mark as sold/available)."""
    meal = get_object_or_404(Meal, id=meal_id, seller=request.user)
    
    if request.method == 'POST':
        meal.is_available = not meal.is_available
        meal.save()
        
        status = "available" if meal.is_available else "sold"
        messages.success(request, f'"{meal.title}" has been marked as {status}.')
        return redirect('accounts:my_meals')
    
    return render(request, 'accounts/toggle_availability_confirm.html', {'meal': meal})


def browse_meals(request):
    """Browse all available meals on an interactive map with filtering."""
    meals = Meal.objects.filter(is_available=True).select_related('seller')
    
    # Apply filters
    filter_form = MealFilterForm(request.GET or None)
    if filter_form.is_valid():
        dietary_tags = filter_form.cleaned_data.get('dietary_tags')
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')
        
        if dietary_tags:
            meals = meals.filter(dietary_tags=dietary_tags)
        if min_price is not None:
            meals = meals.filter(price__gte=min_price)
        if max_price is not None:
            meals = meals.filter(price__lte=max_price)
    
    return render(request, 'accounts/browse_meals.html', {
        'meals': meals,
        'filter_form': filter_form,
    })


def meal_detail(request, meal_id):
    """View details of a specific meal."""
    meal = get_object_or_404(Meal, id=meal_id)
    reviews = meal.reviews.select_related('buyer').all()
    rating_summary = meal.reviews.aggregate(
        average=Avg('rating'),
        count=Count('id')
    )
    return render(request, 'accounts/meal_detail.html', {
        'meal': meal,
        'reviews': reviews,
        'rating_summary': rating_summary,
    })


def meals_api(request):
    """API endpoint to get all available meals as JSON for map markers with filtering."""
    meals = Meal.objects.filter(is_available=True).select_related('seller')
    
    # Apply filters from query parameters
    dietary_tags = request.GET.get('dietary_tags')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if dietary_tags:
        meals = meals.filter(dietary_tags=dietary_tags)
    if min_price:
        try:
            meals = meals.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            meals = meals.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    meals_data = [{
        'id': meal.id,
        'title': meal.title,
        'price': str(meal.price),
        'dietary_tags': meal.get_dietary_tags_display(),
        'nutrition_info': meal.nutrition_info or '',
        'pickup_location': meal.pickup_location,
        'latitude': meal.pickup_latitude,
        'longitude': meal.pickup_longitude,
        'seller': meal.seller.username,
        'photo_url': meal.photo.url if meal.photo else None,
    } for meal in meals]
    return JsonResponse({'meals': meals_data})


@login_required
def create_reservation(request, meal_id):
    """Create a reservation for a meal."""
    meal = get_object_or_404(Meal, id=meal_id)
    
    # Check if meal is available
    if not meal.is_available:
        messages.error(request, 'This meal is currently unavailable.')
        return redirect('accounts:meal_detail', meal_id=meal_id)
    
    # Prevent sellers from ordering their own meals
    if request.user == meal.seller:
        messages.error(request, 'You cannot order your own meal.')
        return redirect('accounts:meal_detail', meal_id=meal_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.meal = meal
            reservation.buyer = request.user
            reservation.save()
            messages.success(request, f'Your order has been placed! Order #{reservation.id}')
            return redirect('accounts:my_orders')
    else:
        form = ReservationForm()
    
    return render(request, 'accounts/create_reservation.html', {
        'form': form,
        'meal': meal,
    })


@login_required
def my_orders(request):
    """View buyer's own orders."""
    orders = Reservation.objects.filter(buyer=request.user).select_related('meal', 'meal__seller', 'review')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def seller_orders(request):
    """View orders for seller's meals."""
    # Check if user is verified seller
    try:
        if not request.user.profile.is_verified_seller:
            messages.error(request, 'You must be a verified seller to view orders.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'You must be a verified seller to view orders.')
        return redirect('home')
    
    # Get all reservations for the seller's meals
    orders = Reservation.objects.filter(meal__seller=request.user).select_related('meal', 'buyer')
    return render(request, 'accounts/seller_orders.html', {'orders': orders})


@login_required
def seller_reviews(request):
    """View all reviews and average rating received by the seller."""
    # Check if user is verified seller
    try:
        if not request.user.profile.is_verified_seller:
            messages.error(request, 'You must be a verified seller to view reviews.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'You must be a verified seller to view reviews.')
        return redirect('home')
    
    # Get all reviews received by this seller
    reviews = Review.objects.filter(seller=request.user).select_related('buyer', 'meal', 'reservation').order_by('-created_at')
    
    # Calculate average rating and total count
    rating_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_count=Count('id')
    )
    
    average_rating = rating_stats['average_rating'] if rating_stats['average_rating'] else 0
    total_reviews = rating_stats['total_count'] or 0
    
    # Calculate rating distribution (for better insights) - convert to list of tuples for template
    rating_distribution = []
    for rating in range(5, 0, -1):  # 5 to 1
        count = reviews.filter(rating=rating).count()
        rating_distribution.append((rating, count))
    
    return render(request, 'accounts/seller_reviews.html', {
        'reviews': reviews,
        'average_rating': round(average_rating, 2) if average_rating else 0,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
    })


@login_required
def leave_review(request, reservation_id):
    """Allow buyers to leave a rating and review after pickup is completed."""
    reservation = get_object_or_404(Reservation, id=reservation_id, buyer=request.user)

    if reservation.status != 'completed':
        messages.error(request, 'You can only leave a review after pickup is completed.')
        return redirect('accounts:my_orders')

    if hasattr(reservation, 'review'):
        messages.info(request, 'You already left feedback for this order.')
        return redirect('accounts:my_orders')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reservation = reservation
            review.meal = reservation.meal
            review.seller = reservation.meal.seller
            review.buyer = request.user
            review.save()
            messages.success(request, 'Thanks for rating your pickup!')
            return redirect('accounts:my_orders')
    else:
        form = ReviewForm()

    return render(request, 'accounts/leave_review.html', {
        'form': form,
        'reservation': reservation,
    })


@login_required
def update_order_status(request, reservation_id):
    """Update order status (seller only)."""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Only the seller can update order status
    if request.user != reservation.meal.seller:
        messages.error(request, 'You do not have permission to update this order.')
        return redirect('accounts:seller_orders')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Reservation.STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            messages.success(request, f'Order #{reservation.id} status updated to {reservation.get_status_display()}')
    
    return redirect('accounts:seller_orders')


@login_required
def cancel_order(request, reservation_id):
    """Cancel an order (buyer only)."""
    reservation = get_object_or_404(Reservation, id=reservation_id, buyer=request.user)
    
    if reservation.status in ['completed', 'cancelled']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('accounts:my_orders')
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, f'Order #{reservation.id} has been cancelled.')
        return redirect('accounts:my_orders')
    
    return render(request, 'accounts/cancel_order_confirm.html', {'reservation': reservation})


@login_required
def order_chat(request, reservation_id):
    """Chat between buyer and seller for a specific reservation."""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user is buyer or seller
    if request.user != reservation.buyer and request.user != reservation.meal.seller:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('home')
    
    # Determine other party
    other_user = reservation.meal.seller if request.user == reservation.buyer else reservation.buyer
    
    # Mark messages as read
    Message.objects.filter(reservation=reservation, receiver=request.user, is_read=False).update(is_read=True)
    
    # Handle new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                reservation=reservation,
                sender=request.user,
                receiver=other_user,
                content=content
            )
            messages.success(request, 'Message sent!')
            return redirect('accounts:order_chat', reservation_id=reservation_id)
    
    # Get all messages for this reservation
    chat_messages = reservation.messages.select_related('sender', 'receiver').all()
    
    return render(request, 'accounts/order_chat.html', {
        'reservation': reservation,
        'chat_messages': chat_messages,
        'other_user': other_user,
    })

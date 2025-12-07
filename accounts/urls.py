from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Verification
    path('verify/', views.verification_apply, name='verification_apply'),
    
    # Meal management (sellers)
    path('meals/create/', views.create_meal, name='create_meal'),
    path('meals/my/', views.my_meals, name='my_meals'),
    path('meals/<int:meal_id>/edit/', views.edit_meal, name='edit_meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete_meal'),
    path('meals/<int:meal_id>/toggle/', views.toggle_meal_availability, name='toggle_meal_availability'),
    
    # Browsing (buyers)
    path('meals/browse/', views.browse_meals, name='browse_meals'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    
    # Reservations/Orders
    path('meals/<int:meal_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('orders/my/', views.my_orders, name='my_orders'),
    path('orders/seller/', views.seller_orders, name='seller_orders'),
    path('orders/<int:reservation_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:reservation_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:reservation_id>/review/', views.leave_review, name='leave_review'),
    path('orders/<int:reservation_id>/chat/', views.order_chat, name='order_chat'),
    
    # API
    path('api/meals/', views.meals_api, name='meals_api'),
]

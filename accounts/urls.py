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
    
    # Browsing (buyers)
    path('meals/browse/', views.browse_meals, name='browse_meals'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    
    # API
    path('api/meals/', views.meals_api, name='meals_api'),
]

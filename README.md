# CampusCrave

A Django-based marketplace for buying and selling home-cooked meals on campus.

## Features

### Implemented

#### For Buyers
- **Interactive Map Browsing**: Browse all available meals on an interactive Leaflet.js map
- **Geolocation Support**: Automatically centers map on your location
- **Meal Details**: View detailed information including photos, ingredients, price, and pickup location
- **Search & Filter**: Find meals near your dorm or class

#### For Sellers
- **User Authentication**: Register, login, and manage your account
- **Seller Verification**: Apply for verification to start selling
- **Create Listings**: Add meals with title, photo, description, ingredients, price
- **Interactive Location Picker**: Click on map to set exact pickup location
- **ManageListings**: Edit, delete, and toggle availability of your meals
- **Dashboard**: View all your active listings in one place

#### Admin Features
- Django admin panel for managing users, meals, and verification applications
- Approve/reject seller verification requests

## Tech Stack

- **Backend**: Django 5.0
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Maps**: Leaflet.js with OpenStreetMap tiles
- **Image Handling**: Pillow

## Installation

1. **Clone the repository**
```bash
cd campus_crave
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Create sample data** (optional)
```bash
python manage.py create_sample_data
```

5. **Run the development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Test Accounts

### Sample Users
- **Seller**: `chef_maria` / `password123` (verified seller with sample meals)
- **Buyer**: `student_john` / `password123`
- **Admin**: `admin` / `admin123`

## Project Structure

```
campus_crave/
├── accounts/                 # Main app
│   ├── models.py            # User profiles, meals, verification
│   ├── views.py             # All view logic
│   ├── forms.py             # Authentication & meal forms
│   ├── urls.py              # URL routing
│   └── admin.py             # Admin configuration
├── campuscrave/             # Project settings
│   ├── settings.py          # Django settings
│   └── urls.py              # Root URL config
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── home.html           # Landing page
│   └── accounts/           # App-specific templates
├── media/                   # User uploads (meals, IDs)
├── db.sqlite3              # Database
└── manage.py               # Django management script
```

## Key URLs

- `/` - Home page
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/verify/` - Seller verification application
- `/accounts/meals/browse/` - Browse meals on interactive map
- `/accounts/meals/create/` - Create new meal listing (verified sellers only)
- `/accounts/meals/my/` - Manage your listings
- `/admin/` - Admin panel

## Models

### UserProfile
- Extends Django User model
- Tracks verified seller status
- Phone number field

### Meal
- Title, description, ingredients
- Photo upload
- Price (decimal)
- Pickup location with latitude/longitude
- Availability toggle
- Seller reference (ForeignKey to User)

### SellerVerificationApplication
- Full name, email, student ID
- Student ID file upload
- Safety agreement checkbox
- Status (pending/approved/rejected)

## Development Notes

- **DEBUG mode**: Currently enabled for development
- **Secret key**: Using development key (change for production)
- **Media files**: Served by Django in development
- **Database**: SQLite (consider PostgreSQL for production)

## Next Steps / Future Enhancements

- Order/purchase system
- Payment integration
- Messaging between buyers and sellers
- Reviews and ratings
- Email notifications
- Advanced search filters
- Mobile app
- Production deployment configuration

## License

This project is for educational purposes.

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import SellerVerificationApplication, UserProfile, Meal, Reservation


@admin.register(SellerVerificationApplication)
class SellerVerificationApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'user', 'student_id_number', 'status', 'submitted_at', 'reviewed_at', 'review_actions']
    list_filter = ['status', 'submitted_at', 'reviewed_at']
    search_fields = ['full_name', 'email', 'student_id_number', 'user__username', 'user__email']
    readonly_fields = ['submitted_at', 'reviewed_at', 'reviewed_by', 'student_id_file_display']
    list_editable = []  # Prevent inline editing of status
    fieldsets = (
        ('Application Information', {
            'fields': ('user', 'full_name', 'email', 'student_id_number', 'student_id_file_display', 'student_id_file', 'agree_meal_safety')
        }),
        ('Review Information', {
            'fields': ('status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by')
        }),
    )
    date_hierarchy = 'submitted_at'
    actions = ['approve_applications', 'reject_applications']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Count pending applications for admin dashboard
        pending_count = SellerVerificationApplication.objects.filter(status='pending').count()
        extra_context['pending_count'] = pending_count
        return super().changelist_view(request, extra_context=extra_context)
    
    def approve_applications(self, request, queryset):
        """Bulk approve selected applications."""
        approved_count = 0
        for application in queryset.filter(status='pending'):
            application.status = 'approved'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.save()
            
            # Update or create user profile and mark as verified
            if application.user:
                profile, created = UserProfile.objects.get_or_create(user=application.user)
                profile.is_verified_seller = True
                profile.save()
            approved_count += 1
        
        self.message_user(request, f'{approved_count} application(s) approved successfully.', messages.SUCCESS)
    approve_applications.short_description = "Approve selected applications"
    
    def reject_applications(self, request, queryset):
        """Bulk reject selected applications."""
        rejected_count = 0
        for application in queryset.filter(status='pending'):
            application.status = 'rejected'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.save()
            rejected_count += 1
        
        self.message_user(request, f'{rejected_count} application(s) rejected.', messages.SUCCESS)
    reject_applications.short_description = "Reject selected applications"
    
    def student_id_file_display(self, obj):
        if obj.student_id_file:
            return format_html(
                '<a href="{}" target="_blank">View ID Document</a>',
                obj.student_id_file.url
            )
        return "No file uploaded"
    student_id_file_display.short_description = "ID Document"
    
    def review_actions(self, obj):
        if obj.status == 'pending':
            info = self.model._meta.app_label, self.model._meta.model_name
            approve_url = reverse('admin:%s_%s_approve' % info, args=[obj.pk])
            reject_url = reverse('admin:%s_%s_reject' % info, args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">Approve</a>'
                '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Reject</a>',
                approve_url,
                reject_url
            )
        return obj.get_status_display()
    review_actions.short_description = "Actions"
    
    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('<int:application_id>/approve/', self.admin_site.admin_view(self.approve_application), name='%s_%s_approve' % info),
            path('<int:application_id>/reject/', self.admin_site.admin_view(self.reject_application), name='%s_%s_reject' % info),
        ]
        return custom_urls + urls
    
    def approve_application(self, request, application_id):
        """Approve a seller verification application."""
        application = get_object_or_404(SellerVerificationApplication, pk=application_id)
        
        if application.status != 'pending':
            messages.error(request, f'Application is already {application.get_status_display()}.')
            return redirect('admin:accounts_sellerverificationapplication_change', application_id)
        
        # Update application status
        application.status = 'approved'
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.save()
        
        # Update or create user profile and mark as verified
        if application.user:
            profile, created = UserProfile.objects.get_or_create(user=application.user)
            profile.is_verified_seller = True
            profile.save()
            messages.success(request, f'Application approved! User {application.user.username} is now a verified seller.')
        else:
            messages.warning(request, 'Application approved, but no user account was linked. Please verify manually.')
        
        return redirect('admin:accounts_sellerverificationapplication_changelist')
    
    def reject_application(self, request, application_id):
        """Reject a seller verification application."""
        application = get_object_or_404(SellerVerificationApplication, pk=application_id)
        
        if application.status != 'pending':
            messages.error(request, f'Application is already {application.get_status_display()}.')
            return redirect('admin:accounts_sellerverificationapplication_change', application_id)
        
        # Update application status
        application.status = 'rejected'
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.save()
        
        messages.success(request, f'Application from {application.full_name} has been rejected.')
        return redirect('admin:accounts_sellerverificationapplication_changelist')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'reviewed_by')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified_seller', 'phone_number']
    list_filter = ['is_verified_seller']
    search_fields = ['user__username', 'user__email']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'pickup_location', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['title', 'seller__username', 'pickup_location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'meal', 'buyer', 'seller_display', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['meal__title', 'buyer__username', 'meal__seller__username', 'buyer_phone']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    list_editable = ['status']
    
    def seller_display(self, obj):
        return obj.meal.seller.username
    seller_display.short_description = 'Seller'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('meal', 'buyer', 'meal__seller')

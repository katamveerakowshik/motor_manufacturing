from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, FreelancerProfile, WorkItem, Submission, CompanyStats

class FreelancerProfileInline(admin.StackedInline):
    model = FreelancerProfile
    can_delete = False
    verbose_name_plural = 'Freelancer Profiles'

class CustomUserAdmin(UserAdmin):
    inlines = (FreelancerProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Approval Status', {'fields': ('is_approved',)}),
    )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('work_item', 'freelancer', 'status', 'submitted_at', 'hours_spent', 'quality_check_passed')
    list_filter = ('status', 'quality_check_passed')
    search_fields = ('work_item__title', 'freelancer__username', 'notes', 'components_used')
    date_hierarchy = 'submitted_at'
    readonly_fields = ('id', 'submitted_at')
    fieldsets = (
        ('Submission Details', {
            'fields': ('id', 'work_item', 'freelancer', 'submitted_at', 'status')
        }),
        ('Work Content', {
            'fields': ('notes', 'components_used', 'hours_spent', 'design_attachments', 'quality_check_passed')
        }),
        ('Review', {
            'fields': ('reviewer_comments', 'reviewed_at')
        }),
    )
    actions = ['approve_submissions', 'reject_submissions']
    
    def approve_submissions(self, request, queryset):
        count = 0
        for submission in queryset.filter(status='PENDING'):
            submission.approve("Approved by admin on " + timezone.now().strftime("%Y-%m-%d %H:%M"))
            count += 1
        self.message_user(request, f'{count} submissions were approved. 1000rs added to each freelancer earnings.')
    approve_submissions.short_description = "Approve selected submissions and credit earnings"
    
    def reject_submissions(self, request, queryset):
        count = 0
        for submission in queryset.filter(status='PENDING'):
            submission.reject("Rejected by admin on " + timezone.now().strftime("%Y-%m-%d %H:%M"))
            count += 1
        self.message_user(request, f'{count} submissions were rejected. Work items returned to available pool.')
    reject_submissions.short_description = "Reject selected submissions"

@admin.register(CompanyStats)
class CompanyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'vehicles_sold', 'total_revenue')
    date_hierarchy = 'date'

admin.site.register(User, CustomUserAdmin)

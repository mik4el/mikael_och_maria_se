from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from mom_invite.models import UserProfile, Guest

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]
    def lastLogin(self, obj):
        try:
            return obj.get_profile().lastLogin
        except UserProfile.DoesNotExist:
            return ''
    def attendChoice(self, obj):
        try:
            return obj.get_profile().get_attend_choice_display()
        except UserProfile.DoesNotExist:
            return ''
    def name(self, obj):
        try:
            return obj.get_profile().name
        except UserProfile.DoesNotExist:
            return ''
    def guests_invited(self, obj):
        return obj.get_profile().guests_invited()

    list_display = UserAdmin.list_display  = ('name', 'lastLogin', 'attendChoice', 'guests_invited')
    list_filter = UserAdmin.list_filter + ('userprofile__lastLogin', 'userprofile__attend_choice')

admin.site.register(User, UserProfileAdmin)

class GuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'alcohol_ok', 'food_comment', 'best_book', 'mobile_number', 'email_address', 'is_active' )
    list_filter = ('alcohol_ok', 'is_active' )
    
admin.site.register(Guest, GuestAdmin)
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib import admin
User = get_user_model()

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm


from .models import Drivers, Ownerprofiles, PhoneOTP,Vehicle,JobRequest,DriverRequest,Notice,Rating

admin.site.register(PhoneOTP)
admin.site.register(Vehicle)
admin.site.register(JobRequest)
admin.site.register(DriverRequest)
admin.site.register(Rating)
admin.site.register(Notice)

class DriverInline(admin.StackedInline):
    model = Drivers
    can_delete = False
    verbose_name_plural = 'Drivers'
    fk_name = 'user'

class OwnerInline(admin.StackedInline):
    model = Ownerprofiles
    can_delete = False
    verbose_name_plural = 'Ownerprofiles'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'phone','email', 'auth_provider',  'admin',)
    list_filter = ('standard','staff','active' ,'admin', )
    fieldsets = (
        (None, {'fields': ('phone', 'email','otp')}),
        ('Personal info', {'fields': ('name', 'standard','score',)}),
        ('Permissions', {'fields': ('admin','staff','active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2')}
        ),
    )


    search_fields = ('phone','name')
    ordering = ('phone','name')
    filter_horizontal = ()


    inlines = (DriverInline, OwnerInline)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.register(User, UserAdmin)



# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)
from django.contrib import admin
from .models import CustomUser, CustomGroup
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


class CustomUserAdmin(BaseUserAdmin):
    # we only want to show the fields below
    list_display = ('email', 'firstname', 'lastname', 'is_admin',)
    list_filter = ('is_admin',)
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal info', {'fields': ('firstname', 'lastname',)}),
        ('Permissions', {'fields': ('is_admin', 'groups', 'data')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)
        }),
    )


# Now register the new UserAdmin...
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup)

# we dont need this!
admin.site.unregister(Group)

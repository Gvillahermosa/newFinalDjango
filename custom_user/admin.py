from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin
from .models import User

# admin.site.register(User, BaseUserAdmin)

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'student_id', 'student_id_display', 'firstname', 'lastname', 'user_type')

    def student_id_display(self, obj):
        if obj.student_id:
            return obj.student_id.studID
        else:
            return ''
    student_id_display.short_description = 'Student ID'

    def firstname(self, obj):
        if obj.student_id:
            return obj.student_id.firstname
        else:
            return ''

    def lastname(self, obj):
        if obj.student_id:
            return obj.student_id.lastname
        else:
            return ''
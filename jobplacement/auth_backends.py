from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import JobPlacementAdminUser, StudentUser

class AdminUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = JobPlacementAdminUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except JobPlacementAdminUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return JobPlacementAdminUser.objects.get(pk=user_id)
        except JobPlacementAdminUser.DoesNotExist:
            return None

class StudentUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = StudentUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except StudentUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return StudentUser.objects.get(pk=user_id)
        except StudentUser.DoesNotExist:
            return None

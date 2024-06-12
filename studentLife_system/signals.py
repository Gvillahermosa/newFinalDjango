# your_app/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import exit_interview_db, OjtAssessment, counseling_schedule

@receiver(pre_save, sender=exit_interview_db)
def update_exit_interview_status(sender, instance, **kwargs):
    instance.check_and_update_status()

@receiver(pre_save, sender=OjtAssessment)
def update_ojt_assessment_status(sender, instance, **kwargs):
    instance.check_and_update_status()

@receiver(pre_save, sender=counseling_schedule)
def update_counseling_schedule_status(sender, instance, **kwargs):
    instance.check_and_update_status()

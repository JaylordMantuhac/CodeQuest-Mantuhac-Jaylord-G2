from django.contrib import admin
from .models import Challenge, Submission


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'created_by', 'created_at')
    list_filter = ('category', 'difficulty')
    search_fields = ('title',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'challenge', 'is_correct', 'submitted_at')
    list_filter = ('is_correct',)

from django.contrib import admin
from .models import UserProfile, UserResponse


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "age", "gender", "profession","scenario", "created_at")


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question","answer", "sentiment", "emotion_score", "created_at")

from django.contrib import admin
from .models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "first_visited_at", "last_visited_at")
    list_filter = ("lesson__course",)
    search_fields = ("user__username", "lesson__title")
    raw_id_fields = ("user", "lesson")
    readonly_fields = ("first_visited_at", "last_visited_at")

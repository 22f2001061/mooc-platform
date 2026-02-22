from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("order", "title", "video_url", "video_type_display", "created_at")
    readonly_fields = ("video_type_display", "created_at")
    ordering = ("order", "created_at")

    @admin.display(description="Video type")
    def video_type_display(self, obj: Lesson) -> str:
        return obj.get_video_type_display()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "short_description", "lesson_count", "manage_link", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    inlines = [LessonInline]

    @admin.display(description="Lessons")
    def lesson_count(self, obj: Course) -> int:
        return obj.lessons.count()

    @admin.display(description="Staff UI")
    def manage_link(self, obj: Course):
        from django.urls import reverse
        url = reverse("courses:manage_course_detail", kwargs={"pk": obj.pk})
        return format_html('<a href="{}">Manage →</a>', url)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "video_type", "has_content", "created_at")
    list_filter = ("course", "video_type")
    search_fields = ("title", "content", "course__title")
    readonly_fields = ("video_type", "youtube_embed_preview", "created_at", "updated_at")
    autocomplete_fields = ("course",)
    fieldsets = (
        (None, {
            "fields": ("course", "title", "order"),
        }),
        ("Video", {
            "fields": ("video_url", "video_type", "youtube_embed_preview"),
            "description": "Paste a YouTube URL or direct video link. video_type is set automatically.",
        }),
        ("Content", {
            "fields": ("content",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Has content", boolean=True)
    def has_content(self, obj: Lesson) -> bool:
        return bool(obj.content)

    @admin.display(description="Embed preview")
    def youtube_embed_preview(self, obj: Lesson):
        url = obj.youtube_embed_url
        if not url:
            return "—"
        return format_html(
            '<iframe width="480" height="270" src="{}" frameborder="0" '
            'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>',
            url,
        )


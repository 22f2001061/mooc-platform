"""
Forms for staff-facing course and lesson management UI.

Kept separate from models to allow:
- Field-level validation (YouTube URL check)
- Different field subsets for create vs edit
- Custom widgets (e.g. Textarea sizing)
"""
from django import forms

from .models import Course, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "short_description", "description"]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "description": forms.Textarea(attrs={"rows": 8}),
        }
        help_texts = {
            "short_description": "Shown on course cards in the catalog (max 500 chars).",
            "description": "Full description visible on the course detail page.",
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "order", "video_url", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "video_url": forms.URLInput(attrs={"placeholder": "https://www.youtube.com/watch?v=..."}),
        }
        help_texts = {
            "video_url": (
                "Paste any YouTube URL (watch, short, or embed format) or a direct "
                "video file URL (.mp4, .webm). Leave blank for text-only lessons."
            ),
            "order": "Lessons are sorted by this number (ascending). Use 10, 20, 30… to leave gaps.",
            "content": "Optional reading material or notes displayed below the video.",
        }

    def clean_video_url(self) -> str:
        url = self.cleaned_data.get("video_url", "").strip()
        if not url:
            return url

        # Validate that YouTube URLs have a recognisable video ID
        from .models import Lesson as LessonModel
        if ("youtube.com" in url or "youtu.be" in url) and not LessonModel._YOUTUBE_RE.search(url):
            raise forms.ValidationError(
                "Could not extract a YouTube video ID from this URL. "
                "Please use a standard watch, short or embed link."
            )
        return url

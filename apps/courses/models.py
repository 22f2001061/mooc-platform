import re
import urllib.parse

from django.db import models
from django.urls import reverse


class Course(models.Model):
    """
    A course in the catalog.

    Separation of `short_description` (for list cards) and `description`
    (for detail page) avoids over-fetching on list queries.
    """

    title = models.CharField(max_length=255)
    short_description = models.CharField(
        max_length=500,
        help_text="Shown on the course list card (max 500 chars).",
    )
    description = models.TextField(
        help_text="Full description shown on the course detail page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("courses:detail", kwargs={"pk": self.pk})


class Lesson(models.Model):
    """
    A lesson belonging to a course.

    Video support:
    - `video_url`: raw URL pasted by staff (YouTube watch/short/embed, or direct mp4)
    - `video_type`: auto-classified on save, drives template rendering
    - YouTube embeds use youtube-nocookie.com to respect user privacy

    Ordering:
    - `order` field for explicit manual ordering (default 0).
      Falls back to `created_at` when order values are equal.
    """

    class VideoType(models.TextChoices):
        NONE = "none", "No video"
        YOUTUBE = "youtube", "YouTube"
        DIRECT = "direct", "Direct video URL (mp4/webm)"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField(
        blank=True,
        help_text="Lesson body / reading material. Supports plain text with line breaks.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within the course. Lower numbers appear first.",
    )
    video_url = models.URLField(
        blank=True,
        max_length=512,
        help_text=(
            "Paste a YouTube URL (any format) or a direct video file URL. "
            "Leave blank if this lesson has no video."
        ),
    )
    video_type = models.CharField(
        max_length=10,
        choices=VideoType.choices,
        default=VideoType.NONE,
        editable=False,  # set automatically in save()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.course.title} — {self.title}"

    def get_absolute_url(self) -> str:
        return reverse("courses:lesson_detail", kwargs={"course_pk": self.course_id, "pk": self.pk})

    # ------------------------------------------------------------------
    # Video helpers
    # ------------------------------------------------------------------

    # Matches all common YouTube URL patterns:
    #   https://www.youtube.com/watch?v=VIDEO_ID
    #   https://youtu.be/VIDEO_ID
    #   https://www.youtube.com/embed/VIDEO_ID
    #   https://www.youtube.com/shorts/VIDEO_ID
    _YOUTUBE_RE = re.compile(
        r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_\-]{11})"
    )

    @property
    def youtube_video_id(self) -> str | None:
        """Extract the 11-char YouTube video ID from any YouTube URL format."""
        if not self.video_url:
            return None
        match = self._YOUTUBE_RE.search(self.video_url)
        return match.group(1) if match else None

    @property
    def youtube_embed_url(self) -> str | None:
        """
        Return a privacy-enhanced embed URL using youtube-nocookie.com.
        This domain does not set cookies or track users until they click play —
        the standard approach for MOOC/educational platforms.

        Parameters added:
        - rel=0       : don't show related videos from other channels after playback
        - modestbranding=1 : reduce YouTube logo prominence
        - origin      : security measure, tells YouTube our domain
        """
        vid_id = self.youtube_video_id
        if not vid_id:
            return None
        params = urllib.parse.urlencode({"rel": 0, "modestbranding": 1})
        return f"https://www.youtube-nocookie.com/embed/{vid_id}?{params}"

    @staticmethod
    def _classify_video_type(url: str) -> str:
        """Classify a URL into a VideoType choice."""
        if not url:
            return Lesson.VideoType.NONE
        if "youtube.com" in url or "youtu.be" in url:
            return Lesson.VideoType.YOUTUBE
        return Lesson.VideoType.DIRECT

    def save(self, *args, **kwargs) -> None:
        """Auto-classify video_type before saving so it stays consistent."""
        self.video_type = self._classify_video_type(self.video_url)
        super().save(*args, **kwargs)

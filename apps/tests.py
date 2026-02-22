"""
Tests for the MOOC platform.

Strategy:
- Service layer tests: pure business logic, no HTTP
- View tests: integration via Django test client
- Focus on critical paths: enrollment, progress tracking, access control
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.courses.models import Course, Lesson
from apps.enrollments.models import Enrollment
from apps.enrollments.services import EnrollmentService
from apps.progress.models import LessonProgress
from apps.progress.services import ProgressService

User = get_user_model()


# ---------------------------------------------------------------------------
# Model / helper tests
# ---------------------------------------------------------------------------

class LessonVideoTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="C", short_description="S", description="D"
        )

    def _make_lesson(self, url=""):
        return Lesson.objects.create(course=self.course, title="L", content="", video_url=url)

    def test_youtube_watch_url_classified(self):
        lesson = self._make_lesson("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(lesson.video_type, Lesson.VideoType.YOUTUBE)

    def test_youtube_short_url_classified(self):
        lesson = self._make_lesson("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(lesson.video_type, Lesson.VideoType.YOUTUBE)

    def test_youtube_shorts_url_classified(self):
        lesson = self._make_lesson("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        self.assertEqual(lesson.video_type, Lesson.VideoType.YOUTUBE)

    def test_direct_video_classified(self):
        lesson = self._make_lesson("https://cdn.example.com/video.mp4")
        self.assertEqual(lesson.video_type, Lesson.VideoType.DIRECT)

    def test_no_url_classified_as_none(self):
        lesson = self._make_lesson("")
        self.assertEqual(lesson.video_type, Lesson.VideoType.NONE)

    def test_youtube_video_id_extracted_from_watch(self):
        lesson = self._make_lesson("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(lesson.youtube_video_id, "dQw4w9WgXcQ")

    def test_youtube_video_id_extracted_from_short(self):
        lesson = self._make_lesson("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(lesson.youtube_video_id, "dQw4w9WgXcQ")

    def test_youtube_embed_url_uses_nocookie_domain(self):
        lesson = self._make_lesson("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertIn("youtube-nocookie.com", lesson.youtube_embed_url)
        self.assertIn("dQw4w9WgXcQ", lesson.youtube_embed_url)

    def test_youtube_embed_url_none_for_no_video(self):
        lesson = self._make_lesson("")
        self.assertIsNone(lesson.youtube_embed_url)

    def test_lesson_order_field_default(self):
        lesson = self._make_lesson()
        self.assertEqual(lesson.order, 0)


# ---------------------------------------------------------------------------
# Enrollment service tests
# ---------------------------------------------------------------------------

class EnrollmentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass123")
        self.course = Course.objects.create(
            title="Test Course", short_description="Short", description="Long description",
        )

    def test_enroll_creates_enrollment(self):
        enrollment, created = EnrollmentService.enroll(self.user, self.course)
        self.assertTrue(created)
        self.assertEqual(enrollment.user, self.user)

    def test_enroll_idempotent(self):
        EnrollmentService.enroll(self.user, self.course)
        _, created = EnrollmentService.enroll(self.user, self.course)
        self.assertFalse(created)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_is_enrolled_returns_true_when_enrolled(self):
        EnrollmentService.enroll(self.user, self.course)
        self.assertTrue(EnrollmentService.is_enrolled(self.user, self.course))

    def test_is_enrolled_returns_false_when_not_enrolled(self):
        self.assertFalse(EnrollmentService.is_enrolled(self.user, self.course))


# ---------------------------------------------------------------------------
# Progress service tests
# ---------------------------------------------------------------------------

class ProgressServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass123")
        self.course = Course.objects.create(title="T", short_description="S", description="D")
        self.lesson = Lesson.objects.create(course=self.course, title="L1", content="")

    def test_mark_visited_creates_progress(self):
        ProgressService.mark_visited(self.user, self.lesson)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())

    def test_mark_visited_idempotent(self):
        ProgressService.mark_visited(self.user, self.lesson)
        ProgressService.mark_visited(self.user, self.lesson)
        self.assertEqual(LessonProgress.objects.count(), 1)

    def test_get_visited_ids_returns_set(self):
        ProgressService.mark_visited(self.user, self.lesson)
        ids = ProgressService.get_visited_ids(self.user, self.course)
        self.assertIsInstance(ids, set)
        self.assertIn(self.lesson.id, ids)


# ---------------------------------------------------------------------------
# Course + lesson view tests
# ---------------------------------------------------------------------------

class CourseViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carol", password="pass123")
        self.course = Course.objects.create(
            title="Django 101", short_description="Learn Django", description="Full desc"
        )

    def test_course_list_accessible_to_anonymous(self):
        response = self.client.get(reverse("courses:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django 101")

    def test_detail_shows_login_prompt_when_anonymous(self):
        response = self.client.get(reverse("courses:detail", kwargs={"pk": self.course.pk}))
        self.assertContains(response, "Log in to enroll")

    def test_detail_shows_enroll_button_when_authenticated(self):
        self.client.login(username="carol", password="pass123")
        response = self.client.get(reverse("courses:detail", kwargs={"pk": self.course.pk}))
        self.assertContains(response, "Enroll Now")

    def test_detail_shows_enrolled_message_when_enrolled(self):
        EnrollmentService.enroll(self.user, self.course)
        self.client.login(username="carol", password="pass123")
        response = self.client.get(reverse("courses:detail", kwargs={"pk": self.course.pk}))
        self.assertContains(response, "You are enrolled")


class LessonDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eve", password="pass123")
        self.course = Course.objects.create(title="C", short_description="S", description="D")
        self.lesson = Lesson.objects.create(
            course=self.course, title="Lesson 1", content="Hello!",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    def test_unenrolled_user_redirected(self):
        self.client.login(username="eve", password="pass123")
        response = self.client.get(
            reverse("courses:lesson_detail", kwargs={"course_pk": self.course.pk, "pk": self.lesson.pk})
        )
        self.assertRedirects(response, reverse("courses:detail", kwargs={"pk": self.course.pk}))

    def test_enrolled_user_sees_video(self):
        EnrollmentService.enroll(self.user, self.course)
        self.client.login(username="eve", password="pass123")
        response = self.client.get(
            reverse("courses:lesson_detail", kwargs={"course_pk": self.course.pk, "pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 200)
        # youtube-nocookie embed should be in the response
        self.assertContains(response, "youtube-nocookie.com")

    def test_lesson_view_tracks_progress(self):
        EnrollmentService.enroll(self.user, self.course)
        self.client.login(username="eve", password="pass123")
        self.client.get(
            reverse("courses:lesson_detail", kwargs={"course_pk": self.course.pk, "pk": self.lesson.pk})
        )
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())


# ---------------------------------------------------------------------------
# Staff management view tests
# ---------------------------------------------------------------------------

class StaffManagementTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pass123", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pass123")
        self.course = Course.objects.create(title="C", short_description="S", description="D")

    def test_dashboard_requires_staff(self):
        self.client.login(username="student", password="pass123")
        response = self.client.get(reverse("courses:manage_dashboard"))
        # Non-staff redirected to admin login
        self.assertNotEqual(response.status_code, 200)

    def test_staff_can_access_dashboard(self):
        self.client.login(username="staff", password="pass123")
        response = self.client.get(reverse("courses:manage_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_create_course(self):
        self.client.login(username="staff", password="pass123")
        response = self.client.post(
            reverse("courses:manage_course_create"),
            {"title": "New Course", "short_description": "Short", "description": "Long"},
        )
        self.assertEqual(Course.objects.filter(title="New Course").count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_staff_can_edit_course(self):
        self.client.login(username="staff", password="pass123")
        self.client.post(
            reverse("courses:manage_course_edit", kwargs={"pk": self.course.pk}),
            {"title": "Updated", "short_description": "S", "description": "D"},
        )
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated")

    def test_staff_can_create_lesson_with_youtube(self):
        self.client.login(username="staff", password="pass123")
        self.client.post(
            reverse("courses:manage_lesson_create", kwargs={"course_pk": self.course.pk}),
            {
                "title": "Intro",
                "order": 10,
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "content": "some text",
            },
        )
        lesson = Lesson.objects.get(course=self.course)
        self.assertEqual(lesson.video_type, Lesson.VideoType.YOUTUBE)
        self.assertEqual(lesson.youtube_video_id, "dQw4w9WgXcQ")

    def test_staff_can_delete_course(self):
        self.client.login(username="staff", password="pass123")
        pk = self.course.pk
        self.client.post(reverse("courses:manage_course_delete", kwargs={"pk": pk}))
        self.assertFalse(Course.objects.filter(pk=pk).exists())

    def test_lesson_form_rejects_bad_youtube_url(self):
        self.client.login(username="staff", password="pass123")
        response = self.client.post(
            reverse("courses:manage_lesson_create", kwargs={"course_pk": self.course.pk}),
            {"title": "L", "order": 10, "video_url": "https://youtube.com/notavideo", "content": ""},
        )
        # Form should re-render with errors, not redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could not extract a YouTube video ID")

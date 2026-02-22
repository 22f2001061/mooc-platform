from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("enrollments/", include("apps.enrollments.urls", namespace="enrollments")),
    path("", include("apps.courses.urls", namespace="courses")),
]

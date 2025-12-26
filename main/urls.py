from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    CourseViewSet,
    StudentViewSet,
    EnrollmentViewSet,
    CategoryViewSet,
    StudentCoursesAPIView,
    CourseStudentsAPIView,
)

router = SimpleRouter()
router.register('courses', CourseViewSet, basename='course')
router.register('students', StudentViewSet, basename='student')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('students/<int:pk>/courses/', StudentCoursesAPIView.as_view(), name='student-courses'),
    path('courses/<int:pk>/students/', CourseStudentsAPIView.as_view(), name='course-students'),

    path('', include(router.urls)),
]

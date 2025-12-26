from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Course, Student, Enrollment, Category
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    CourseDetailSerializer,
    StudentSerializer,
    EnrollmentSerializer,
)


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'id']



class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    pagination_class = DefaultPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['status', 'category', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        status_filter = self.request.query_params.get('status')
        category_id = self.request.query_params.get('category')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by('-created_at')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.enrollments.exists():
            return Response(
                {
                    'error': "Kursga yozilgan studentlar bor. "
                             "Avval yozilishlarni o‘chiring."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(
            {'message': 'Kurs muvaffaqiyatli o‘chirildi'},
            status=status.HTTP_204_NO_CONTENT
        )


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'created_at']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.enrollments.exists():
            return Response(
                {
                    'error': "Student kurslarga yozilgan. "
                             "Avval yozilishlarni o‘chiring."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(
            {'message': 'Student muvaffaqiyatli o‘chirildi'},
            status=status.HTTP_204_NO_CONTENT
        )



class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().order_by('-enrolled_at')
    serializer_class = EnrollmentSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'student', 'completed']
    ordering_fields = ['enrolled_at', 'completed_at']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data['course']
        student = serializer.validated_data['student']

        if not course.is_active:
            return Response(
                {'error': 'Bu kurs faol emas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not student.is_active:
            return Response(
                {'error': 'Bu student faol emas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Enrollment.objects.filter(course=course, student=student).exists():
            return Response(
                {'error': 'Student allaqachon bu kursga yozilgan.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class StudentCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        student = get_object_or_404(Student, id=self.kwargs['pk'])
        return Course.objects.filter(
            enrollments__student=student
        ).distinct().order_by('-created_at')



class CourseStudentsAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs['pk'])
        return Student.objects.filter(
            enrollments__course=course
        ).distinct().order_by('-created_at')



class PopularCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        from django.db.models import Count
        return Course.objects.annotate(
            student_count=Count('enrollments')
        ).filter(
            student_count__gte=10,
            is_active=True
        ).order_by('-student_count')


class CategoryCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        category = get_object_or_404(Category, id=self.kwargs['pk'])
        return category.courses.filter(
            is_active=True
        ).order_by('-created_at')



class ActiveStudentsAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Student.objects.filter(
            is_active=True,
            enrollments__isnull=False
        ).distinct().order_by('-created_at')

from rest_framework import serializers
from .models import Course, Student, Enrollment, Category


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "slug", "course_count"]
        read_only_fields = ["slug"]

    def get_course_count(self, obj):
        return obj.courses.count()

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Kategoriya nomi kamida 3 ta belgidan iborat bo‘lishi kerak!"
            )
        if Category.objects.filter(title__iexact=value).exclude(
            pk=getattr(self.instance, "pk", None)
        ).exists():
            raise serializers.ValidationError(
                "Bu nomdagi kategoriya allaqachon mavjud!"
            )
        return value


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.title", read_only=True)
    student_count = serializers.SerializerMethodField(read_only=True)
    is_popular = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "price", "status",
            "category", "category_name", "is_active",
            "created_at", "updated_at", "student_count", "is_popular",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_student_count(self, obj):
        return obj.enrollments.count()

    def get_is_popular(self, obj):
        return obj.enrollments.count() >= 10

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError(
                "Kurs nomi kamida 5 ta belgidan iborat bo‘lishi kerak!"
            )
        if Course.objects.filter(title__iexact=value).exclude(
            pk=getattr(self.instance, "pk", None)
        ).exists():
            raise serializers.ValidationError(
                "Bu nomdagi kurs allaqachon mavjud!"
            )
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Narx manfiy bo‘lishi mumkin emas!"
            )
        return value

    def validate(self, attrs):
        if attrs.get("status") == "beginner" and attrs.get("price", 0) > 500_000:
            raise serializers.ValidationError(
                {"price": "Boshlang‘ich kurslar 500,000 so‘mdan oshmasligi kerak!"}
            )
        return attrs


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    enrolled_students = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "price", "status",
            "category", "is_active", "created_at", "updated_at",
            "enrolled_students",
        ]

    def get_enrolled_students(self, obj):
        students = Student.objects.filter(
            enrollments__course=obj
        ).distinct()
        return StudentSerializer(students, many=True).data


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    enrolled_courses_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id", "first_name", "last_name", "full_name", "email",
            "slug", "phone", "is_active",
            "created_at", "updated_at", "enrolled_courses_count",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_enrolled_courses_count(self, obj):
        return obj.enrollments.count()

    def validate_email(self, value):
        value = value.lower().strip()
        if Student.objects.filter(email=value).exclude(
            pk=getattr(self.instance, "pk", None)
        ).exists():
            raise serializers.ValidationError(
                "Bu email allaqachon ro‘yxatdan o‘tgan!"
            )
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "course", "student",
            "course_title", "student_name",
            "enrolled_at", "completed", "completed_at",
        ]
        read_only_fields = ["enrolled_at", "completed_at"]

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"


class StudentCourseSerializer(serializers.ModelSerializer):
    enrollment_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'status',
            'enrollment_info'
        ]
    
    def get_enrollment_info(self, obj):
        request = self.context.get('request')
        student_id = self.context.get('student_id')
        
        if student_id:
            enrollment = Enrollment.objects.filter(
                course=obj,
                student_id=student_id
            ).first()
            
            if enrollment:
                return {
                    'enrollment_id': enrollment.id,
                    'enrolled_at': enrollment.enrolled_at,
                    'completed': enrollment.completed,
                    'completed_at': enrollment.completed_at
                }
        return None


class CourseStudentSerializer(serializers.ModelSerializer):
    enrollment_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email',
            'enrollment_info'
        ]
    
    def get_enrollment_info(self, obj):
        request = self.context.get('request')
        course_id = self.context.get('course_id')
        
        if course_id:
            enrollment = Enrollment.objects.filter(
                student=obj,
                course_id=course_id
            ).first()
            
            if enrollment:
                return {
                    'enrollment_id': enrollment.id,
                    'enrolled_at': enrollment.enrolled_at,
                    'completed': enrollment.completed
                }
        return None
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from urllib.parse import urlencode

from .models import Student, Subject, Mark


def search_student(request):
    if not request.user.is_authenticated:
        return redirect("student_login")

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        logout(request)
        return redirect("student_login")

    return redirect(
        "student_result",
        register_number=student.register_number
    )


def student_result(request, register_number):
    if not request.user.is_authenticated:
        return redirect("student_login")

    student = get_object_or_404(
        Student,
        register_number=register_number,
        user=request.user
    )

    marks = Mark.objects.filter(
        student=student
    ).select_related("subject")

    total = sum(mark.marks for mark in marks)
    max_total = sum(
        mark.subject.max_marks for mark in marks
    )

    percentage = (
        round((total / max_total) * 100, 2)
        if max_total > 0 else 0
    )

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    else:
        grade = "D"

    result_status = "PASS" if percentage >= 35 else "FAIL"

    return render(
        request,
        "results/student_result.html",
        {
            "student": student,
            "marks": marks,
            "total": total,
            "max_total": max_total,
            "percentage": percentage,
            "grade": grade,
            "result_status": result_status,
        }
    )


def student_login(request):
    error = ""

    if request.user.is_authenticated:
        return redirect("search_student")

    if request.method == "POST":
        register_number = request.POST.get(
            "register_number", ""
        ).strip()
        password = request.POST.get("password", "")

        try:
            student = Student.objects.select_related("user").get(
                register_number__iexact=register_number
            )
        except Student.DoesNotExist:
            error = "Invalid register number or password."
        else:
            if student.user is None:
                error = "No login account is linked to this student."
            else:
                user = authenticate(
                    request,
                    username=student.user.username,
                    password=password
                )

                if user is not None:
                    login(request, user)
                    return redirect(
                        "student_result",
                        register_number=student.register_number
                    )
                else:
                    error = "Invalid register number or password."

    return render(
        request,
        "results/student_login.html",
        {"error": error}
    )


def student_logout(request):
    logout(request)
    return redirect("student_login")


@staff_member_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_subjects = Subject.objects.count()
    total_marks = Mark.objects.count()

    recent_students = Student.objects.order_by("-id")[:5]

    passed_students = 0
    failed_students = 0
    top_students = []
    chart_students = []

    for student in Student.objects.all():
        student_marks = Mark.objects.filter(
            student=student
        ).select_related("subject")

        total = sum(mark.marks for mark in student_marks)
        max_total = sum(
            mark.subject.max_marks for mark in student_marks
        )

        if max_total > 0:
            percentage = round((total / max_total) * 100, 2)

            if percentage >= 35:
                passed_students += 1
            else:
                failed_students += 1

            top_students.append({
                "student": student,
                "percentage": percentage,
            })

            chart_students.append({
                "name": student.name,
                "percentage": percentage,
            })

    top_students.sort(
        key=lambda item: item["percentage"],
        reverse=True
    )
    top_students = top_students[:5]

    chart_students.sort(
        key=lambda item: item["percentage"],
        reverse=True
    )
    chart_students = chart_students[:10]

    subject_chart = []

    for subject in Subject.objects.all().order_by("subject_name"):
        subject_marks = Mark.objects.filter(subject=subject)
        marks_count = subject_marks.count()

        if marks_count > 0 and subject.max_marks > 0:
            total_subject_marks = sum(
                mark.marks for mark in subject_marks
            )
            average_marks = total_subject_marks / marks_count
            average_percentage = round(
                (average_marks / subject.max_marks) * 100, 2
            )

            subject_chart.append({
                "name": subject.subject_name,
                "code": subject.subject_code,
                "percentage": average_percentage,
                "students_count": marks_count,
                "average_marks": round(average_marks, 2),
                "max_marks": subject.max_marks,
            })

    return render(
        request,
        "results/admin_dashboard.html",
        {
            "total_students": total_students,
            "total_subjects": total_subjects,
            "total_marks": total_marks,
            "recent_students": recent_students,
            "passed_students": passed_students,
            "failed_students": failed_students,
            "top_students": top_students,
            "chart_students": chart_students,
            "subject_chart": subject_chart,
        }
    )


@staff_member_required
def view_all_students(request):
    students = Student.objects.all().order_by("register_number")
    return render(
        request,
        "results/view_all_students.html",
        {"students": students}
    )


@staff_member_required
def admin_search_student(request):
    student = None
    error = ""

    if request.method == "POST":
        register_number = request.POST.get(
            "register_number", ""
        ).strip()
    else:
        register_number = request.GET.get(
            "register_number", ""
        ).strip()

    if register_number:
        try:
            student = Student.objects.get(
                register_number__iexact=register_number
            )
        except Student.DoesNotExist:
            error = "Student not found. Check the register number."
    elif request.method == "POST":
        error = "Please enter a register number."

    return render(
        request,
        "results/admin_search_student.html",
        {"student": student, "error": error}
    )


@staff_member_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    error = ""

    if request.method == "POST":
        register_number = request.POST.get(
            "register_number", ""
        ).strip()
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        department = request.POST.get("department", "").strip()
        year = request.POST.get("year", "").strip()

        if not all([register_number, name, email, department, year]):
            error = "Please fill in all fields."
        else:
            try:
                year_value = int(year)
                if year_value < 1:
                    raise ValueError

                duplicate = Student.objects.filter(
                    register_number__iexact=register_number
                ).exclude(id=student.id).exists()

                if duplicate:
                    error = "Register number already exists."
                else:
                    student.register_number = register_number
                    student.name = name
                    student.email = email
                    student.department = department
                    student.year = year_value
                    student.save()

                    search_url = reverse("admin_search_student")
                    query_string = urlencode({
                        "register_number": student.register_number
                    })
                    return redirect(f"{search_url}?{query_string}")

            except ValueError:
                error = "Year must be a valid positive number."

    return render(
        request,
        "results/edit_student.html",
        {"student": student, "error": error}
    )


@staff_member_required
def add_student(request):
    error = ""

    if request.method == "POST":
        register_number = request.POST.get(
            "register_number", ""
        ).strip()
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        department = request.POST.get("department", "").strip()
        year = request.POST.get("year", "").strip()
        password = request.POST.get("password", "")

        if not all([
            register_number, name, email,
            department, year, password
        ]):
            error = "Please fill in all fields, including temporary password."
        else:
            try:
                year_value = int(year)

                if year_value < 1:
                    raise ValueError

                if Student.objects.filter(
                    register_number__iexact=register_number
                ).exists():
                    error = "Register number already exists."
                elif User.objects.filter(
                    username=register_number
                ).exists():
                    error = "A login account already exists for this register number."
                elif User.objects.filter(email__iexact=email).exists():
                    error = "This email is already used by another account."
                else:
                    user = User.objects.create_user(
                        username=register_number,
                        email=email,
                        password=password,
                        first_name=name,
                    )

                    Student.objects.create(
                        user=user,
                        register_number=register_number,
                        name=name,
                        email=email,
                        department=department,
                        year=year_value,
                    )

                    return redirect("admin_dashboard")

            except ValueError:
                error = "Year must be a valid positive number."

    return render(
        request,
        "results/add_student.html",
        {"error": error}
    )


@staff_member_required
def add_marks(request):
    error = ""

    students = Student.objects.all().order_by("name")
    subjects = Subject.objects.all().order_by("subject_name")

    if request.method == "POST":
        student_id = request.POST.get("student", "")
        subject_id = request.POST.get("subject", "")
        marks_value = request.POST.get("marks", "").strip()

        if not all([student_id, subject_id, marks_value]):
            error = "Please fill in all fields."
        else:
            try:
                student = Student.objects.get(id=int(student_id))
                subject = Subject.objects.get(id=int(subject_id))
                marks_value = int(marks_value)

                if marks_value < 0 or marks_value > subject.max_marks:
                    error = (
                        f"Marks must be between 0 and "
                        f"{subject.max_marks}."
                    )
                elif Mark.objects.filter(
                    student=student, subject=subject
                ).exists():
                    error = (
                        "Marks for this student and subject "
                        "already exist."
                    )
                else:
                    Mark.objects.create(
                        student=student,
                        subject=subject,
                        marks=marks_value,
                    )
                    return redirect("admin_dashboard")

            except (
                ValueError,
                TypeError,
                Student.DoesNotExist,
                Subject.DoesNotExist
            ):
                error = "Please select a valid student and subject."

    return render(
        request,
        "results/add_marks.html",
        {
            "students": students,
            "subjects": subjects,
            "error": error,
        }
    )
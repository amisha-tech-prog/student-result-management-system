from django.contrib import admin
from django.urls import path
from results import views

urlpatterns = [
    path("", views.search_student, name="home"),

    path("admin/", admin.site.urls),

    path(
        "dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "all-students/",
        views.view_all_students,
        name="view_all_students"
    ),

    path(
        "result/<str:register_number>/",
        views.student_result,
        name="student_result"
    ),

    path(
        "search/",
        views.search_student,
        name="search_student"
    ),

    path(
        "admin-search/",
        views.admin_search_student,
        name="admin_search_student"
    ),

    path(
        "edit-student/<int:student_id>/",
        views.edit_student,
        name="edit_student"
    ),

    path(
        "add-student/",
        views.add_student,
        name="add_student"
    ),

    path(
        "add-marks/",
        views.add_marks,
        name="add_marks"
    ),

    path(
        "login/",
        views.student_login,
        name="student_login"
    ),

    path(
        "logout/",
        views.student_logout,
        name="student_logout"
    ),
]
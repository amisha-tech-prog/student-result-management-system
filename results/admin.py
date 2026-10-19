from django.contrib import admin
from .models import Student, Subject, Mark

admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Mark)
from webbrowser import register
from django.contrib.auth.models import Permission
from django.contrib import admin
from user.models import Student, Teacher, Staff, Adminn, Booking, Booking_student, Booking_teacher, Booking_staff, Booking_list, Room, Room_type, UserRole
# Register your models here.

class listShow(admin.ModelAdmin):
    list_display = ['list_no', 'start_time', 'end_time', 'bookdate']

class bookShow(admin.ModelAdmin):
    list_display = ['id', 'user_id']

class stbookShow(admin.ModelAdmin):
    list_display = ['booking_id']

class tbookShow(admin.ModelAdmin):
    list_display = ['booking_id']

class sbookShow(admin.ModelAdmin):
    list_display = ['booking_id']


admin.site.register(Student)

admin.site.register(Teacher)

admin.site.register(Staff)

admin.site.register(Adminn)

admin.site.register(Booking, bookShow)

admin.site.register(Booking_student, stbookShow)

admin.site.register(Booking_teacher, tbookShow)

admin.site.register(Booking_staff, sbookShow)

admin.site.register(Booking_list, listShow)

admin.site.register(Room)

admin.site.register(Room_type)

admin.site.register(UserRole)

admin.site.register(Permission)
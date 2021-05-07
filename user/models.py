from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.forms import ModelForm
# Create your models here.




class UserRole(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    rl = (
    (1, "นักศึกษา"),
    (2, "อาจารย์"),
    (3, "บุคคลากร"),
    )
    role = models.IntegerField(choices=rl)

class Student(models.Model):
    mj = (
    (1, "it"),
    (2, "dsba"),
    (3, "bit"),
    )
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    stu_id = models.IntegerField()
    year = models.IntegerField()
    major = models.IntegerField(choices=mj, blank=True)

    # def __str__(self):
    #     return self.user_id.username


class Adminn(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user_id.username

class Teacher(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(max_length=255)
    def __str__(self):
        return self.user_id.username


class Staff(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    def __str__(self):
        return self.user_id.username


class Booking(models.Model): #each time the user submit the booking.html create this and it contains multiple bookinglist (model) if more than one day booked at once
    st = (
    (1, "รอการอนุมัติ"),
    (2, "อนุมัติ"),
    (3, "ไม่อนุมัติ"),
    )
    id = models.AutoField(primary_key=True) #id booking
    description = models.TextField() # descipt 
    date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.IntegerField(choices=st, default = 1)
    
    status_remark = models.IntegerField(choices=st, default = 1)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Booking_student(models.Model):
    st = (
    (1, "รอการอนุมัติ"),
    (2, "อนุมัติ"),
    (3, "ไม่อนุมัติ"),
    )
    booking_id = models.OneToOneField(Booking, on_delete=models.CASCADE)
    teacher_user_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)
    staff_user_id = models.ForeignKey(Staff, on_delete=models.CASCADE, blank=True, null=True)
    teacher_date = models.DateTimeField(blank=True, null=True)
    teacher_result = models.IntegerField(choices=st, default = 1)
    staff_date = models.DateTimeField(blank=True, null=True)
    staff_result = models.IntegerField(choices=st, default = 1)


class Booking_teacher(models.Model):
    booking_id = models.OneToOneField(Booking, on_delete=models.CASCADE)

class Booking_staff(models.Model):
    booking_id = models.OneToOneField(Booking, on_delete=models.CASCADE)


class Room_type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.IntegerField()
    room_type = models.ForeignKey(Room_type, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Booking_list(models.Model): #each day of booking
    list_no = models.AutoField(primary_key=True)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    bookdate = models.DateField(blank=True, null=True)
    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    

  

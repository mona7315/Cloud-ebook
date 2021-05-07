from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.db.models import Subquery
from user.models import Student, Teacher, Staff, Adminn, Booking, Booking_student, Booking_teacher, Booking_staff, Booking_list, Room, Room_type
from django.forms import formset_factory
from user.forms import EditForm, AddRoomForm, BookRoomDescriptionForm, RangeBookingForm, BookRoomForm
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.response import Response
from user.serializers import RoomSerializer,RoomTypeSerializer

from datetime import date, timedelta

# Create your views here.
@login_required(login_url='/')
@permission_required('user.view_room', login_url='/')

def index(request):

    all_room = Room.objects.all()
    type = Room_type.objects.all()
    
    context = {
        'all_room': all_room,
        'type': type,   


    }

    return render(request, 'user/index.html', context)

class RoomList(generics.ListCreateAPIView):  #ใช้rest framework มาสร้าง api class beas view สืบทอด generics ดึงมาเป็นjson ดึงจากdatabaseละแสดงมาเป็นjason
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class RoomTypeList(generics.ListCreateAPIView):
    queryset = Room_type.objects.all()
    serializer_class = RoomTypeSerializer
 

#  ส่วนที่ดึงข้อมูลมาห้องมาเพื่อที่จะแสดงในหน้าindex แล้วก็ทำajax 
class RoomFilter(generics.RetrieveAPIView):    #เพิ่มเงื่อนไข
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


    def isEqual(self, room):                            #เช็คว่าห้องที่
        return room['room_type'] == self.type           #เช็คfk กับ typeในurl
    

    def get(self, request, *args, **kwarg):
        try:
            self.type = int(request.GET.get('type'))  #ตัวแปรหลังhttp

            if self.type:
                room = Room.objects.all()
                serializer = RoomSerializer(room, many=True)
                filter_data = filter(self.isEqual, serializer.data)   #แปลงข้อมูลเป็นjason  รับตัวที่กรอง กับ list ข้อมูลที่จะกรอง
            return Response(filter_data)
        except Exception as e:
            return Response({
                "error" : str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/')
@permission_required('user.view_booking', login_url='/index/')

def bookinglistall(request):
    context = {}

    # if request.POST.get('select') == 1:
    #     all_booklist.objects.filter(roon_id__name__icontains = 'L308')
    #     count = all_booklist.count()
    
    search_txt = request.POST.get('search','')
    all_booklist = Booking_list.objects.filter(
        Q(room_id__name__icontains= search_txt) & ~Q(booking_id__status ='2') ).distinct('booking_id')

    student = Booking_student.objects.values('booking_id_id')
    count = Booking.objects.filter(id__in = Subquery(student)).exclude(status = '2').exclude(status = '3').count()
   
    stbooking = Booking_student.objects.all()
    user_id = request.user.id
    
    context['all_booklist'] = all_booklist
    context['count'] = count
    context['stbooking'] = stbooking

    if request.user.groups.filter(name ='student').exists():
       context['group'] = 'นักศึกษา'
    elif request.user.groups.filter(name ='teacher').exists():
       context['group'] = 'อาจารย์'
    elif request.user.groups.filter(name ='extra staff').exists():
       context['group'] = 'เจ้าหน้าที่สถานที่'
    elif request.user.groups.filter(name ='staff').exists():
       context['group'] = 'บุคลากร'
    elif request.user.groups.filter(name ='admin').exists():
       context['group'] = 'ผู้ดูแลระบบ'
    
    

    
    
    return render(request, 'user/bookinglist.html', context=context)

@login_required(login_url='/')
@permission_required('user.add_booking_student', login_url='/index/')
def trackbookinglist(request): #existing booking list from users' requests

  
    all_booklist = Booking_list.objects.filter(Q(booking_id__status ='1')).distinct('booking_id')
    
    user_id = request.user.id
    context = {
        'all_booklist' : all_booklist,
        'user_id' : user_id,
    }



    return render(request, 'user/trackbookinglist.html', context)

@login_required(login_url='/')
@permission_required('user.add_booking', login_url='/index/')
# แอดมินเข้าไม่ได้
def booking(request, rm_id): #func called by booking.html
    context = dict()
    BookRoomFormSet = formset_factory(BookRoomForm)
    room = Room.objects.get(pk=rm_id)
    
    
    # data = {
    #         'formset-0-raw': 'my raw field string',
    #         'formset-INITIAL_FORMS': 1,
    #         'formset-TOTAL_FORMS': 2,
    #         }
    if request.method == 'POST':
        if 'normalBooking' in request.POST:
            formset = BookRoomFormSet(request.POST,form_kwargs={'rm': rm_id})
            form = BookRoomDescriptionForm(request.POST)
            rangeBookingForm = RangeBookingForm()
            print(request.POST.get('bookdate'))
            if formset.is_valid() and form.is_valid():
                
                booking = Booking.objects.create(
                    description = form.cleaned_data['description'],
                    user_id = request.user
                )
                booking.save()
                bookid = booking.id
                for eachForm in formset:
                    # print(eachForm.cleaned_data['start_time'])
                    booking_list = Booking_list.objects.create(                      
                        start_time = eachForm.cleaned_data['start_time'],
                        end_time = eachForm.cleaned_data['end_time'],
                        bookdate = eachForm.cleaned_data['bookdate'],
                        booking_id = booking,
                        room_id = Room.objects.get(id=rm_id)  
                    )
                    
                    booking_list.save()
    # ramonzii ============================================================================================
                if request.user.groups.filter(name ='student').exists():
                    student = Booking_student.objects.create(    
                        booking_id_id = bookid
                    )
                    student.save()
                elif request.user.groups.filter(name ='teacher').exists():
                    teacher = Booking_teacher.objects.create(
                        booking_id_id = bookid
                    )
                    teacher.save()
                    update = Booking.objects.get(pk=bookid)
                    update.status = '2'
                    update.save()
                
                elif request.user.groups.filter(name ='staff').exists():
                    staff = Booking_staff.objects.create(
                        booking_id_id = bookid
                        
                    )
                    staff.save()
                    update = Booking.objects.get(pk=bookid)
                    update.status = '2'
                    update.save()
    # ramonzii ============================================================================================
                
                return redirect('index')


        elif 'rangeBooking' in request.POST:
            rangeBookingForm = RangeBookingForm(request.POST, room=rm_id)
            formset = BookRoomFormSet(form_kwargs={'rm': rm_id})
            form = BookRoomDescriptionForm()
            if rangeBookingForm.is_valid():   
                fromDate = rangeBookingForm.cleaned_data['fromDate'] # start date
                toDate = rangeBookingForm.cleaned_data['toDate']  # end date

                fromTime = rangeBookingForm.cleaned_data['fromTime']
                toTime = rangeBookingForm.cleaned_data['toTime']
                
                delta = toDate - fromDate # as timedelta
                
                booking = Booking.objects.create(
                        description = rangeBookingForm.cleaned_data['description'],
                        user_id = request.user
                    )
                booking.save()
                bookid = booking.id
                for i in range(delta.days + 1):
                    day = fromDate + timedelta(days=i)
                    
                    
                    
                    booking_list = Booking_list.objects.create(                      
                        start_time = fromTime,
                        end_time = toTime,
                        bookdate = day,
                        booking_id = booking,
                        room_id = Room.objects.get(id=rm_id)   
                    )               
                    booking_list.save()
                    # ramonzii ============================================================================================
                if request.user.groups.filter(name ='student').exists():
                    student = Booking_student.objects.create(    
                        booking_id_id = bookid
                    )
                    student.save()
                elif request.user.groups.filter(name ='teacher').exists():
                    teacher = Booking_teacher.objects.create(
                        booking_id_id = bookid
                    )
                    teacher.save()
                    update = Booking.objects.get(pk=bookid)
                    update.status = '2'
                    update.save()
                
                elif request.user.groups.filter(name ='staff').exists():
                    staff = Booking_staff.objects.create(
                        booking_id_id = bookid
                        
                    )
                    staff.save()
                    update = Booking.objects.get(pk=bookid)
                    update.status = '2'
                    update.save()
    # ramonzii ============================================================================================
                return redirect('index')
                 
    else:
        formset = BookRoomFormSet(form_kwargs={'rm': rm_id})
        form = BookRoomDescriptionForm()
        rangeBookingForm = RangeBookingForm()
        
        
    # formset = BookRoomFormSet()
    # form = BookRoomDescriptionForm()
    # rangeBookingForm = RangeBookingForm()
    
    context['formset'] = formset
    # context['data'] = data
    context['form'] = form
    context['rm_id'] = rm_id
    context['rangeBookingForm'] = rangeBookingForm
    context['room'] = room

    return render(request, 'user/booking.html', context)



# เข้าได้ทุกคน
@login_required(login_url='/')
def profile(request):
    context = {}

    try:
      
        user_id = request.user.id
        user = request.user
        student = Student.objects.get(user_id__exact=user_id)
        list = Booking.objects.filter(user_id=user_id).count()
        accept = Booking.objects.filter(user_id=user_id, status='2').count()
        
       
        context['student'] = student
        context['list'] = list
        context['accept'] = accept
      


    except ObjectDoesNotExist:
        student = None

    if request.user.groups.filter(name ='student').exists():
       context['group'] = 'นักศึกษา'
    elif request.user.groups.filter(name ='teacher').exists():
       context['group'] = 'อาจารย์'
    elif request.user.groups.filter(name ='extra staff').exists():
       context['group'] = 'เจ้าหน้าที่สถานที่'
    elif request.user.groups.filter(name ='staff').exists():
       context['group'] = 'บุคลากร'
    else: 
       context['group'] = 'ผู้ดูแลระบบ'


    
    if request.method == 'POST':
        if 'submitpass' in request.POST:
            username = request.user.id
            user = User.objects.get(id__exact=username)
            password1 = request.POST.get('pass1')
            password2 = request.POST.get('pass2')
         
            if password1 == password2:
                user.set_password(password1)
                user.save()

                logout(request)
                return redirect('my_login')
            else:
                    context['error'] = 'รหัสผ่านไม่ตรงกัน'
           
        elif 'submitname' in request.POST:
            user.first_name = request.POST.get('fname')
            user.last_name = request.POST.get('lname')
            user.save()
            context['success'] = 'แก้ไขข้อมูลสำเร็จ'
        

     
         

    return render(request, 'user/profile.html', context)
# ทุกคน
@login_required(login_url='/')
def bookcheck(request, rm_id):
    room = Room.objects.get(pk=rm_id)
    # all_booklist = Booking_list.objects.all()  
    all_booklist = Booking_list.objects.filter(~Q(booking_id__status ='1') & ~Q(booking_id__status ='3')).order_by('bookdate')
    context = {
        'all_booklist' : all_booklist,
        'room' : room,


    }
    return render(request, 'user/bookcheck.html', context)

# def add(request):
#     context = dict()
#     type = Room_type.objects.all()
#     context['type'] = type

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         opentime = request.POST.get('st_time')
#         closetime = request.POST.get('ed_time')
#         capacity = request.POST.get('cap')
#         roomType = request.POST.get('typeselect')


#         try:
#             room = Room.objects.get(name=request.POST.get('name'))
#         except ObjectDoesNotExist:
#             room = None

#         if room:
#             context['error'] = 'ห้องซ้ำ'
#             return render(request, 'user/addroom.html', context=context)     
#         else:
#             room = Room.objects.create(
#             name = name,
#             start_time = opentime,
#             end_time = closetime,
#             capacity = capacity,
#             room_type = Room_type.objects.get(pk=roomType)

#             )
#             room.save()
#             return redirect('index')
    
#     return render(request, 'user/addroom.html', context=context)

# แอดมิน
@login_required(login_url='/')
@permission_required('user.add_room', login_url='/index/')
def add(request):
    context = dict()

    
    if request.method == 'POST':
        form = AddRoomForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            capacity = request.POST.get('capacity')
            room_type = request.POST.get('room_type')


            # try:
            #     room = Room.objects.get(name=request.POST.get('name'))
            # except ObjectDoesNotExist:
            #     room = None

            # if room:
            #     context['error'] = 'ห้องซ้ำ'
            #     context['form'] = AddRoomForm()
            #     # return render(request, 'user/addroom.html', context=context)     
            # else:
            room = Room.objects.create(
            name = name,
            start_time = start_time,
            end_time = end_time,
            capacity = capacity,
            room_type = Room_type.objects.get(pk=room_type)
            )
            room.save()
            return redirect('index')
            
        
    else:
        form = AddRoomForm()
    return render(request, 'user/addroom.html', {'form': form})
# แอดมิน
@login_required(login_url='/')
@permission_required('user.change_room', login_url='/index/')
def edit(request, rm_id):
    context = {}
    allroom = Room.objects.all()
    room = Room.objects.get(pk=rm_id)
    type = Room_type.objects.all()
    

    if request.method == 'POST':     
        
        for all in allroom:
            if all.name == request.POST.get('name') and room.name != request.POST.get('name'):
                print('not equal')
                context['error'] = "ห้องซ้ำ"

        if room.name == request.POST.get('name'):
            print('equal')
            room.name = request.POST.get('name')
            room.start_time = request.POST.get('st_time')
            room.end_time = request.POST.get('ed_time')
            room.capacity = request.POST.get('cap')
            room.room_type_id = request.POST.get('type')
            room.save()

            return redirect('index')

        else:
            print('ไม่ซ้ำ')
            room.name = request.POST.get('name')
            room.start_time = request.POST.get('st_time')
            room.end_time = request.POST.get('ed_time')
            room.capacity = request.POST.get('cap')
            room.room_type_id = request.POST.get('type')
            room.save()
            return redirect('index')

    context['room'] = room
    context['room_id'] = rm_id
    context['type'] = type


    return render(request, 'user/editroom.html', context=context)

# นักศึกษา
@login_required(login_url='/')
@permission_required('user.add_booking_student', login_url='/index/')
def tracking(request, bl_id):

    listno = Booking_list.objects.filter(list_no=bl_id).values_list('booking_id_id')
    booking = Booking.objects.filter(id__in = Subquery(listno)).values_list('id')
    booking_st = Booking_student.objects.filter(booking_id__in =  Subquery(booking))
    all_book = Booking_list.objects.all().order_by('bookdate')
    

    book_list = Booking_list.objects.get(pk=bl_id)
    print(booking_st)
    student = Student.objects.all()

    book_id = Booking.objects.filter()

    context = {
        'book_list': book_list,
        'student': student,
        'booking_st': booking_st,
        'all_book': all_book,
    }
    return render(request, 'user/track.html', context)


# teacher extrastaff
@login_required(login_url='/')
@permission_required('user.change_booking_student', login_url='/index/')
def accept(request, bl_id):

    student = Student.objects.all()
    book_list = Booking_list.objects.get(pk=bl_id)
    book = Booking.objects.get(pk=book_list.booking_id.id)
    stu = Booking_student.objects.get(booking_id=book.id)
    all_book = Booking_list.objects.all()


    context = {}
    context['book_list'] = book_list
    context['student'] = student
    context['bl_id'] = bl_id
    context['all_book'] = all_book

    now = str(datetime.now())

    try:
        user_id = request.user.id
        teacher = Teacher.objects.filter(user_id_id=user_id).values_list('id')
        staff = Staff.objects.filter(user_id_id=user_id).values_list('id')

    except ObjectDoesNotExist:
        teacher = None
        staff = None

    
    
    if request.user.groups.filter(name ='teacher').exists():   #ปุ่มอนุมัติของอาจารย์
        if 'allow' in request.POST:
            stu.teacher_result = '2'
            stu.teacher_date = now
            stu.teacher_user_id_id = teacher
            
            stu.save()
            if stu.teacher_result == '2' and stu.staff_result == '2':
                book.status = '2'
                book.save()
                print('===============1==================')
        
            return redirect('bookinglistall')

        elif 'deny' in request.POST:
            stu.teacher_result = '3'
            stu.teacher_user_id_id = teacher
            stu.save()
            if stu.teacher_result == '3':
                stu.staff_result = '3'
                stu.save()
                book.status = '3'
                book.save()
                print('================2=================')


            return redirect('bookinglistall')

    elif request.user.groups.filter(name ='staff').exists():    #ปุ่มอนุมัติของบุคคลากร
        if 'allow' in request.POST:
            stu.staff_result = '2'
            stu.staff_date = now
            stu.staff_user_id_id = staff
            stu.save()
            if stu.teacher_result == '2' and stu.staff_result == '2':
                book.status = '2'
                book.save()
                print('===============3==================')
  
            return redirect('bookinglistall')

        elif 'deny' in request.POST:
            stu.staff_result = '3'
            stu.staff_user_id_id = staff

            stu.save()
            if stu.staff_result == '3':
                stu.teacher_result = '3'
                stu.save()
                book.status = '3'
                book.save()
                print('================4=================')


            return redirect('bookinglistall')
    
        

    return render(request, 'user/accept.html', context)


#  admin
@login_required(login_url='/')
@permission_required('user.delete_room', login_url='/index/')
def delete(request, rm_id):
    room = Room.objects.get(pk=rm_id)
    room.delete()
    return redirect('index')

# student
@login_required(login_url='/')
@permission_required('user.delete_booking_student', login_url='/index/')
def track_delete(request, bl_id):
    listno = Booking_list.objects.filter(list_no=bl_id).values_list('booking_id_id')  #ดึงรายการจองที่มีlist_no เท่ากับค่าที่รับมา แล้วselect  booking_id_id
    booking = Booking.objects.filter(id__in = Subquery(listno))  # ดึงข้อมูลการจองที่มีid เท่ากับ id ของรายการจอง
    booking.delete()                                               #ลบ
    return redirect('trackbookinglist')

# ยกเว้นแอดมิน ค่อยไปแก้ในหน้าย่อย list base template
@login_required(login_url='/')
@permission_required('user.add_booking', login_url='/index/')
def mybookinglist(request):
    search_txt = request.POST.get('search','')

    
    all_booklist = Booking_list.objects.filter(
            Q(room_id__name__icontains= search_txt) & ~Q(booking_id__status ='1')).distinct('booking_id') #ดึงรายการจองย่อยที่ตรงกับการค้นหา และไม่มีสถานะเป็น 'รอการอนุมัติ' และไม่ซ้ำกัน
        
    user_id = request.user.id
    context = {
        'all_booklist' : all_booklist,
        'user_id' : user_id
     
    }
    return render(request, 'user/mybookinglist.html', context)


@login_required(login_url='/')
@permission_required('user.view_booking', login_url='/index/')

def history(request):
    try:
        user = User.objects.all()                                           #ดึงข้อมูลผู้ใช้ทั้งหมด
        st_booking = Booking_student.objects.all()                          #ดึงข้อมูลการจองของนักศึกษา
        search_txt = request.POST.get('search','')
        all_booklist = Booking_list.objects.filter(
            Q(room_id__name__icontains= search_txt) & ~Q(booking_id__status ='1')).distinct('booking_id')  #ดึงรายการจองย่อยที่ตรงกับการค้นหา และไม่มีสถานะเป็น 'รอการอนุมัติ' และไม่ซ้ำกัน
        teacher =Teacher.objects.all()                                      #ดึงข้อมูลอาจารย์
        staff =Staff.objects.all()                                          #ดึงข้อมูลเจ้าหน้าที่

    except ObjectDoesNotExist:
        st_booking = None  
        teacher = None
        staff = None

    context = {
            'all_booklist' : all_booklist,
            'st_booking' : st_booking,
            'user' : user,
            'teacher' : teacher,
            'staff' : staff,
    }

    return render(request, 'user/history.html', context)


@login_required(login_url='/')
@permission_required('user.view_booking', login_url='/index/')

def history_teacher(request):
    user = User.objects.all()                                           #ดึงข้อมูลผู้ใช้ทั้งหมด
    teacher_book = Booking_teacher.objects.all()                        #ดึงข้อมูลการจองของอาจารย์
    search_txt = request.POST.get('search','')                          #get request มาเพื่อเอาไปsearch
    all_booklist = Booking_list.objects.filter(
        room_id__name__icontains= search_txt ).distinct('booking_id')   #ดึงรายการจองโดยเลือกห้องที่มีชื่อตามการค้นหา และ ไม่เอาห้องซ้ำ
   
        


    context = {
            'all_booklist' : all_booklist,
            'teacher_book' : teacher_book,
            'user' : user,
    }

    return render(request, 'user/historyteacher.html', context)

@login_required(login_url='/')
@permission_required('user.view_booking', login_url='/index/')

def history_staff(request):
 
    user = User.objects.all()                                               #ดึงข้อมูลผู้ใช้ทั้งหมด
    staff_book = Booking_staff.objects.all()                                #ดึงข้อมูลการจองของบุคลากร
    search_txt = request.POST.get('search','')                              #get request มาเพื่อเอาไปsearch
    all_booklist = Booking_list.objects.filter(
        room_id__name__icontains= search_txt ).distinct('booking_id')       #ดึงรายการจองโดยเลือกห้องที่มีชื่อตามการค้นหา และ ไม่เอาห้องซ้ำ
   
        


    context = {
            'all_booklist' : all_booklist,
            'staff_book' : staff_book,
            'user' : user,
    }

    return render(request, 'user/historystaff.html', context)


# ทุกคน
@login_required(login_url='/')
def detail(request, bl_id):
    
    student = Student.objects.all()                         #ดึงข้อมูลนักเรียน จะเอาพวกรหัส ชั้นปี
    book_list = Booking_list.objects.get(pk=bl_id)          #ดึงรายการจองย่อยที่มีidตรงกับที่ส่งมา เพื่อจะได้แสดงรายการจองในหน้าdetail
    all_book = Booking_list.objects.all()                   #ดึงรายการจองย่อยทั้งหมด เพื่อไปเช็ควัน เวลา ของแต่ละรายการจองนั้นๆ เอาวันที่ เวลาของbooking นั้นๆ

    context = {}
    context['book_list'] = book_list
    context['student'] = student
    context['bl_id'] = bl_id
    context['all_book'] = all_book

   

    return render(request, 'user/detail.html', context=context)

from builtins import object
from tkinter import Widget

from django import forms
from user.models import Room_type, Booking_list, Booking
from user.models import Room
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta


class EditForm(forms.Form):
    name = forms.CharField(max_length=255)
    date = forms.DateField()
    
    
class TimeInput(forms.TimeInput):
    input_type = 'time'    
    
class DateInput(forms.DateInput):
    input_type = 'date' 
    
class AddRoomForm(forms.Form): #form add, book
    roomType = Room_type.objects.all()
    roomTypeChoices = [('', 'select')]
    for i in roomType:
        roomTypeChoices.append((i.id, i.name))
        
    name = forms.CharField(label='ชื่อห้อง' ,max_length=30, required=True)

    start_time = forms.TimeField(label='เวลาเปิด' ,widget=TimeInput, required=True)
    end_time = forms.TimeField(label='เวลาปิด' ,widget=TimeInput, required=True)
    capacity = forms.IntegerField(label='ความจุห้อง' ,required=True)
    room_type = forms.ChoiceField(label='ประเภทห้อง' ,widget=forms.Select, choices=roomTypeChoices)

    name.widget.attrs.update({'class' : 'form-control'})
    room_type.widget.attrs.update({'class' : 'form-control'})
    start_time.widget.attrs.update({'class' : 'form-control'})
    end_time.widget.attrs.update({'class' : 'form-control'})
    capacity.widget.attrs.update({'class' : 'form-control'})
    
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        
        try:
            room = Room.objects.get(name=name)
            # room = Room.objects.get(name=request.POST.get('name'))

        except ObjectDoesNotExist:
            room = None

        if room:
            # raise ValidationError(
            #     'ห้องชื่อ %(name)s มีอยู่ในระบบแล้ว', code='invalid', params={'roomName' : name}
            errorMsg = 'ห้องชื่อนี้มีอยู่ในระบบแล้ว'
            self.add_error('name', errorMsg)
            # )

class BookRoomDescriptionForm(forms.Form):
    description = forms.CharField(label='เหตุผลในการจอง', widget=forms.Textarea, required=True)
    def clean(self):
        cleaned_data = super().clean()
        
    description.widget.attrs.update({'class' : 'form-control'})
                
            
class BookRoomForm(forms.Form): #for booking_list
    def __init__(self, *args, rm, **kwargs):
        self.rm = rm
        super().__init__(*args, **kwargs)
        
    
    
    bookdate = forms.DateField(label='วันที่', widget=DateInput, required=True)
    start_time = forms.TimeField(label='จองเวลา' ,widget=TimeInput, required=True)
    end_time = forms.TimeField(label='ถึงเวลา' ,widget=TimeInput, required=True)
    
    
    bookdate.widget.attrs.update({'class' : 'form-control', 'max':'3000-12-31'})
    start_time.widget.attrs.update({'class' : 'form-control'})
    end_time.widget.attrs.update({'class' : 'form-control'})
    

    def clean(self):
        cleaned_data = super().clean()
        allBookingList = Booking_list.objects.filter(room_id__id=self.rm)
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        bookdate = cleaned_data.get('bookdate')
        state = 1
        roomErr = ''
        print(self.rm)
        
        for each in allBookingList:
            if (Booking.objects.get(id=each.booking_id.id).st == '2' and (start_time >= each.start_time and start_time <= each.end_time) or 
                (end_time >= each.start_time and end_time <= each.end_time)) and each.bookdate == bookdate:
                state = 0  
                roomErr = each.room_id.name
                break
            
        # room already booked
        if state == 0:
            errorMsg = 'ห้อง ' + roomErr + ' ถูกจองไปแล้ว'
            self.add_error('bookdate', errorMsg)
            print('ห้อง', roomErr, 'ถูกจองไปแล้ว')
                          
                          
        # time-error
        if start_time > end_time:
            errorMsg = 'เวลาไม่ถูกต้อง'
            self.add_error('start_time', errorMsg)
            print('เวลาไม่ถูกต้อง')
        
        room = Room.objects.get(id=self.rm)
        if not (start_time >= room.start_time and end_time <= room.end_time):
            errorMsg = 'เวลาที่จองไม่อยู่ในเวลาให้บริการของห้อง'
            self.add_error('start_time', errorMsg)
            print('เวลาที่จองไม่อยู่ในเวลาให้บริการของห้อง')
            
        
            
            
            
class RangeBookingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
    
    fromDate = forms.DateField(label='ตั้งแต่', widget=DateInput, required=True)
    toDate = forms.DateField(label='จนถึง', widget=DateInput, required=True)
    fromTime = forms.TimeField(label='จองเวลา' ,widget=TimeInput, required=True)
    toTime = forms.TimeField(label='ถึงเวลา' ,widget=TimeInput, required=True)
    description = forms.CharField(label='เหตุผลในการจอง', widget=forms.Textarea, required=True)
    
    fromDate.widget.attrs.update({'class' : 'form-control', 'max':'3000-12-31'})
    toDate.widget.attrs.update({'class' : 'form-control', 'max':'3000-12-31'})
    fromTime.widget.attrs.update({'class' : 'form-control'})
    toTime.widget.attrs.update({'class' : 'form-control'})
    description.widget.attrs.update({'class' : 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        allBookingList = Booking_list.objects.filter(room_id__id=self._room)
        fromDate = cleaned_data.get('fromDate')
        toDate = cleaned_data.get('toDate')
        fromTime = cleaned_data.get('fromTime')
        toTime = cleaned_data.get('toTime')
        state = 1
        
        
        # date-error
        if fromDate > toDate:
            errorMsg = 'วันที่ไม่ถูกต้อง'
            self.add_error('fromDate', errorMsg)
            print('date-error')
            
        #time-error
        if fromTime > toTime:
            errorMsg = 'เวลาไม่ถูกต้อง'
            self.add_error('fromTime', errorMsg)
            print('Time-error')
            
        delta = toDate - fromDate # as timedelta
  
        for i in range(delta.days + 1):
            day = fromDate + timedelta(days=i)
            for each in allBookingList:  
                if (Booking.objects.get(id=each.booking_id.id).st == '2' and (fromTime >= each.start_time and fromTime <= each.end_time) or 
                    (toTime >= each.start_time and toTime <= each.end_time)) and each.bookdate == day:
                    state = 0  
                    break
                
        # room already booked
        if state == 0:
            errorMsg = 'มีห้องในช่วงถูกจองไปแล้ว'
            self.add_error('fromDate', errorMsg)
            print('มีห้องในช่วงถูกจองไปแล้ว')
            
            
         # room already booked
        room = Room.objects.get(id=self._room)
        if not (fromTime >= room.start_time and toTime <= room.end_time):
            errorMsg = 'เวลาที่จองไม่อยู่ในเวลาให้บริการของห้อง'
            self.add_error('fromDate', errorMsg)
            print('เวลาที่จองไม่อยู่ในเวลาให้บริการของห้อง')    
            
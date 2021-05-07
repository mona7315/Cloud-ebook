from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from user.models import Student,UserRole,Teacher,Staff

# Create your views here.

def my_login(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password'
            return render(request, 'guest/login.html', context=context)
    
    return render(request, 'guest/login.html', context=context)



def register(request):
    context = dict()

    if request.method == 'POST':
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        select = request.POST.get('role')

        print(select)


        try:
            user = User.objects.get(username=request.POST.get('username'))
           
           
            
        except ObjectDoesNotExist:
            user = None

        if user:
        
            context['error_user'] = 'This username is taken. Try another.'
            context['fname'] = request.POST.get('firstname')
            context['lname'] = request.POST.get('lastname')
            context['email'] = request.POST.get('email')
            context['user'] = request.POST.get('username')

            return render(request, 'guest/login.html', context)

        if password == repassword:
            user = User.objects.create_user(request.POST.get('username'), request.POST.get('email'), request.POST.get('password'))
            user.first_name = request.POST.get('firstname')
            user.last_name = request.POST.get('lastname')

            if select == '1':
                group = Group.objects.get(name='student')
                user.groups.add(group)
            elif select == '2':
                group = Group.objects.get(name='teacher')
                user.groups.add(group)
            elif select == '3':
                group = Group.objects.get(name='staff')
                user.groups.add(group)
            user.save()
            print(user.id)
            id = user.id


            if select == '1':
                student = Student.objects.create(
                    stu_id = request.POST.get('st_id'),
                    year = request.POST.get('year'),
                    major = request.POST.get('major'),
                    user_id_id = id
                )
                student.save()
                print('ok i get it1')
            elif select == '2':
                teacher = Teacher.objects.create(
                    user_id_id = id,
                    rank = request.POST.get('rank')
                )
                teacher.save()
                print('ok i get it2')
            elif select == '3':
                staff = Staff.objects.create(
                    user_id_id = id,
                    position = request.POST.get('position')
                )
                staff.save()

                print('ok i get it3')

            return redirect('my_login')
        else:
            context['error_pass'] = 'Password not match.'
            context['fname'] = request.POST.get('firstname')
            context['lname'] = request.POST.get('lastname')
            context['email'] = request.POST.get('email')
            context['user'] = request.POST.get('username')
 


            return render(request, 'guest/login.html', context=context)
     
    return render(request, 'guest/login.html')

def my_logout(request):
    logout(request)
    return redirect('my_login')
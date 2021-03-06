from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import loader
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from user.forms import SignUpForm, StudentEditForm, AdminSignUpForm
from django.contrib.auth.models import User
from user.models import AbstractUser, Student, Seller, FixedSeller, WalkingSeller, PaymentMethod


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid() and form.pass_is_valid(): # should show me pass dont match
            account_type = form.cleaned_data['account_type']
            duser = User.objects.create_user(form.cleaned_data['email'],
                                                  form.cleaned_data['email'],
                                                  form.cleaned_data['password'])
            authuser = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            login(request, authuser)
            auser = AbstractUser(user=duser, fullname=form.cleaned_data['fullname'], account_type=int(account_type))
            auser.save()
            if account_type is '1':
                auser.avatar = '/static/app/img/AvatarEstudiante' + str(int(form.cleaned_data['student_avatar']) + 1) + ".png"
                auser.save()
                student = Student(user=auser)
                student.save()
                return redirect('index')
            # Here if seller
            auser.avatar = '/static/app/img/AvatarVendedor' + str(int(form.cleaned_data['seller_avatar']) + 1) + ".png"
            auser.save()
            seller = Seller()
            seller.user = auser
            seller.save()
            for pay in form.cleaned_data['pay_methods']:
                seller.payment_methods.add(pay)
            seller.save()
            if account_type is '2':
                walking_seller = WalkingSeller(super_seller=seller)
                walking_seller.save()

            elif account_type is '3':
                fixed_seller = FixedSeller(super_seller=seller,
                                           start_hour=form.cleaned_data['start_hour'],
                                           end_hour=form.cleaned_data['end_hour'],
                                           address=form.cleaned_data['address'])
                fixed_seller.save()
            return redirect('index')
    else:
        form = SignUpForm(initial={'pay_methods': [PaymentMethod.objects.all().values_list('name', flat=True)[0]]})
    return render(request, 'user/signup.html', {'form': form})


def admin_signup(request):
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid() and form.pass_is_valid(): # should show me pass dont match
            duser = User.objects.create_superuser(form.cleaned_data['email'],
                                                  form.cleaned_data['email'],
                                                  form.cleaned_data['password'])
            auser = AbstractUser(user=duser, fullname=form.cleaned_data['fullname'], account_type=4)
            auser.save()
            # finish user creation
            # start login
            authuser = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            login(request, authuser)
            return redirect('index')
    else:
        form = AdminSignUpForm()
    return render(request, 'user/admin_signup.html', {'form': form})


def edit_student(request, pkid):
    try:
        duser = User.objects.get(pk=pkid)
        auser = AbstractUser.objects.get(user=duser)
    except ObjectDoesNotExist:
        return render(request, 'not-found.html')
    if request.method == 'POST':
        form = StudentEditForm(request.POST)

        if form.is_valid() and form.pass_is_valid():  # should show me pass dont match
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            fullname = form.cleaned_data['fullname']
            avatar = form.cleaned_data['student_avatar']
            if avatar is not "":
                auser.avatar = '/static/app/img/AvatarEstudiante' + str(int(avatar) + 1) + ".png"
                auser.save()
            if fullname is not "":
                print("edited fullname")
                auser.fullname = fullname
                auser.save()
            if email is not "":
                print("edited mail")
                duser.email = email
                duser.username = email
                duser.save()
            if password is not "":
                print("edited pass")
                duser.set_password(password)
                duser.save()
            return redirect('index')
    else:
        if request.user.is_authenticated():
            logged_auser = AbstractUser.objects.get(user=request.user)
            if (request.user.id == int(pkid) and auser.account_type is 1) or logged_auser.account_type is 4:
                form = StudentEditForm(initial={'email':duser.email,
                                                'fullname':auser.fullname,})
                return render(request, 'user/student-edit.html', {'form': form, 'pkid': pkid})
    return render(request, 'not-found.html')


def delete_student(request, pkid):
    try:
        duser = User.objects.get(pk=pkid)
        auser = AbstractUser.objects.get(user=duser)
        student = Student.objects.get(user=auser)
    except ObjectDoesNotExist:
        return render(request, 'not-found.html')
    if request.user.is_authenticated():
        logged_user = AbstractUser.objects.get(user=request.user)
        if logged_user.account_type is 4:
            # admin
            student.delete()
            auser.delete()
            duser.delete()
            return redirect('index')
    return render(request, 'not-found.html')





from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import account_creation, account_validate
from .models import User as _User, Employee as _Employee, Admin as _Admin, Request as _Request, Submissions as _Submissions

import base64

# Create your views here.

def landing(request):
    return render(request, 'artTubeApp/index.html')

def login(request):
    if request.method == 'GET':
        form = account_validate()
    elif request.method == 'POST':
        form = account_validate(request.POST)
        if form.is_valid():
            _email = form.cleaned_data.get('email')
            _password = form.cleaned_data.get('pwd')

            users = _User.objects.get(email=_email)

            if not users:
                form.add_error('email', 'Email is not associated with an account. Please create a new account or try another email.')
            elif check_password(_password, users.password):
                next_page = request.POST.get('next') or request.GET.get('next') or '/'
                request.session['current_user'] = users.email
                return redirect(next_page)
            else:
                form.add_error('email', 'Bad login. Try again.')

            
    return render(request, 'artTubeApp/login.html', {'form': form})

def logout(request):
    if request.session.get('current_user'):
        del request.session['current_user']
        return render(request, 'artTubeApp/logout.html')
    else:
        return redirect('home')

def signup(request):
    if request.method == "POST":
        form = account_creation(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            pwd = make_password(form.cleaned_data.get('pwd'))

            if _User.objects.filter(username=username).exists():
                form.add_error('username', 'Username has been taken.')
            if _User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already registered.')
            else:
                _User.objects.create(
                    username=username,
                    email=email,
                    password=pwd,
                    admin_approve=0,
                    locked=0,
                    number_2fa=0
                )
                return redirect('login')
    else:
        form = account_creation()
    return render(request, 'artTubeApp/signup.html', {'form': form})

def emp_dashboard(request):
    if request.session.get('current_user'):
        return render(request, 'artTubeApp/emp_dash.html')
    else:
        return redirect('/login?next=/employee/')

def admin_dashboard(request):
    if request.session.get('current_user'):
        return render(request, 'artTubeApp/admin_dash.html')
    else:
        return redirect('/login?next=/admin/')

def submit_request_page(request):
    if request.session.get('current_user'):
        return render(request, 'artTubeApp/request.html')
    else:
        return redirect('/login?next=/canvas/request/')

def studio_page(request):
    if request.session.get('current_user'):
        _email = request.session.get('current_user')
        if _Request.objects.filter(email=_email):
            requests = _Request.objects.get(email=_email)
            imgs = [r.img for r in requests]
        else:
            imgs = []
        if len(imgs) == 0:
            imgs = "No requests pending..."
        return render(request, 'artTubeApp/studio.html', {'requests': imgs})
    else:
        return redirect('/login?next=/canvas/')

def creator_studio(request):
    print("null")

def gallery(request):
    if request.method == 'GET':
        submissions = list(_Submissions.objects.values(
            "img",
            "img_type",
            "img_title",
            "img_desc",
        ))

        #convert LONGBLOB to image
        for submission in submissions:
            binary_image = base64.b64encode(submission["img"]).decode("ascii")
            submission["img"] = (
                f"data:{submission['img_type']};base64,{binary_image}"
            )
        
        return render(request, 'artTubeApp/gallery.html', {'submissions': submissions})
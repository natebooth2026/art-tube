from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import account_creation, account_validate
from .models import User as _User

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

            if not _User.objects.filter(email=_email).exists():
                form.add_error('email', 'Email is not associated with an account. Please create a new account or try another email.')
            elif check_password(_email, users.email) and check_password(_password, users.password):
                next_page = request.POST.get('next') or request.GET.get('next')
                request.session['current_user'] = _User.username
                return redirect(next_page or 'index')
            else:
                form.add_error('email', 'Bad login. Try again.')

            
    return render(request, 'artTubeApp/login.html', {'form': form})

def signup(request):
    if request.method == "POST":
        form = account_creation(request.POST)
        if form.is_valid():
            email = make_password(form.cleaned_data.get('email'))
            username = make_password(form.cleaned_data.get('username'))
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
                    locked=0
                )
                return redirect('login')
    else:
        form = account_creation()
    return render(request, 'artTubeApp/signup.html', {'form': form})

@login_required
def submit_request_page(request):
    return render(request, 'artTubeApp/request.html')

@login_required 
def creator_studio(request):
    print("null")

def emp_dashboard(request):
    print("null")
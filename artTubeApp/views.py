from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as _login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.

def landing(request):
    return render(request, 'artTubeApp/index.html')

def login(request):
    if request.method == 'GET':
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                _login(request, user)

                next_page = request.POST.get('next') or request.GET.get('next')

                if next_page and url_has_allowed_host_and_scheme(url=next_page, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    return redirect(next_page)
    return render(request, 'artTubeApp/login.html', {'form': form})

@login_required
def submit_request_page(request):
    return render(request, 'artTubeApp/request.html')
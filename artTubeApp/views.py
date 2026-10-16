from base64 import b64encode #for image decoding
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import account_creation, account_validate
from .models import User as _User, Employee as _Employee, Admin as _Admin, Request as _Request, Submissions as _Submissions, Category as _Category

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
        email = request.session.get('current_user')
        is_emp = False
        if _Employee.objects.filter(email=email):
            is_emp = True
        return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
    else:
        return redirect('/login?next=/employee/')

def admin_dashboard(request):
    if request.session.get('current_user'):
        email = request.session.get('current_user')
        is_admin = False
        if _Admin.objects.filter(email=email):
            is_admin = True
        return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
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
        if _Request.objects.filter(email=_email).exists():
            imgs = _Request.objects.filter(email=_email)
            img_categories = [_Category.objects.get(id=i.img_category.id).name for i in imgs]
        else:
            imgs = []

        if _Submissions.objects.filter(email=_email).exists():
            sub_imgs = _Submissions.objects.filter(email=_email)
            sub_img_categories = [_Category.objects.get(id=s.approved_category.id).name for s in sub_imgs]
        else:
            sub_imgs = []
            sub_img_categories = []

        return render(request, 'artTubeApp/studio.html', {'requests': imgs, 'request_len': len(imgs), 'request_cat': img_categories, 
                                                          'pub_pieces': sub_imgs, 'pub_len': len(sub_imgs), 'pub_cat': sub_img_categories})
    else:
        return redirect('/login?next=/canvas/')

def request_view(request, id = -1):
    if id < 0 or not _Request.objects.filter(id=id).exists():
        return redirect('studio')
    else:
        return render(request, 'artTubeApp/studio_view.html', {'is_sub': False, 'item': _Request.objects.get(id=id), 'category': _Request.objects.get(id=id).img_category.name})

def sub_view(request, id = -1):
    if id < 0 or not _Submissions.objects.filter(id=id).exists():
        return redirect('studio')
    else:
        return render(request, 'artTubeApp/studio_view.html', {'is_sub': True, 'item': _Submissions.objects.get(id=id)})

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
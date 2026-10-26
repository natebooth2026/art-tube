from base64 import b64encode #for image decoding
from enum import Enum

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import timedelta, datetime, UTC

from .forms import account_creation, account_validate, sub_request_form, add_event, account_validate_emailMFA
from .models import User as _User, Employee as _Employee, Admin as _Admin, Request as _Request, Submissions as _Submissions, Category as _Category, Events as _Events
from .sanitize import sanitize_img

import secrets
from django.core.mail import send_mail


class LogType(Enum):
    NONE = -1
    ACCOUNT_LOGIN = 0
    ACCOUNT_LOGOUT = 1
    ACCOUNT_CREATE = 2
    EMPLOYEE_ACCESS = 3
    EMPLOYEE_EVENT_CREATE = 4
    EMPLOYEE_EVENT_MODIFY = 5
    EMPLOYEE_REQUEST_APPROVE = 6
    EMPLOYEE_REQUEST_DENY = 7
    ADMIN_ACCESS = 8
    ADMIN_REQUEST_APPROVE = 9
    ADMIN_REQUEST_DENY = 10
    ADMIN_SWITCH_ROLE = 11
    USER_SUBMIT_REQUEST = 12
    USER_ATTEMPT_REQUEST = 13
    USER_FAILED_REQUEST = 14
    USER_ACCESS_VIEW = 15
    USER_ACCESS_STUDIO = 16
    USER_CHANGE_SUBMISSION = 17
    EMPLOYEE_REVERT_APPROVE = 18
    ADMIN_REVERT_APPROVE = 19
    ACCOUNT_FAILED_LOGIN = 20
    ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT = 21
    ACCOUNT_FAILED_CREATE = 22
    EMPLOYEE_FAILED_CREATE = 23
    EMPLOYEE_FAILED_MODIFY = 24
    EMPLOYEE_FAILED_REQUEST_DECISION = 25
    EMPLOYEE_FAILED_ACCESS = 26
    USER_ATTEMPT_EMP_DASHBOARD = 27
    USER_ATTEMPT_ADMIN_PORTAL = 28

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

            users = _User.objects.filter(email=_email).first()
            if users is None:
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

            if _User.objects.filter(username=username).exists() and _User.objects.filter(email=email).exists():
                form.add_error('username', 'Username has been taken.')
                form.add_error('email', 'Email already registered.')
            elif _User.objects.filter(username=username).exists():
                    form.add_error('email', 'Email already registered.')
            elif _User.objects.filter(email=email).exists():
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
    is_emp = False
    if request.session.get('current_user'):
        email = request.session.get('current_user')
        if _Employee.objects.filter(email=email):
            is_emp = True
    else:
        return redirect('/login?next=/employee/')
    
    if request.method == 'GET':
        if(is_emp):
            code = f"{secrets.randbelow(1_000_000):06d}"
            request.session["employee_code"] = code
            #send email with code
            send_mail(
                "ArtTube Verification code",
                f"code is {code}",
                None,  # Uses DEFAULT_FROM_EMAIL if configured
                [email],
                fail_silently=False,
            )
            form = account_validate_emailMFA()
            return render(request, 'artTubeApp/validate_email_MFA.html', {'form': form})
        else:
            return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
    elif request.method == 'POST':
        form = account_validate_emailMFA(request.POST)
        if form.is_valid():
            email_code = form.cleaned_data.get('email_code')
            code = request.session.get("employee_code")
            #compare with code that was sent
            if email_code == code:
                return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
            else:
                is_emp = False
                return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})

def emp_events(request):
    if request.session.get('current_user'):
        _email = request.session.get('current_user')
        form = add_event()
        events = list(_Events.objects.values(
                    "event_title",
                    "event_start",
                    "event_end",
                ))
        #must be exployee to access employee dash
        if _Employee.objects.filter(email=_email).exists(): 
            if request.method == 'GET':
                return render(request, 'artTubeApp/emp_dash.html', {'events': events, 'form': form})
            if request.method == 'POST':
                form = add_event(request.POST)
                #user queries events
                if 'search-events' in request.POST:
                    query_title = request.POST.get('query')
                    if query_title:
                        form = add_event()
                        queried_events = _Events.objects.filter(event_title__icontains=query_title)
                        return render(request, 'artTubeApp/emp_dash.html', {'form': form, 'events': queried_events})
                    elif not query_title:
                        return redirect('employee')
                #user submits new event
                elif form.is_valid():
                    _event_title = form.cleaned_data.get('event_title')
                    _event_start = form.cleaned_data.get('event_start')
                    _event_end = form.cleaned_data.get('event_end')
                    if _Events.objects.filter(event_start__lt=_event_end, event_end__gt=_event_start).exists():
                        form.add_error('event_title', 'Event overlaps with other events')
                    elif _Events.objects.filter(event_title=_event_title).exists():
                        form.add_error('event_title', 'Event name unavailable')
                    elif _event_end < _event_start:
                        form.add_error('event_end', 'End date/time must come after start date/time')
                    else:
                        # create event entry
                        _Events.objects.create(
                            event_title=_event_title,
                            event_start= _event_start,
                            event_end=_event_end
                        )
                        form=add_event() #reset form
                        return render(request, 'artTubeApp/emp_dash.html', {'form': form, 'events': events, 'confirmation': 'Event successfully submitted!'})
                    return render(request, 'artTubeApp/emp_dash.html', {'form': form, 'events': events})
        else:
            #redirect to home page
            return redirect('/')
    else:
        return redirect('/login/?next=/employee/')

def admin_dashboard(request):
    is_admin = False
    if request.session.get('current_user'):
        email = request.session.get('current_user')
        if _Admin.objects.filter(email=email).exists(): #myst be an admin to access admin_dash
            is_admin = True
    else:
        return redirect('/login?next=/admin/')
    if request.method == 'GET':
            if(is_admin):
                code = f"{secrets.randbelow(1_000_000):06d}"
                request.session["employee_code"] = code
                #send email with code
                send_mail(
                    "ArtTube Verification code",
                    f"code is {code}",
                    None,  # Uses DEFAULT_FROM_EMAIL if configured
                    [email],
                    fail_silently=False,
                )
                form = account_validate_emailMFA()
                return render(request, 'artTubeApp/validate_email_MFA.html', {'form': form})
            else:
                return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
    elif request.method == 'POST':
        form = account_validate_emailMFA(request.POST)
        if form.is_valid():
            email_code = form.cleaned_data.get('email_code')
            code = request.session.get("employee_code")
            #compare with code that was sent
            if email_code == code:
                return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
            else:
                is_admin = False
                return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
            
def submit_request_page(request):
    if request.session.get('current_user'):
        last_req = _Request.objects.filter(email=request.session.get('current_user')).order_by('-time').first()
        if last_req and datetime.now(UTC) < (last_req.time + timedelta(hours=2)):
            request.session['request_allowed'] = False
            return redirect('/canvas/request/wait')
        else:
            request.session['request_allowed'] = True
        if request.method == "GET":
            form1 = sub_request_form()
            form2 = account_validate()
        elif request.method == "POST":
            form1 = sub_request_form(request.POST, request.FILES)
            form2 = account_validate(request.POST)

            if form2.is_valid():
                email = form2.cleaned_data.get('email')
                pwd = form2.cleaned_data.get('pwd')

                user = _User.objects.get(email=email)

                if not user:
                    form2.add_error('email', 'User not found. Try again.')
                else:
                    if user.email != request.session.get('current_user'):
                        form2.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                    elif not check_password(pwd, user.password):
                        form2.add_error('email', 'Incorrect email/password combination. Try again.')
                    else:
                        if form1.is_valid():
                            _img = form1.cleaned_data.get('img')
                            _title = form1.cleaned_data.get('title')
                            _desc = form1.cleaned_data.get('desc')
                            _category = form1.cleaned_data.get('category')

                            # file santiziation
                            try:
                                sanitize0, sanitize1 = sanitize_img(_img)
                                _img = sanitize0.read()
                                img_ext = sanitize1
                            except ValueError:
                                _img, img_ext = None

                            have_img = have_title = have_category = True

                            if not _img:
                                have_img = False
                                form1.add_error('img', 'Must provide a valid image file. Supported formats: .jpeg/.jpg, .png, .webp')
                            if not _title:
                                have_title = False
                                form1.add_error('title', 'Title is required.')
                            if not _Category.objects.filter(id=_category.id):
                                have_category = False
                                form1.add_error('category', 'Invalid category.')
                            if not request.session.get('request_allowed'):
                                return redirect('/canvas/request/wait')
                            if have_img and have_title and have_category:
                                _Request.objects.create(
                                    email=user,
                                    img=_img,
                                    img_type=img_ext,
                                    img_title=_title,
                                    img_desc=_desc,
                                    img_category=_category,
                                    admin_approve=user.admin_approve,
                                    denied=0,
                                    denial_reason=""
                                )
                                request.session['request_success'] = True
                                return redirect('/canvas/request/success')  
        return render(request, 'artTubeApp/studio_new_req.html', {'r_form': form1, 'v_form': form2})
    else:
        return redirect('/login?next=/canvas/request/')
    
def request_submitted(request):
    if request.session.get('current_user'):
        if request.session.get('request_success') == True:
            request.session['request_success'] = False
            return render(request, 'artTubeApp/studio_req_success.html')
        return redirect('/canvas/request')
    else:
        return redirect('/login?next=/canvas/request')

def request_wait(request):
    if request.session.get('current_user'):
        if not request.session.get('request_allowed'):
            last_req = _Request.objects.filter(email=request.session.get('current_user')).order_by('-time').first()
            if last_req and datetime.now(UTC) >= (last_req.time + timedelta(hours=2)):
                request.session['request_allowed'] = True
                return redirect('/canvas/request')
            else:
                wait_time = (last_req.time + timedelta(hours=2)) - datetime.now(UTC);
                if wait_time.total_seconds() < 60:
                    wait_time = str(round(wait_time.total_seconds())) + " seconds"
                    wait_time += " (or until " + str(last_req.time + timedelta(hours=2)) + ")"
                elif wait_time.total_seconds() < 3600:
                    minutes_calc = divmod(wait_time.total_seconds(), 60)
                    wait_time = str(round(minutes_calc[0] + (minutes_calc[1] / 60.0))) + " minute(s)"
                    wait_time += " (or until " + str(last_req.time + timedelta(hours=2)) + ")"
                else:
                    hours_calc = divmod(wait_time.total_seconds(), 3600)
                    wait_time = str(round(hours_calc[0] + (hours_calc[1] / 3600.0))) + " hour(s)"
                    wait_time += " (or until " + str(last_req.time + timedelta(hours=2)) + " UTC)"
                return render(request, 'artTubeApp/studio_wait_req.html', {'wait_time': wait_time})
        else:
            return redirect('/canvas/request')
    else:
        return redirect('/login?next=/canvas/request')

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

def denied_reqs(request):
    if request.session.get('current_user'):
        _email = request.session.get('current_user')
        if _Request.objects.filter(email=_email).exists():
            imgs = _Request.objects.filter(email=_email)
            img_categories = [_Category.objects.get(id=i.img_category.id).name for i in imgs]
        else:
            imgs = []
        return render(request, 'artTubeApp/studio_denied_reqs.html', {'requests': imgs, 'request_len': len(imgs), 'request_cat': img_categories})
    else:
        return redirect('/login?next=/canvas/denied_requests')

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
            binary_image = b64encode(submission["img"]).decode("ascii")
            submission["img"] = (
                f"data:{submission['img_type']};base64,{binary_image}"
            )
        
        return render(request, 'artTubeApp/gallery.html', {'submissions': submissions})

def events(request):
    if request.method == 'GET':
        events = list(_Events.objects.values(
                                "event_title",
                                "event_start",
                                "event_end",
                            ))
    elif request.method == 'POST':
        query_title = request.POST.get('query')
        if query_title:
            queried_events = _Events.objects.filter(event_title__icontains=query_title)
            return render(request, 'artTubeApp/events.html', {'events': queried_events})
        else:
            events = list(_Events.objects.values(
                                "event_title",
                                "event_start",
                                "event_end",
                            ))
    return render(request, 'artTubeApp/events.html', {'events': events})
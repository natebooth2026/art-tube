from base64 import b64encode #for image decoding

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from datetime import timedelta, datetime, UTC
from django.http import Http404

from .forms import account_creation, account_validate, sub_request_form, add_event, account_validate_emailMFA, request_decision, account_validate_questionsSetup, account_validate_changePWD, report_decision, switch_role
from .models import User as _User, Employee as _Employee, Admin as _Admin, Request as _Request, Submissions as _Submissions, Category as _Category, Events as _Events
from .sanitize import sanitize_img
from .log import add_log as _slog, LogType
import secrets
from django.core.mail import send_mail

#helper funcs
def get_user(email):
    return _User.objects.get(email=email)

def can_enter(request):
    return not request.session.get('in_gallery')

def admin_has_req_access(id):
    return _Request.objects.get(id=id).admin_approve == 1 

def remove_emp_touch(request):
    employee_obj = _Employee.objects.get(email=request.session.get('current_user'))
    if employee_obj:
        _Request.objects.filter(employee_touch=employee_obj.employee_id).update(employee_touch=None)

def revoke_validations(request):
    if _Admin.objects.filter(email=request.session.get('current_user')).exists():
        request.session['validate_requests'] = False
        request.session['validate_events'] = False
        request.session['validate_reports'] = False
        request.session['validate_roles'] = False
    elif _Employee.objects.filter(email=request.session.get('current_user')).exists():
        request.session['validate_requests'] = False
        request.session['validate_events'] = False
        remove_emp_touch(request)
    
# Create your views here.

def landing(request):
    revoke_validations(request)
    if not can_enter(request):
        return redirect('gallery')
    return render(request, 'artTubeApp/index.html')

def login(request):
    if not request.session.get('current_user'):
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
                _slog(LogType.ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT, extra_info=[request, _email])
            elif check_password(_password, users.password):
                next_page = request.POST.get('next') or request.GET.get('next') or '/'
                request.session.cycle_key()
                request.session['current_user'] = users.email
                _slog(LogType.ACCOUNT_LOGIN, extra_info=[request, users])
                return redirect(next_page)
            else:
                form.add_error('email', 'Bad login. Try again.')
                _slog(LogType.ACCOUNT_FAILED_LOGIN, extra_info=[request, users])

        return render(request, 'artTubeApp/login.html', {'form': form})
    else:
        return redirect('home')

def logout(request):
    if request.session.get('current_user') and _User.objects.filter(email=request.session.get('current_user')):
        revoke_validations(request)
        _slog(LogType.ACCOUNT_LOGOUT, extra_info=[request, get_user(request.session.get('current_user'))])
        del request.session['current_user']
        return render(request, 'artTubeApp/logout.html')
    elif not _User.objects.filter(email=request.session.get('current_user')):
        revoke_validations(request)
        _slog(LogType.ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT, extra_info=[request, request.session.get('current_user')])
        del request.session['current_user']
        return render(request, 'artTubeApp/logout.html')
    else:
        return redirect('home')

def signup(request):
    if not request.session.get('current_user'):
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
                    form.add_error('username', 'username already registered.')
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
                    _slog(LogType.ACCOUNT_CREATE, extra_info=[request, get_user(email)])
                    return redirect('login')
        else:
            form = account_creation()
        return render(request, 'artTubeApp/signup.html', {'form': form})
    else:
        revoke_validations(request)
        return redirect('home')

def emp_dashboard(request):
    is_emp = False
    if request.session.get('current_user'):
        revoke_validations(request)
        email = request.session.get('current_user')
        if _Employee.objects.filter(email=email).exists():
            if _Employee.objects.get(email=email).deactivated == 0:
                is_emp = True
            _slog(LogType.EMPLOYEE_ACCESS, extra_info=[request, get_user(email), _Employee.objects.get(email=email).employee_id, "Employee Dashboard"])
        else:
            _slog(LogType.USER_ATTEMPT_EMP_DASHBOARD, extra_info=[request, get_user(email)])
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
                settings.EMAIL_HOST_USER,  # Uses DEFAULT_FROM_EMAIL if configured
                [email],
                fail_silently=False,
            )
            form = account_validate_emailMFA()
            return render(request, 'artTubeApp/validate_email_MFA.html', {'form': form})
        else:
            return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
    elif request.method == 'POST' :
        form = account_validate_emailMFA(request.POST)
        if form.is_valid():
            if request.POST.get("action") == "next":
                email_code = form.cleaned_data.get('email_code')
                code = request.session.get("employee_code")
                #compare with code that was sent
                if email_code == code:
                    return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
                else:
                    is_emp = False
                    return render(request, 'artTubeApp/emp_dash.html', {'is_emp': is_emp})
            else: #resend button clicked
                return redirect('employee') #redirects and resends email
        else: #resend button clicked
            return redirect('employee') #redirects and resends email
                

def emp_events(request):
    if request.session.get('current_user'):
        if not request.session.get('validate_events'):
            return redirect('/validate?next=/employee/events')
        else:
            _email = request.session.get('current_user')
            form = add_event()
            v_form = account_validate()
            events = list(_Events.objects.values(
                        "id",
                        "event_title",
                        "event_start",
                        "event_end",
                    ))
            #email is associated with an employees acount
            if _Employee.objects.filter(email=_email).exists(): 
                if request.method == 'GET':
                    _slog(LogType.EMPLOYEE_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, "events"])
                    return render(request, 'artTubeApp/emp_events.html', {'events': events, 'form': form, 'v_form': v_form})
                if request.method == 'POST':
                    form = add_event(request.POST)
                    #user queries events
                    if 'search-events' in request.POST:
                        query_title = request.POST.get('query')
                        if query_title:
                            form = add_event()
                            queried_events = _Events.objects.filter(event_title__icontains=query_title)
                            return render(request, 'artTubeApp/emp_events.html', {'form': form, 'events': queried_events})
                        elif not query_title:
                            return redirect('emp_events')
                    #user submits new event
                    elif form.is_valid():
                        event_title = form.cleaned_data.get('event_title')
                        event_start = form.cleaned_data.get('event_start')
                        event_end = form.cleaned_data.get('event_end')
                        if _Events.objects.filter(event_title=event_title).exists():
                            _slog(LogType.EMPLOYEE_FAILED_CREATE, extra_info=[request, get_user(_email), _Employee.objects.get(email=_email).employee_id, event_title])
                            form.add_error('event_title', 'Event name unavailable')
                        elif event_end is not None:
                            if event_end < event_start:
                                _slog(LogType.EMPLOYEE_FAILED_CREATE, extra_info=[request, get_user(_email), _Employee.objects.get(email=_email).employee_id, event_title])
                                form.add_error('event_end', 'End date/time must come after start date/time')
                            else:
                                # create event entry
                                _Events.objects.create(
                                    event_title=event_title,
                                    event_start= event_start,
                                    event_end=event_end
                                )
                                events = list(_Events.objects.values(
                                            "id",
                                            "event_title",
                                            "event_start",
                                            "event_end",
                                        ))
                                _slog(LogType.EMPLOYEE_EVENT_CREATE, extra_info=[request, get_user(_email), _Employee.objects.get(email=_email).employee_id, _Events.objects.get(event_title=event_title).id])
                        else:
                            # create event entry
                            _Events.objects.create(
                                event_title=event_title,
                                event_start= event_start,
                                event_end=event_end
                            )
                            events = list(_Events.objects.values(
                                        "id",
                                        "event_title",
                                        "event_start",
                                        "event_end",
                                    ))
                            _slog(LogType.EMPLOYEE_EVENT_CREATE, extra_info=[request, get_user(_email), _Employee.objects.get(email=_email).employee_id, _Events.objects.get(event_title=event_title).id])
                        form=add_event() #reset form
                        return render(request, 'artTubeApp/emp_events.html', {'form': form, 'events': events, 'confirmation': 'Event successfully submitted!'})
            else:
                #redirect to home page
                request.session['validate_events'] = False
                return redirect('/')
    else:
        return redirect('/login?next=/employee/')

def emp_requests_landing(request):
    if request.session.get('current_user'):
        if not request.session.get('validate_requests'):
            return redirect('/validate?next=/employee/requests')
        else:
            if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                _slog(LogType.EMPLOYEE_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, "requests"])
            else:
                _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, "requests"])
            remove_emp_touch(request)
            requests = _Request.objects.filter(employee_touch__isnull=True, admin_approve=0, denied=0).exclude(email=request.session.get('current_user'))
            return render(request, 'artTubeApp/emp_requests.html', {'reqs': requests})
    else:
        return redirect('/login?next=/employee/')

def emp_request_view(request, id = -1):
    if request.session.get('current_user'):
        if not request.session.get('validate_requests'):
            return redirect('/validate?next=/employee/requests')
        else:
            if id < 0 or not _Request.objects.filter(id=id).exists():
                if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                    _slog(LogType.EMPLOYEE_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, f"request #{id} view"])
                else:
                    _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"request #{id} view"])
                return redirect('/employee/requests')
            elif _Request.objects.filter(id=id).exists():
                if (_Request.objects.get(id=id).employee_touch == None or _Request.objects.get(id=id).employee_touch == _Employee.objects.get(email=request.session.get('current_user')).employee_id) and _Request.objects.get(id=id).email.email != request.session.get('current_user') and not (_Admin.objects.get(email=request.session.get('current_user')) and not admin_has_req_access(id)):
                    if request.method == 'GET':
                        if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                            _slog(LogType.EMPLOYEE_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, f"request #{id} view"])
                        else:
                            _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"request #{id} view"])
                        req = _Request.objects.get(id=id)
                        req.employee_touch = _Employee.objects.get(email=request.session.get('current_user')).employee_id
                        req.save(update_fields=['employee_touch'])
                        form1 = request_decision()
                        form2 = account_validate()
                    elif request.method == "POST":
                        form1 = request_decision(request.POST)
                        form2 = account_validate(request.POST)
                        
                        if form2.is_valid():
                            _email = form2.cleaned_data.get("email")
                            _pwd = form2.cleaned_data.get("pwd")

                            employee = _Employee.objects.get(email=_email)
                            is_admin = _Admin.objects.filter(email=request.session.get('current_user'))
                            if not employee:
                                if not is_admin:
                                    _slog(LogType.EMPLOYEE_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                else:
                                    _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                form2.add_error('email', 'Employee account not found. Try again.')
                            else:
                                if employee.email.email != request.session.get('current_user'):
                                    if not is_admin:
                                        _slog(LogType.EMPLOYEE_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                    else:
                                        _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                    form2.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                                elif not check_password(_pwd, get_user(_email).password):
                                    if not is_admin:
                                        _slog(LogType.EMPLOYEE_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                    else:
                                        _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                    form2.add_error('email', 'Incorrect email/password combination. Try again.')
                                else:
                                    if form1.is_valid():
                                        _decision = form1.cleaned_data.get('decision')
                                        _category = form1.cleaned_data.get('category')
                                        _d_reason = form1.cleaned_data.get('denial_reason')
                                        r = _Request.objects.filter(id=id)
                                        if _decision == "approve":
                                            if _category is None:
                                                if not is_admin:
                                                    _slog(LogType.EMPLOYEE_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                                else:
                                                    _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                                form1.add_error('category', 'To approve a request, you must select an existing category.')
                                            else:
                                                item = _Request.objects.get(id=id)
                                                _Submissions.objects.create(
                                                    email=get_user(item.email.email),
                                                    approval_emp=_Employee.objects.get(email=request.session.get('current_user')),
                                                    img=r.img,
                                                    img_type=r.img_type,
                                                    img_title=r.img_title,
                                                    img_desc=r.img_desc,
                                                    approved_category=_category
                                                )
                                                item.delete()
                                                if not is_admin:
                                                    _slog(LogType.EMPLOYEE_REQUEST_APPROVE, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                                else:
                                                    _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                                return redirect('/employee/requests')
                                        elif _decision == "deny":
                                            if _d_reason != "":
                                                r.update(denied=1, denial_reason=_d_reason)
                                            else:
                                                r.update(denied=1)
                                            if not is_admin:
                                                _slog(LogType.EMPLOYEE_REQUEST_DENY, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                                            else:
                                                _slog(LogType.ADMIN_REQUEST_DENY, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                            return redirect('/employee/requests')
                    return render(request, 'artTubeApp/emp_view.html', {'item': _Request.objects.get(id=id), 'category': _Request.objects.get(id=id).img_category.name, 'd_form': form1, 'v_form': form2})
                else:
                    if request.method == 'GET':
                        if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                            _slog(LogType.EMPLOYEE_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, f"request #{id} view"])
                        else:
                            _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"request #{id} view"])
                    elif request.method == "POST":
                        if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                            _slog(LogType.EMPLOYEE_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, id])
                        else:
                            _slog(LogType.ADMIN_FAILED_REQUEST_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                    return redirect('/employee/requests')
            else:
                if not _Admin.objects.filter(email=request.session.get('current_user')).exists():
                    _slog(LogType.EMPLOYEE_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(request.session.get('current_user')).employee_id, f"request #{id} view"])
                else:
                    _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(request.session.get('current_user')).admin_id, f"request #{id} view"])
                return redirect('/employee/requests')
    else:
        return redirect('/login/?next=/employee/')

def admin_dashboard(request):
    is_admin = False
    if request.session.get('current_user'):
        revoke_validations(request)
        email = request.session.get('current_user')
        if _Admin.objects.filter(email=email).exists(): #myst be an admin to access admin_dash
            is_admin = True
            _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(email), _Admin.objects.get(email=email).admin_id, "Admin Portal"])
        elif _Employee.objects.filter(email=email):
            _slog(LogType.EMPLOYEE_ATTEMPT_ADMIN_PORTAL, extra_info=[request, get_user(email), _Employee.objects.get(email=email).employee_id])
        else:
            _slog(LogType.USER_ATTEMPT_ADMIN_PORTAL, extra_info=[request, get_user(email)])
        # return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
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
                    settings.EMAIL_HOST_USER,  # Uses DEFAULT_FROM_EMAIL if configured
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
            #user submits code
            if request.POST.get("action") == "next":
                email_code = form.cleaned_data.get('email_code')
                code = request.session.get("employee_code")
                #compare with code that was sent
                if email_code == code:
                    return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
                else:
                    is_admin = False
                    return render(request, 'artTubeApp/admin_dash.html', {'is_admin': is_admin})
            else: #user clicked resend code
                return redirect('admin') #redirects and resends email
        else: #user clicked resend code
            return redirect('admin') #redirects and resends email

def admin_submissions_landing(request):
    if request.session.get('current_user'):
        if not request.session.get('validate_reports'):
            return redirect('/validate?next=/admin/submissions')
        else:
            _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, "submissions"])
            remove_emp_touch(request)
            submissions = _Submissions.objects.all().exclude(email=request.session.get('current_user'), approval_emp_id=_Employee.objects.get(email=request.session.get('current_user')).employee_id).order_by('admin_review')
            return render(request, 'artTubeApp/admin_submissions.html', {'subs': submissions})
    else:
        return redirect('/login?next=/admin/')

def admin_submission_view(request, id = -1):
    if request.session.get('current_user'):
        if not request.session.get('validate_reports'):
            return redirect('/validate?next=/admin/submissions')
        else:
            if id < 0 or not _Submissions.objects.filter(id=id).exists():
                _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"submission #{id} view"])
                return redirect('/admin/submissions')
            elif _Submissions.objects.filter(id=id).exists():
                if (_Submissions.objects.get(id=id).admin_touch == None or _Submissions.objects.get(id=id).admin_touch == _Employee.objects.get(email=request.session.get('current_user')).employee_id) and _Submissions.objects.get(id=id).email.email != request.session.get('current_user'):
                    if request.method == 'GET':
                        _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"submission #{id} view"])
                        sub = _Submissions.objects.get(id=id)
                        sub.admin_touch = _Employee.objects.get(email=request.session.get('current_user')).employee_id
                        sub.save(update_fields=['admin_touch'])
                        form1 = report_decision()
                        form2 = account_validate()
                    elif request.method == "POST":
                        form1 = report_decision(request.POST)
                        form2 = account_validate(request.POST)
                        
                        if form2.is_valid():
                            _email = form2.cleaned_data.get("email")
                            _pwd = form2.cleaned_data.get("pwd")

                            admin = _Admin.objects.get(email=_email)
                            if not admin:
                                _slog(LogType.ADMIN_FAILED_REPORT_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                form2.add_error('email', 'Admin account not found. Try again.')
                            else:
                                if admin.email.email != request.session.get('current_user'):
                                    _slog(LogType.ADMIN_FAILED_REPORT_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                    form2.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                                elif not check_password(_pwd, get_user(_email).password):
                                    _slog(LogType.ADMIN_FAILED_REPORT_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                    form2.add_error('email', 'Incorrect email/password combination. Try again.')
                                else:
                                    if form1.is_valid():
                                        _decision = form1.cleaned_data.get('decision')
                                        _d_reason = form1.cleaned_data.get('denial_reason')
                                        s = _Submissions.objects.filter(id=id)
                                        s_obj = _Submissions.objects.get(id=id)
                                        if _decision == "verify":
                                            s.update(admin_review=admin)
                                            _slog(LogType.ADMIN_REPORT_DENIED, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                            return redirect('/admin/submissions')
                                        elif _decision == "remove":
                                            reported_user = _User.objects.filter(email=s_obj.email.email)
                                            reported_user.update(admin_approve=1)
                                            if _d_reason != "":
                                                new_r = _Request.objects.create(
                                                        email=s_obj.email,
                                                        img=s_obj.img,
                                                        img_type=s_obj.img_type,
                                                        img_title=s_obj.img_title,
                                                        img_desc=s_obj.img_desc,
                                                        img_category=s_obj.approved_category,
                                                        admin_approve=1,
                                                        denied=1,
                                                        denial_reason=_d_reason,
                                                        time=datetime.now(UTC)
                                                    )
                                            else:
                                                new_r = _Request.objects.create(
                                                        email=s_obj.email,
                                                        img=s_obj.img,
                                                        img_type=s_obj.img_type,
                                                        img_title=s_obj.img_title,
                                                        img_desc=s_obj.img_desc,
                                                        img_category=s_obj.approved_category,
                                                        admin_approve=1,
                                                        denied=1,
                                                        denied_reason=None,
                                                        time=datetime.now(UTC)
                                                    )
                                            s.delete()
                                            _slog(LogType.ADMIN_REPORT_APPROVED, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                                            return redirect('/admin/submissions')
                    return render(request, 'artTubeApp/admin_sub_view.html', {'item': _Submissions.objects.get(id=id), 'category': _Submissions.objects.get(id=id).approved_category.name, 'admin_app': _Submissions.objects.get(id=id).admin_review, 'd_form': form1, 'v_form': form2})
                else:
                    if request.method == 'GET':
                        _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, f"submission #{id} view"])
                    elif request.method == "POST":
                        _slog(LogType.ADMIN_FAILED_REPORT_DECISION, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, id])
                    return redirect('/admin/submissions')
            else:
                _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(request.session.get('current_user')).admin_id, f"submission #{id} view"])
                return redirect('/admin/submissions')
    else:
        return redirect('/login?next=/admin/')

def admin_switch_roles(request):
    if request.session.get('current_user'):
        if not request.session.get('validate_roles'):
            return redirect('/validate?next=/admin/switch_role')
        else:
            if request.method == 'GET':
                _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, "roles"])
                form1 = switch_role()
                form2 = account_validate()
            elif request.method == 'POST':
                form1 = switch_role(request.POST)
                form2 = account_validate(request.POST)

                if form1.is_valid():
                    _m_email = form1.cleaned_data.get("candidate_email")
                    _role = form1.cleaned_data.get("role")

                    print(_m_email)

                    _m_user = _User.objects.get(email=_m_email)
                    if _Employee.objects.filter(email=_m_email).exists():
                        _m_is_emp = _Employee.objects.get(email=_m_email)
                    else:
                        _m_is_emp = None

                    if form2.is_valid():
                        _email = form2.cleaned_data.get("email")
                        _pwd = form2.cleaned_data.get("pwd")

                        admin = _Admin.objects.get(email=_email)
                        if not admin:
                            if _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "fire":
                                _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "User"])
                            elif _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "hire":
                                _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "Employee"])
                            elif _m_user and _role == "hire":
                                _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "Employee"])
                            elif _m_user and _role == "fire":
                                _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "User"])
                            form2.add_error('email', 'Admin account not found. Try again.')
                        else:
                            if admin.email.email != request.session.get('current_user'):
                                if _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "fire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "User"])
                                elif _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "hire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "Employee"])
                                elif _m_user and _role == "hire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "Employee"])
                                elif _m_user and _role == "fire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "User"])
                                form2.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                            elif not check_password(_pwd, get_user(_email).password):
                                if _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "fire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "User"])
                                elif _m_user and (_m_is_emp and _m_is_emp.deactivated == 0) and _role == "hire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "Employee"])
                                elif _m_user and _role == "hire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "Employee"])
                                elif _m_user and _role == "fire":
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "User"])
                                form2.add_error('email', 'Incorrect email/password combination. Try again.')
                            else:
                                if not _m_user:
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Unknown", "Unknown"])
                                    form1.add_error('email', 'Not valid account. Try again. DON\'T FALL FOR A SCAM!')
                                elif _m_is_emp:
                                    if _m_is_emp.deactivated == 0 and _role == "fire": #valid
                                        _m_is_emp.deactivated = 1
                                        _m_is_emp.save()
                                        _slog(LogType.ADMIN_SWITCH_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "User"])
                                        form1 = switch_role()
                                        form2 = account_validate()
                                    elif _m_is_emp.deactivated == 1 and _role == "hire": #valid
                                        _m_is_emp.deactivated = 0
                                        _m_is_emp.save()
                                        _slog(LogType.ADMIN_SWITCH_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "Employee"])
                                        form1 = switch_role()
                                        form2 = account_validate()
                                    elif _m_is_emp.deactivated == 0 and _role == "hire": #invalid
                                        form1.add_error('role', 'Invalid role switch. Can\'t hire active employee')
                                        _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "Employee"])
                                    elif _m_is_emp.deactivated == 1 and _role == "fire": #invalid
                                        form1.add_error('role', 'Invalid role switch. Can\'t demote user/inactive employee')
                                        _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "User"])
                                elif not _m_is_emp and _role == "hire": #valid
                                    _Employee.objects.create(
                                        email=_m_user,
                                        can_approve_req = 1,
                                        deactivated = 0
                                    )
                                    _slog(LogType.ADMIN_SWITCH_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "Employee", "User"])
                                    form1 = switch_role()
                                    form2 = account_validate()
                                elif (not _m_is_emp or _m_is_emp.deactivated == 1) and _role == "fire": #invalid
                                    form1.add_error('role', 'Invalid role switch. Can\'t demote user/inactive employee')
                                    _slog(LogType.ADMIN_FAILED_SWITCHING_ROLE, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, _m_email, "User", "User"])
        return render(request, 'artTubeApp/admin_role_switch.html', {'r_form': form1, 'v_form': form2})        
    else:       
        return redirect('/login?next/admin/')

def validate(request):
    if request.session.get('current_user'):
        if request.method == 'GET' and _Employee.objects.filter(email=request.session.get('current_user')).exists():
            next_page = request.POST.get('next') or request.GET.get('next') or '/'
            if _Employee.objects.get(email=request.session.get('current_user')).deactivated == 0:
                form = account_validate()
                if not _Admin.objects.filter(email=request.session.get('current_user')):
                    _slog(LogType.EMPLOYEE_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, "validation"])
                else:
                    _slog(LogType.ADMIN_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, "validation"])
            else:
                if next_page[0:7] == "/admin/":
                    return redirect('admin')
                else:
                    return redirect('employee')
        if request.method == 'POST' and _Employee.objects.filter(email=request.session.get('current_user')).exists():
            next_page = request.POST.get('next') or request.GET.get('next') or '/'
            form = account_validate(request.POST)
            if form.is_valid():
                _email = form.cleaned_data.get('email')
                _password = form.cleaned_data.get('pwd')

                employee = _Employee.objects.filter(email=_email).first()

                if not employee:
                    form.add_error('email', 'Email is not associated with an employee/admin account. Please contact admin/database support if this is an error.')
                    _slog(LogType.ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT, extra_info=[request, _email])
                else:
                    if not _Admin.objects.filter(employee=employee).exists():
                        if employee.email.email != request.session.get('current_user'):
                            _slog(LogType.EMPLOYEE_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, next_page])
                            form.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                        elif not check_password(_password, employee.email.password):
                            _slog(LogType.EMPLOYEE_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Employee.objects.get(email=request.session.get('current_user')).employee_id, next_page])
                            form.add_error('email', 'Incorrect email/password combination. Try again.')
                        else:
                            revoke_validations(request)
                            if next_page == "/employee/events":
                                request.session['validate_events'] = True
                            elif next_page == "/employee/requests":
                                request.session['validate_requests'] = True
                            return redirect(next_page)
                    else:
                        if employee.email.email != request.session.get('current_user'):
                            _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, next_page])
                            form.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                        elif not check_password(_password, employee.email.password):
                            _slog(LogType.ADMIN_FAILED_ACCESS, extra_info=[request, get_user(request.session.get('current_user')), _Admin.objects.get(email=request.session.get('current_user')).admin_id, next_page])
                            form.add_error('email', 'Incorrect email/password combination. Try again.')
                        else:
                            revoke_validations(request)
                            if next_page == "/employee/events":
                                request.session['validate_events'] = True
                            elif next_page == "/employee/requests":
                                request.session['validate_requests'] = True
                            elif next_page == "/admin/submissions":
                                request.session['validate_reports'] = True
                            elif next_page == "/admin/switch_role":
                                request.session['validate_roles'] = True
                            return redirect(next_page)
        if not _Employee.objects.filter(email=request.session.get('current_user')).exists():
            if next_page[0:7] == "/admin/":
                return redirect('admin')
            else:
                return redirect('employee')
    else:
        return redirect('/login?next=/employee/')
            
    return render(request, 'artTubeApp/validate_email_pass.html', {'form': form})

def submit_request_page(request):
    if request.session.get('current_user'):
        last_req = _Request.objects.filter(email=request.session.get('current_user')).order_by('-time').first()
        if last_req and datetime.now(UTC) < (last_req.time + timedelta(hours=2)):
            request.session['request_allowed'] = False
            _slog(LogType.USER_ATTEMPT_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
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
                    _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
                    form2.add_error('email', 'User not found. Try again.')
                else:
                    if user.email != request.session.get('current_user'):
                        _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
                        form2.add_error('email', 'Email doesn\'t match current login. You must verify with your account details only.')
                    elif not check_password(pwd, user.password):
                        _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
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
                                _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
                                have_img = False
                                form1.add_error('img', 'Must provide a valid image file. Supported formats: .jpeg/.jpg, .png, .webp')
                            if not _title:
                                _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
                                have_title = False
                                form1.add_error('title', 'Title is required.')
                            if not _Category.objects.filter(id=_category.id):
                                _slog(LogType.USER_FAILED_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
                                have_category = False
                                form1.add_error('category', 'Invalid category.')
                            if not request.session.get('request_allowed'):
                                _slog(LogType.USER_ATTEMPT_REQUEST, extra_info=[request, get_user(request.session.get('current_user'))])
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
                                    denial_reason=None,
                                    time=datetime.now(UTC)
                                )
                                request.session['request_success'] = True
                                _slog(LogType.USER_SUBMIT_REQUEST, extra_info=[request, user])
                                return redirect('/canvas/request/success')  
        return render(request, 'artTubeApp/studio_new_req.html', {'r_form': form1, 'v_form': form2})
    else:
        return redirect('/login?next=/canvas/request/')

#successful request already logged
def request_submitted(request):
    if request.session.get('current_user'):
        if request.session.get('request_success') == True:
            request.session['request_success'] = False
            return render(request, 'artTubeApp/studio_req_success.html')
        return redirect('/canvas/request')
    else:
        return redirect('/login?next=/canvas/request')

#attempted request already logged
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
        revoke_validations(request)
        _email = request.session.get('current_user')
        _slog(LogType.USER_ACCESS_STUDIO, extra_info=[request, get_user(_email)])
        if _Request.objects.filter(email=_email).exists():
            imgs = _Request.objects.filter(email=_email)
            img_categories = [_Category.objects.get(id=i.img_category.id).name for i in imgs]
        else:
            imgs = []
            img_categories = []

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
        _slog(LogType.USER_FAILED_ACCESS_VIEW, extra_info=[request, get_user(request.session.get('current_user')), id])
        return redirect('studio')
    elif _Request.objects.filter(id=id, email=request.session.get('current_user')):
        revoke_validations(request)
        _slog(LogType.USER_ACCESS_VIEW, extra_info=[request, get_user(request.session.get('current_user')), id])
        return render(request, 'artTubeApp/studio_view.html', {'is_sub': False, 'item': _Request.objects.get(id=id), 'category': _Request.objects.get(id=id).img_category.name})
    else:
        _slog(LogType.USER_FAILED_ACCESS_VIEW, extra_info=[request, get_user(request.session.get('current_user')), id])
        return redirect('studio')

def sub_view(request, id = -1):
    if id < 0 or not _Submissions.objects.filter(id=id).exists():
        _slog(LogType.USER_FAILED_ACCESS_VIEW, extra_info=[request, get_user(request.session.get('current_user')), id])
        return redirect('studio')
    else:
        revoke_validations(request)
        _slog(LogType.USER_ACCESS_VIEW, extra_info=[request, get_user(request.session.get('current_user')), id])
        return render(request, 'artTubeApp/studio_view.html', {'is_sub': True, 'item': _Submissions.objects.get(id=id), 'category': _Submissions.objects.get(id=id).approved_category.name})

def denied_reqs(request):
    if request.session.get('current_user'):
        revoke_validations(request)
        _email = request.session.get('current_user')
        if _Request.objects.filter(email=_email).exists():
            imgs = _Request.objects.filter(email=_email)
            img_categories = [_Category.objects.get(id=i.img_category.id).name for i in imgs]
        else:
            imgs = []
        return render(request, 'artTubeApp/studio_denied_reqs.html', {'requests': imgs, 'request_len': len(imgs), 'request_cat': img_categories})
    else:
        return redirect('/login?next=/canvas/denied_requests')

#NEEDS LOGGING, POTENTIALLY ADDITIONAL LOGIC TOO TO INCLUDE ROOMS
def gallery(request):
    revoke_validations(request)
    if request.method == 'GET':
        request.session['in_gallery'] = True
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
        revoke_validations(request)
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

def enable_mfa(request):
    form1 = account_validate_emailMFA()
    form2 = account_validate_questionsSetup()
    if request.method == 'GET':
        email = request.session.get('current_user')
        code = f"{secrets.randbelow(1_000_000):06d}"
        request.session["employee_code"] = code
        #send email with code
        send_mail(
            "ArtTube Verification code",
            f"code is {code}",
            settings.EMAIL_HOST_USER,  # Uses DEFAULT_FROM_EMAIL if configured
            [email],
            fail_silently=False,
        )
        return render(request, "artTubeApp/enable_mfa.html", {'form1': form1})
    elif request.method == 'POST':
        if request.POST.get("action") == "submit-code":
            form = account_validate_emailMFA(request.POST)
            if form.is_valid():
                email_code = form.cleaned_data.get('email_code')
                code = request.session.get("employee_code")
                #compare with code that was sent
                if email_code == code:
                    return render(request, "artTubeApp/enable_mfa.html", {'form2': form2})
                else:
                    return render(request, "artTubeApp/enable_mfa.html", {'form1': form1, 'failure': 1})
        elif request.POST.get("action") == "submit-security-questions":
            form = account_validate_questionsSetup(request.POST)
            if form.is_valid():
                question_1 = form.cleaned_data.get('q1')
                answer_1 = make_password(form.cleaned_data.get('q_answer1'))
                question_2 = form.cleaned_data.get('q2')
                answer_2 = make_password(form.cleaned_data.get('q_answer2'))

                email=request.session.get('current_user')
                user = _User.objects.get(email=email)
                user.secure_q1 = question_1
                user.secure_a1 = answer_1
                user.secure_q2 = question_2
                user.secure_a2 = answer_2
                user.save(update_fields=['secure_q1', 'secure_a1', 'secure_q2', 'secure_a2'])
                return render(request, "artTubeApp/enable_mfa.html", {'success': 1})
    return render(request, "artTubeApp/enable_mfa.html", {'form1': form1})

def change_pwd(request):
    form1 = account_validate_emailMFA()
    form2 = account_validate_changePWD()
    if request.method == 'GET':
        email = request.session.get('current_user')
        code = f"{secrets.randbelow(1_000_000):06d}"
        request.session["employee_code"] = code
        #send email with code
        send_mail(
            "ArtTube Verification code",
            f"code is {code}",
            settings.EMAIL_HOST_USER,  # Uses DEFAULT_FROM_EMAIL if configured
            [email],
            fail_silently=False,
        )
        return render(request, "artTubeApp/change_password.html", {'form1': form1})
    elif request.method == 'POST':
        if request.POST.get("action") == "submit-code":
            form = account_validate_emailMFA(request.POST)
            if form.is_valid():
                email_code = form.cleaned_data.get('email_code')
                code = request.session.get("employee_code")
                #compare with code that was sent
                if email_code == code:
                    return render(request, "artTubeApp/change_password.html", {'form2': form2})
                else:
                    return render(request, "artTubeApp/change_password.html", {'form1': form1, 'failure': 1})
        elif request.POST.get("action") == "submit-new-pwd":
            form = account_validate_changePWD(request.POST)
            if form.is_valid():
                new_pwd = make_password(form.cleaned_data.get('new_pwd'))
                email=request.session.get('current_user')
                user = _User.objects.get(email=email)
                user.password = new_pwd
                user.save(update_fields=['password'])
                return render(request, "artTubeApp/change_password.html", {'success': 1})
            else: #pwd does not match
                return render(request, "artTubeApp/change_password.html", {'form2': form})
    return render(request, "artTubeApp/change_password.html", {'form1': form1})
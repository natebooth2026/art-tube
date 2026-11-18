from ipware import get_client_ip
from enum import Enum
from .models import Log as _Log
from datetime import datetime, UTC

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
    empty1 = 18
    empty2 = 19
    ACCOUNT_FAILED_LOGIN = 20
    ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT = 21
    ACCOUNT_FAILED_CREATE = 22
    EMPLOYEE_FAILED_CREATE = 23
    EMPLOYEE_FAILED_MODIFY = 24
    EMPLOYEE_FAILED_REQUEST_DECISION = 25
    EMPLOYEE_FAILED_ACCESS = 26
    USER_ATTEMPT_EMP_DASHBOARD = 27
    USER_ATTEMPT_ADMIN_PORTAL = 28
    EMPLOYEE_ATTEMPT_ADMIN_PORTAL = 29
    ADMIN_FAILED_ACCESS = 30
    ADMIN_FAILED_REQUEST_DECISION = 31
    ADMIN_FAILED_SWITCHING_ROLE = 32
    ADMIN_REPORT_APPROVED = 33
    ADMIN_REPORT_DENIED = 34
    ADMIN_FAILED_REPORT_DECISION = 35
    REPORT_FILED = 36
    USER_ENTER_ROOM = 37
    USER_LEAVE_ROOM = 38
    USER_ENTER_GALLERY = 39
    USER_LEAVE_GALLERY = 40
    USER_ATTEMPT_INVALID_ENTER = 41
    USER_VIEW_EVENT = 42
    USER_CHANGE_PASSWORD = 43
    USER_FAILED_CHANGE_PASSWORD = 44
    USER_ENABLED_MFA = 45
    USER_FAILED_ENABLE_MFA = 46
    USER_DISABLED_MFA = 47
    USER_FAILED_DISABLE_MFA = 48
    USER_ENABLE_MFA_SECURE_Q = 49 #Failure --> see 46
    EMPLOYEE_CHANGE_PASSWORD = 50
    EMPLOYEE_FAILED_CHANGE_PASSWORD = 51
    EMPLOYEE_ENABLE_SECURE_Q = 52
    EMPLOYEE_FAILED_ENABLE_SECURE_Q = 53
    EMPLOYEE_CHANGE_SECURE_Q = 54
    EMPLOYEE_FAILED_CHANGE_SECURE_Q = 55
    USER_CHANGE_SECURE_Q = 56
    USER_FAILED_CHANGE_SECURE_Q = 57
    ADMIN_CHANGE_PASSWORD = 58
    ADMIN_FAILED_CHANGE_PASSWORD = 59
    ADMIN_CHANGE_SECURE_Q = 60
    ADMIN_FAILED_CHANGE_SECURE_Q = 61
    EMPLOYEE_DISABLED_SECURE_Q = 62
    EMPLOYEE_FAILED_DISABLE_SECURE_Q = 63
    USER_FAILED_ACCESS_VIEW = 64
    USER_FAILED_ENTER_ROOM = 65

def add_log(_event = LogType.NONE, _time = datetime.now(UTC), _givenTime = False, extra_info = []):
    if not _givenTime:
        _time = datetime.now(UTC)

    if _event is LogType.NONE or _event is LogType.empty1 or _event is LogType.empty2:
        _Log.objects.create(
            time=_time,
            ip="0.0.0.0",
            action="Test log or failed to produce actual log message"
        )
    elif _event is LogType.ACCOUNT_LOGIN:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action="Logged in to",
            email=extra_info[1]
        )
    elif _event is LogType.ACCOUNT_FAILED_LOGIN:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action="Failed login into",
            email=extra_info[1]
        )
    elif _event is LogType.ACCOUNT_FAILED_LOGIN_TO_UNEXISTANT:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Attempted action to non-existant account ({extra_info[1]})"
        )
    elif _event is LogType.ACCOUNT_LOGOUT:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action="Logged out of",
            email=extra_info[1]
        )
    elif _event is LogType.ACCOUNT_CREATE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action="Successfully created account",
            email=extra_info[1]
        )
    elif _event is LogType.ACCOUNT_FAILED_CREATE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Failed to create an account with email {extra_info[1]}",
        )
    elif _event is LogType.EMPLOYEE_ACCESS:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} accessed {extra_info[3]} page",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_ACCESS:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to access {extra_info[3]} page",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_EVENT_CREATE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} created event #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_CREATE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to create event with name \"{extra_info[3]}\"",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_EVENT_MODIFY:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} modified event #{extra_info[3]} from ({extra_info[4:6]}) to ({extra_info[7:9]})",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_MODIFY:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to modify event #{extra_info[3]} from ({extra_info[4:6]}) to ({extra_info[7:9]})",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_REQUEST_APPROVE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} approved request #{extra_info[3]} for submission",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_REQUEST_DENY:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} denied request #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_REQUEST_DECISION:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to decide on request #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_ATTEMPT_ADMIN_PORTAL:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} attempted to access admin portal",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_CHANGE_PASSWORD:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} successfully changed password",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_CHANGE_PASSWORD:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to change password",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_ENABLE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} successfully enabled secure questions",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_DISABLED_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} successfully disabled secure questions",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_ENABLE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to enable secure questions",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_DISABLE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to disable secure questions",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_CHANGE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} successfully changed secure question #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.EMPLOYEE_FAILED_CHANGE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Employee #{extra_info[2]} failed to change secure question #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_ACCESS:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} accessed {extra_info[3]} page",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_ACCESS:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to access {extra_info[3]} page",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_REQUEST_APPROVE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} approved request #{extra_info[3]} for submission",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_REQUEST_DENY:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} denied request #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_REQUEST_DECISION:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to decide on request #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_REPORT_APPROVED:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} approved report on submission #{extra_info[3]}, submission #{extra_info[3]} now a denied request",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_REPORT_DENIED:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} denied report on submission #{extra_info[3]}, no action taken",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_REPORT_DECISION:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to decide on report on submission #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_SWITCH_ROLE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} switched role of user \"{extra_info[3]}\" from {extra_info[4]} to {extra_info[5]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_SWITCHING_ROLE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to switch role of user \"{extra_info[3]}\" from {extra_info[4]} to {extra_info[5]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_CHANGE_PASSWORD:
         _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} successfully changed password",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_CHANGE_PASSWORD:
         _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to change password",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_CHANGE_SECURE_Q:
         _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} successfully changed secure question #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_CHANGE_SECURE_Q:
         _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to change secure question #{extra_info[3]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_SUBMIT_REQUEST:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User created a new request",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ATTEMPT_REQUEST:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User attempted to create a new request before the end of the cooldown",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_REQUEST:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to create a new request",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ACCESS_VIEW:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User accessed view of request/submission #{extra_info[2]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_ACCESS_VIEW:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to access view of request/submission #{extra_info[2]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ACCESS_STUDIO:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User accessed the canvas",
            email=extra_info[1]
        )
    elif _event is LogType.USER_CHANGE_SUBMISSION:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User changed submission #{extra_info[2]} visibility from {extra_info[4]} to {extra_info[5]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ATTEMPT_EMP_DASHBOARD:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User attempted to access employee dashboard",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ATTEMPT_ADMIN_PORTAL:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User attempted to access admin portal",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ENTER_ROOM:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User/guest entered room \"{extra_info[2]}\"",
            email=extra_info[1]
        )
    elif _event is LogType.USER_LEAVE_ROOM:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User/guest left room \"{extra_info[2]}\"",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_ENTER_ROOM:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User/guest failed to enter room \"{extra_info[2]}\"",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ENTER_GALLERY:
        if extra_info[1] is not None:
            _Log.objects.create(
                time=_time,
                ip=get_client_ip(extra_info[0]),
                action=f"User/guest entered the gallery",
                email=extra_info[1]
            )
        else:
            _Log.objects.create(
                time=_time,
                ip=get_client_ip(extra_info[0]),
                action=f"User/guest entered the gallery"
            )
    elif _event is LogType.USER_LEAVE_GALLERY:
        if extra_info[1] is not None:
            _Log.objects.create(
                time=_time,
                ip=get_client_ip(extra_info[0]),
                action=f"User/guest entered the gallery",
                email=extra_info[1]
            )
        else:
            _Log.objects.create(
                time=_time,
                ip=get_client_ip(extra_info[0]),
                action=f"User/guest entered the gallery"
            )
    elif _event is LogType.USER_ATTEMPT_INVALID_ENTER:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User/guest attempted to enter \"{extra_info[2]}\" while in room \"{extra_info[4]}\"",
            email=extra_info[1]
        )
    elif _event is LogType.USER_VIEW_EVENT:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User/guest viewed event #{extra_info[2]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_CHANGE_PASSWORD:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User successfully changed password",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_CHANGE_PASSWORD:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to change password",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ENABLED_MFA:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User successfully enabled MFA",
            email=extra_info[1]
        )
    elif _event is LogType.USER_ENABLE_MFA_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User successfully enabled MFA and secure questions",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_ENABLE_MFA:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to enable MFA",
            email=extra_info[1]
        )
    elif _event is LogType.USER_DISABLED_MFA:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User successfully disabled MFA",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_DISABLE_MFA:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to disable MFA",
            email=extra_info[1]
        )
    elif _event is LogType.USER_CHANGE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User successfully changed secure question #{extra_info[2]}",
            email=extra_info[1]
        )
    elif _event is LogType.USER_FAILED_CHANGE_SECURE_Q:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"User failed to change secure question #{extra_info[2]}",
            email=extra_info[1]
        )
    elif _event is LogType.REPORT_FILED:
        if extra_info[1] is not None:
            _Log.objects.create(
                time=_time,
                ip=get_client_ip(extra_info[0]),
                action=f"Report was filed on submission #{extra_info[2]}",
                email=extra_info[1]
            )
    else:
        _Log.objects.create(
            time=_time,
            ip="-1.-1.-1.-1",
            action="LOG ERROR: Unknown type"
        )
    
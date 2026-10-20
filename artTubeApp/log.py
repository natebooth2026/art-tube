from ipware import get_client_ip
from .views import LogType
from .models import Log as _Log
from datetime import datetime, UTC

"""
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
"""

def add_log(_event = LogType.NONE, _time = datetime.now(UTC), extra_info = []):
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
            action=f"Attempted to login to non-existant account ({extra_info[1]})"
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
    elif _event is LogType.ACCOUNT_FAILED_LOGIN:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action="Failed to create an account",
            email=extra_info[1]
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
            action=f"Employee #{extra_info[2]} failed to create event with name {extra_info[3]}",
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
            action=f"Employee #{extra_info[2]} approved request #{extra_info[3]}",
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
            action=f"Admin #{extra_info[2]} approved request #{extra_info[3]}",
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
            action=f"Admin #{extra_info[2]} switched role of user #{extra_info[3]} from {extra_info[4]} to {extra_info[5]}",
            email=extra_info[1]
        )
    elif _event is LogType.ADMIN_FAILED_SWITCHING_ROLE:
        _Log.objects.create(
            time=_time,
            ip=get_client_ip(extra_info[0]),
            action=f"Admin #{extra_info[2]} failed to switch role of user #{extra_info[3]} from {extra_info[4]} to {extra_info[5]}",
            email=extra_info[1]
        )
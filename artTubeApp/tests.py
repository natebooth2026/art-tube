from io import BytesIO

from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from .forms import add_event, account_creation, account_validate, sub_request_form
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from .models import Category, User, Employee, Admin, Events, Request
import datetime
from unittest.mock import patch


class FormTests(TestCase):
    user_data = {
        "email": "test@gmail.com",
        "username": "test",
        "pwd": "testing213",
        "confirm_pwd": "testing213",
    }

    def create_employee_session(self):
        self.client.post(reverse("signup"), self.user_data)
        user = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(email=user, can_approve_req=0)
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session["validate_events"] = True
        session.save()

    # functional test
    def test_add_event(self):
        form_result = add_event(data={
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        self.assertTrue(form_result.is_valid())

    # functional test
    def test_invalid_event_title(self):
        form_result = add_event(data={
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        #invalid - no event_title
        self.assertFalse(form_result.is_valid())

    # functional test
    def test_invalid_event_start_end_times(self):
        self.create_employee_session()
        self.client.post(reverse("emp_events"), {
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 5:00",
        })

        self.assertFalse(Events.objects.filter(
            event_title="Test Event Title",
        ).exists())

    # functional test
    def test_reject_duplicate_event_title(self):
        self.create_employee_session()
        event_data = {
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 15:00",
        }
        self.client.post(reverse("emp_events"), event_data)
        self.client.post(reverse("emp_events"), {
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 16:00",
            "event_end": "2026-10-17 17:00",
        })

        self.assertEqual(
            Events.objects.filter(event_title="Test Event Title").count(),
            1,
        )

    # functional test
    def test_sub_request_form(self):
        category = Category.objects.create(name="testing")
        buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(buffer, format="PNG")
        sub_request_form_result = sub_request_form(
            data={
            "title": "test image",
            "desc": "testing",
            "category": category.pk,
            },
            files={
                "img": SimpleUploadedFile(
                    "test.png",
                    buffer.getvalue(),
                    content_type="image/png"
                ),
            },
        )
        self.assertTrue(sub_request_form_result.is_valid())

    
    # functional test
    def test_invalid_sub_request_form(self):
        category = Category.objects.create(name="testing")
        sub_request_form_result = sub_request_form(
            data={
            "title": "test image invalid",
            "desc": "testing invalid image",
            "category": category.pk,
            },
        )
        #No img file
        self.assertFalse(sub_request_form_result.is_valid())
    
    # functional test
    def test_account_creation(self):
        account_creation_result = account_creation(
            data={
                "email": "test@gmail.com",
                "username": "test",
                "pwd": "test123",
                "confirm_pwd": "test123",
            }
        )
        self.assertTrue(account_creation_result.is_valid())

    # functional test
    def test_account_creation_invalid_pwd(self):
        account_creation_result = account_creation(
            data={
                "email": "test@gmail.com",
                "username": "test",
                "pwd": "test123",
                "confirm_pwd": "passworddoesnotmatch",
            }
        )
        self.assertFalse(account_creation_result.is_valid())

    # functional test
    def test_account_validate(self):
        account_validate_result = account_validate(
            data={
                "email": "test@gmail.com",
                "pwd": "testing",
            }
        )
        self.assertTrue(account_validate_result.is_valid())

    # functional test
    def test_account_validate_invalid(self):
        account_validate_result = account_validate(
            data={
                "email": "test@gma",
                "pwd": "te",
            }
        )
        #invalid email
        self.assertFalse(account_validate_result.is_valid())

class ViewTests(TestCase):
    user_data = {
        "email": "test@gmail.com",
        "username": "test",
        "pwd": "testing213",
        "confirm_pwd": "testing213",
    }
    # functional test
    def test_signup(self):
        self.client.post(reverse("signup"), self.user_data)
        test_user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(test_user.email, self.user_data["email"])
        self.assertEqual(test_user.username, self.user_data["username"])
        self.assertTrue(check_password(self.user_data["pwd"], test_user.password))

    # security test
    def test_signup_rejects_mismatched_passwords_without_creating_account(self):
        signup_data = {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "wrong pwd",
        }

        self.client.post(reverse("signup"), signup_data)

        self.assertFalse(User.objects.filter(email=self.user_data["email"]).exists())

    # functional test
    def test_login(self):
        self.client.post(reverse("signup"), self.user_data)
        self.client.post(reverse("login"), self.user_data)
        _email = self.client.session.get("current_user")
        self.assertEqual(_email, self.user_data["email"])

    # security test
    def test_prevent_session_attacks(self):
        self.client.post(reverse("signup"), self.user_data)
        session = self.client.session
        session_id = session.session_key
        session.save()
        self.client.cookies["sessionid"] = session_id

        attacker = Client()
        attacker.cookies["sessionid"] = session_id
        self.client.post(reverse("login"), self.user_data)

        self.assertNotEqual(self.client.session.session_key, session_id)
        
    # security test
    def test_signup_reject_duplicate_account(self):
        self.client.post(reverse("signup"), self.user_data)
        self.client.post(reverse("signup"), self.user_data)
        user_count = User.objects.filter(
            email=self.user_data["email"],
            username=self.user_data["username"],
        ).count()
        self.assertEqual(user_count, 1)

    # security test
    def test_signup_reject_duplicate_username(self):
        self.client.post(reverse("signup"), self.user_data)
        duplicate_user_data = {
            **self.user_data,
            "email": "test2@gmail.com",
            "pwd": "testing456",
            "confirm_pwd": "testing456",
        }
        self.client.post(reverse("signup"), duplicate_user_data)
        print(self.user_data["username"])
        user_count = User.objects.filter(
            username=self.user_data["username"],
        ).count()
        
        self.assertEqual(user_count, 1)

    # security test
    def test_signup_reject_duplicate_email(self):
        self.client.post(reverse("signup"), self.user_data)
        duplicate_email_data = {
            "email": "test@gmail.com",
            "username": "new_test",
            "pwd": "testing12345",
            "confirm_pwd": "testing12345",
        }
        self.client.post(reverse("signup"), duplicate_email_data)
        user_count = User.objects.filter(
            email=self.user_data["email"],
            username=self.user_data["username"],
        ).count()
        self.assertEqual(user_count, 1)

    # security test
    def test_login_wrong_password_rejected(self):
        new_user = self.client.post(reverse("signup"), self.user_data)
        result = self.client.post(reverse("login"), {
                "email": "test@gmail.com",
                "pwd": "wrongpasssword",
            }
        )
        form = result.context["form"]
        self.assertIn("Email/password not found. Try again.", 
                    form.errors["email"])

    # security test
    def test_login_unkown_email_rejected(self):
        self.client.post(reverse("signup"), self.user_data)
        result = self.client.post(reverse("login"), {
                "email": "unkownemail@gmail.com",
                "pwd": "password",
            }
        )
        form = result.context["form"]
        self.assertIn("Email is not associated with an account. Please create a new account or try another email.", 
                        form.errors["email"])

    # functional test
    def test_logout_redirects_to_logout_page(self):
        self.client.post(reverse("signup"), self.user_data)
        result = self.client.post(reverse("login"), {
                "email": "test@gmail.com",
                "pwd": "testing213",
            }
        )
        self.assertRedirects(result, "/")
        result = self.client.get(reverse("logout"))
        self.assertTemplateUsed(result,"artTubeApp/logout.html")

    # security test
    def test_event_search_prevents_sql_injection(self):
        start = datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)
        end = datetime.datetime(2009, 1, 6, 16, 8, 24, 78915)
        Events.objects.create(
            event_title="Existing event",
            event_start=start,
            event_end=end,
        )
        response = self.client.post(
            reverse("events"),
            {"query": "' OR '1'='1' --"},
        )
        self.assertEqual(list(response.context["events"]), [])

    # security test
    def test_event_title_prevents_xss(self):
        start = datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)
        end = datetime.datetime(2009, 1, 6, 16, 8, 24, 78915)
        payload = '<script>console.log("xss")</script>'
        Events.objects.create(
            event_title=payload,
            event_start=start,
            event_end=end
        )
        response = self.client.get(reverse("events"))
        self.assertNotContains(response, payload)

    # security test
    def test_prevent_IDOR(self):
        user = {
            "email": "user@gmail.com",
            "username": "user",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        }
        other_user = {
            "email": "otheruser@gmail.com",
            "username": "otheruer",
            "pwd": "testing456",
            "confirm_pwd": "testing456",
        }
        self.client.post(reverse("signup"), user)
        self.client.post(reverse("signup"), other_user)
        user = User.objects.get(email=user["email"])
        category = Category.objects.create(name="classical")
        submission = Request.objects.create(
            email=user,
            img=b"submitted image",
            img_type="image/png",
            img_title="title",
            img_desc="description",
            img_category=category,
            admin_approve=0,
            denied=0,
        )

        session = self.client.session
        session["current_user"] = other_user["email"]
        session.save()

        response = self.client.get(
            reverse("studio_req_view", args=[submission.id])
        )

        self.assertRedirects(response, reverse("studio"))

    # security test
    def test_restrict_access_emp_dashboard_after_logout(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()

        result = self.client.get(reverse("logout"))
        self.assertTemplateUsed(result,"artTubeApp/logout.html")
        result = self.client.get(reverse("employee"))
        self.assertEqual(result["Location"], "/login?next=/employee/")

    # security test
    def test_disallow_user_access_emp_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()
        result = self.client.get(reverse("employee"))
        self.assertTemplateUsed(result, "artTubeApp/emp_dash.html")
        self.assertContains(result, "You are not authorized to access this page.")

    # security test
    def test_allow_emp_access_emp_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()
        #send email verification code
        with patch("artTubeApp.views.send_mail") as send_mail:
            result = self.client.get(reverse("employee"))
        self.assertTemplateUsed(result, "artTubeApp/validate_email_pass.html")
        #enter verficaiton code
        result = self.client.post(reverse("employee"), {
            "email_code": self.client.session["employee_code"],
            "action": "next",
        })

        self.assertTemplateUsed(result, "artTubeApp/emp_dash.html")
        self.assertContains(result, "Employee Dashboard")

    # security test
    def test_allow_admin_access_admin_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        user = User.objects.get(email=self.user_data["email"])
        employee = Employee.objects.create(
            email=user,
            can_approve_req=0,
        )
        Admin.objects.create(
            email=user,
            employee=employee,
        )
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()
        #sends email with code
        with patch("artTubeApp.views.send_mail") as send_mail:
            result = self.client.get(reverse("admin"))
        send_mail.assert_called_once()
        self.assertTemplateUsed(result, "artTubeApp/validate_email_MFA.html")
        #enters code
        result = self.client.post(reverse("admin"), {
            "email_code": self.client.session["employee_code"],
            "action": "next",
        })
        #can access admin portal
        self.assertTemplateUsed(result, "artTubeApp/admin_dash.html")
        self.assertContains(result, "Admin Portal")

    # security test
    def test_disallow_user_access_admin_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()
        result = self.client.get(reverse("admin"))
        self.assertTemplateUsed(result, "artTubeApp/admin_dash.html")
        self.assertContains(result, "You are not authorized to access this page.")

    # security test
    def test_disallow_employee_access_admin_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        session = self.client.session
        session["current_user"] = self.user_data["email"]
        session.save()
        result = self.client.get(reverse("admin"))
        self.assertTemplateUsed(result, "artTubeApp/admin_dash.html")
        self.assertContains(result, "You are not authorized to access this page.")



         

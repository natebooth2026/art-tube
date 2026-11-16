from io import BytesIO

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from artTubeApp.forms import add_event, account_creation, account_validate, sub_request_form
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from artTubeApp.models import Category, User, Employee, Events


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

    def test_login(self):
        self.client.post(reverse("signup"), self.user_data)
        self.client.post(reverse("login"), self.user_data)
        _email = self.client.session.get("current_user")
        self.assertEqual(_email, self.user_data["email"])

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

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import add_event, Sub_Request_Form, account_creation, account_validate
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from .models import Category, User, Employee

class FormTests(TestCase):
    def test_add_event(self):
        form_result = add_event(data={
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        self.assertTrue(form_result.is_valid())

    def test_invalid_add_event(self):
        form_result = add_event(data={
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        #invalid - not event_title
        self.assertFalse(form_result.is_valid())

    def test_sub_request_form(self):
        category = Category.objects.create(name="testing")
        sub_request_form_result = Sub_Request_Form(
            data={
            "title": "test image",
            "desc": "testing",
            "category": category.pk,
            },
            files={
                "img": SimpleUploadedFile(
                    "test.png",
                    b"test image",
                    content_type="image/png"
                ),
            },
        )
        self.assertTrue(sub_request_form_result.is_valid())

    
    def test_invalid_sub_request_form(self):
        category = Category.objects.create(name="testing")
        sub_request_form_result = Sub_Request_Form(
            data={
            "title": "test image invalid",
            "desc": "testing invalid image",
            "category": category.pk,
            },
        )
        #No img file
        self.assertFalse(sub_request_form_result.is_valid())
    
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

    def test_account_validate(self):
        account_validate_result = account_validate(
            data={
                "email": "test@gmail.com",
                "pwd": "testing",
            }
        )
        self.assertTrue(account_validate_result.is_valid())

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
    #functional test
    def test_signup(self):
        self.client.post(reverse("signup"), {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        })
        user_data = {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        }
        test_user = User.objects.get(email="test@gmail.com")
        self.assertEqual(test_user.email, user_data['email'])
        self.assertEqual(test_user.username, user_data["username"])
        self.assertTrue(check_password(user_data["pwd"], test_user.password))

    #functional and security test
    def test_signup_duplicate_account(self):
        new_user = self.client.post(reverse("signup"), {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        })
        duplicate_new_user = self.client.post(reverse("signup"), {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        })
        user_count = User.objects.filter(
            email="test@gmail.com",
            username="test",
        ).count()
        self.assertEqual(user_count, 1)

    #security test
    def test_restrict_user_access_emp_dashboard(self):
        new_user = self.client.post(reverse("signup"), {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        })
        user_data = {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        }
        current_session = self.client.session
        current_session["current_user"] = user_data["email"]
        current_session.save()
        result = self.client.get(reverse("employee"))
        self.assertRedirects(result,"/")

    #security test
    def test_allow_emp_access_emp_dashboard(self):
        self.client.post(reverse("signup"), {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        })
        user_data = {
            "email": "test@gmail.com",
            "username": "test",
            "pwd": "testing213",
            "confirm_pwd": "testing213",
        }
        new_emp = User.objects.get(email="test@gmail.com")
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        current_session = self.client.session
        current_session["current_user"] = user_data["email"]
        current_session.save()
        result = self.client.get(reverse("employee"))
        self.assertTemplateUsed(result,"artTubeApp/emp_dash.html")

    

         


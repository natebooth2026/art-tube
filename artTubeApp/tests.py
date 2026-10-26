from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import add_event, Sub_Request_Form, account_creation, account_validate
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from .models import Category, User, Employee, Admin


class FormTests(TestCase):
    user_data = {
        "email": "test@gmail.com",
        "username": "test",
        "pwd": "testing213",
        "confirm_pwd": "testing213",
    }
    def test_add_event(self):
        form_result = add_event(data={
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        self.assertTrue(form_result.is_valid())

    def test_invalid_event_title(self):
        form_result = add_event(data={
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 12:00",
        })

        #invalid - no event_title
        self.assertFalse(form_result.is_valid())

    def test_invalid_event_start_end_times(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        form_result = self.client.post(reverse("employee"), {
            "event_title": "Test Event Title",
            "event_start": "2026-10-17 10:00",
            "event_end": "2026-10-17 5:00",
        })

        form = form_result.context["form"]
        self.assertIn("End date/time must come after start date/time", 
                        form.errors["event_end"])

    def test_duplicate_event_title(self):
            self.client.post(reverse("signup"), self.user_data)
            new_emp = User.objects.get(email=self.user_data["email"])
            Employee.objects.create(
                email=new_emp,
                can_approve_req=0,
            )
            current_session = self.client.session
            current_session["current_user"] = self.user_data["email"]
            current_session.save()
            self.client.post(reverse("employee"), {
                "event_title": "Test Event Title",
                "event_start": "2026-10-17 10:00",
                "event_end": "2026-10-17 15:00",
            })
            form_result = self.client.post(reverse("employee"), {
                "event_title": "Test Event Title",
                "event_start": "2026-10-17 16:00",
                "event_end": "2026-10-17 17:00",
            })
    
            form = form_result.context["form"]
            self.assertIn("Event name unavailable", 
                            form.errors["event_title"])

    def test_event_time_overlap(self):
                self.client.post(reverse("signup"), self.user_data)
                new_emp = User.objects.get(email=self.user_data["email"])
                Employee.objects.create(
                    email=new_emp,
                    can_approve_req=0,
                )
                current_session = self.client.session
                current_session["current_user"] = self.user_data["email"]
                current_session.save()
                self.client.post(reverse("employee"), {
                    "event_title": "Test Event",
                    "event_start": "2026-10-17 10:00",
                    "event_end": "2026-10-17 15:00",
                })
                form_result = self.client.post(reverse("employee"), {
                    "event_title": "Overlapping Event",
                    "event_start": "2026-10-17 11:00",
                    "event_end": "2026-10-17 17:00",
                })
        
                form = form_result.context["form"]
                self.assertIn("Event overlaps with other events", 
                                form.errors["event_title"])

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
    user_data = {
        "email": "test@gmail.com",
        "username": "test",
        "pwd": "testing213",
        "confirm_pwd": "testing213",
    }
    #functional test
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

    #functional and security test
    def test_signup_reject_duplicate_account(self):
        self.client.post(reverse("signup"), self.user_data)
        self.client.post(reverse("signup"), self.user_data)
        user_count = User.objects.filter(
            email=self.user_data["email"],
            username=self.user_data["username"],
        ).count()
        self.assertEqual(user_count, 1)

    def test_signup_reject_duplicate_username(self):
        self.client.post(reverse("signup"), self.user_data)
        duplicate_user_data = {
            **self.user_data,
            "email": "test2@gmail.com",
            "pwd": "testing456",
            "confirm_pwd": "testing456",
        }
        self.client.post(reverse("signup"), duplicate_user_data)
        user_count = User.objects.filter(
            username=self.user_data["username"],
        ).count()
        self.assertEqual(user_count, 1)

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

    #security test
    def test_login_wrong_password_rejected(self):
        new_user = self.client.post(reverse("signup"), self.user_data)
        result = self.client.post(reverse("login"), {
                "email": "test@gmail.com",
                "pwd": "wrongpasssword",
            }
        )
        form = result.context["form"]
        self.assertIn("Bad login. Try again.", 
                    form.errors["email"])

    #security test
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

    def test_restrict_access_emp_dashboard_after_logout(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()

        result = self.client.get(reverse("logout"))
        self.assertTemplateUsed(result,"artTubeApp/logout.html")
        result = self.client.get(reverse("employee"))
        self.assertRedirects(result,"/login/?next=/employee/")

    #security test
    def test_restrict_user_access_emp_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        result = self.client.get(reverse("employee"))
        self.assertRedirects(result,"/")

    #security test
    def test_allow_emp_access_emp_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        result = self.client.get(reverse("employee"))
        self.assertTemplateUsed(result,"artTubeApp/emp_dash.html")

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
            secure_q1="security question 1",
            secure_q2="security question 2",
            secure_a1="answer",
            secure_a2="answer",
        )
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        result = self.client.get(reverse("admin"))
        self.assertTemplateUsed(result,"artTubeApp/admin_dash.html")

    def test_restrict_user_access_admin_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        result = self.client.get(reverse("admin"))
        self.assertRedirects(result,"/")

    def test_restrict_emp_access_admin_dashboard(self):
        self.client.post(reverse("signup"), self.user_data)
        new_emp = User.objects.get(email=self.user_data["email"])
        Employee.objects.create(
            email=new_emp,
            can_approve_req=0,
        )
        current_session = self.client.session
        current_session["current_user"] = self.user_data["email"]
        current_session.save()
        result = self.client.get(reverse("admin"))
        self.assertRedirects(result,"/")



         

import base64
from datetime import datetime, timezone

from django.db import migrations
from django.db import models


SAMPLE_USERS = (
    {
        "email": "test_user_one@gmail.com",
        "username": "test_user_one",
    },
    {
        "email": "test_user_two@gmail.com",
        "username": "test_user_two",
    },
    {
        "email": "employee@gmail.com",
        "username": "sample_employee",
    },
    {
        "email": "admin@gmail.com",
        "username": "sample_admin",
    },
)

SAMPLE_CATEGORIES = ("Abstract", "Classical", "Digital", "Landscape")

SAMPLE_EVENTS = (
    {
        "event_title": "ArtTube exhibition",
        "event_start": datetime(2026, 11, 14, 16, tzinfo=timezone.utc),
        "event_end": datetime(2026, 11, 14, 19, tzinfo=timezone.utc),
    },
    {
        "event_title": "Fall Artwork showcase",
        "event_start": datetime(2026, 12, 5, 17, tzinfo=timezone.utc),
        "event_end": datetime(2026, 12, 5, 19, tzinfo=timezone.utc),
    },
)

SAMPLE_IMAGES = (
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAKAAAAB4CAIAAAD6wG44AAAFL0lEQVR42u2dy07bQBSGx2agVdpKXbYSC+oVBLohodx35WH6Aq2g3ZRbXwyplQpsSmABuOzYIpWYSyaoi1SUEMcZe+7j/1dUIWrs+c8355zx4IRgtP6BQP4qRAgAGAJgyFZREiAIfgMGYZRoCIAh9GAIGQxhkQUhgyH0YGQwBMAQFlkQejCEEg2JlWjPFW//zj4gWnsDwB5y7T3SS9KUBF414XgrFp8T0ecIGewV2tRT+YE5BF2d5wRgu0h4wNjt++B4M9Yze6IvkbsZHDj60kC3eyY5GaXQ2dw99f6K5e3BpmLtImPsRedUgAxWnUYbp6W9uv+LLBviG2+cYpGlKLInGAl6MJqxmz04Xj/BePALfwjPZJWsTIdOLAbj9WMru8ax/aFDiSZ46A4CYKWV8OsxxoZnsgyutAJkMATAEABD2IvGbgd2skpGGCUaPRhCD0aFRgaXV2y5jWeysl7R+ri18KL18ezBd+iy5TaeyfIyd1nq1+jBPjRgtsR6edMdih6cVgk3xv0YVS91AHazOC8xgp0sXws0W2pls6c7w/4/k8WWWrmOjzYn7KrPmxN9fQ3O75bnz2Sxxdb9v15VZm5H2ryHZqOQy6c9SZw6krzM9DAOjc9x5xhLoauNcUiCQNurnx+22OI/SbRVNUl3q5o+MJEZrzLm+jKYLdwW/l/bW6/Y4JV6D+0JAb9PU0mcel0peNQxDq2a4DYzVkdXKWPl98F5x80WbnnvjLf1MY62q+LWuDZOZL+C0fcfFebu/E3BDbbvT/gPjtcaKtFOyrUm0bjJEs3mbxSFgJ+BzWeWnhJaAYuPMu8ZVJDIOKfSuSv35MHoiuQSzeakjY/+yF2v4lUJ5Tr6NqnHoFzvOgBLN1/YZwHS2Vx10pXIOBhd+SSP7rUan09FfjxePRjEdcqsQXXeZQJWal7cp+UG1XmXcx+s2jybuzb7bKcpuuLeJayi2awO83quQvDWFYNxN8XY+NwSGYDQg+/6nbPZa83V2ZLKUdh48R7MZq8MWb3S13oNeexnPBk+0tSD2TuTzvVc3azHXt3unxFCEnqkvAdrc96xZGQMVtG93T97GIqEHvFjDu10fm/JCGPb6KZ+n5Nxvs/JYjOJfj+d74xMj6WSoD8rHt/kZMzve8aVdlVOBqum+6gQcVqVPioNk1g8Gl2Yhw4lAFZqm9NMv8Mkjs0eurmOz2BMzdrO66TzI73lms0k4rXaBroFAvKQcW+5Hvz+YFZPrHLSryuzmYTuFmesyKa2mNxjrtxVed9dyOpNO230S2VWT+jus0J0mx7Q/cc4PCSEVO4mB5RoFZ5leeBZYHuzVC6KudFhHOqhy78mFAxQgZGbTV91YUnCRhI2UnowqzWdMNAvlVm9Sfd4C7VcsxYGh6ozrAdtaldmNS7GBulqC07XIovVLh1F25vKrNake88z6V56T7erB0sxrLTX5o1ghqOS0P1/H8ymL93N2qzx1Mbo/uM8FjfrUIiouGHb0D4e23QK45LQJYRQEbo2o+3qGoRUyJSp9DUbJeox2q6bQnJQIW/Z9J9S0S0C2Dm0Dxj/Ivtat71siBUtA9qBv4zyEm0OwH6g1baDbVW4Qifuax3CYFu4aEmyVkMq2xmxsFRZqw6MtRGjZctaFalsc9xoydEKLrDtj9vQyItX7fML0O2ofX7RPr8Yev3Sm5sLfKR/EXIOLVMAODdCt9oZABd5Hw1x6W8XQnwLbEfXochgz/fhAZjgQ1ggAIYAGAJgCIAhAIYAGIAhAIac0F+Mxs7/YA/J+QAAAABJRU5ErkJggg=="
    ),
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAKAAAAB4CAIAAAD6wG44AAAFPElEQVR42u2dSUwUQRiF/xrHmxucRhP0pDIuiCuIggugxpNrCJ6NF8VEHY8eVG6aqMzgFu8mknhyHTFxV9xREU8uYOK+HIwKjImHQSQiM909Vd1Vf72XPvQBZnrq6/e6u+rvKlEYWUdpCcIOv50QQawFwMwVFmgD3oD7BTaEiIYQ0RAcDOEaDCGiIUQ0BMAWRDRCGg6GABjCXTSE52AIEQ0horPr7oG3hh75rPoIHAzhGmywBCIaeBHRNkW0drpY8ivzH1TeGwJyhvVFN5emXJwBM/+eAVX3w2RXRAuTHNw8N5XrJ8zo/YSqB2H4VSPAzWUpyR84PUVEVQ+BOei76AvzUgrPm+IUEVXzxezhLlr4uSml+/ccKk5lOxKjEbvY/DvTL8zv8TUnpvUQUXXrUMsjOuSPc32m2x+z1f71p6MjGRDd3m8v6rF8uFCte5PlwbdvsqjHWg+rjehkebcmrZIs6kZES9Z5bej2Hs/UblR0yGvNCh1b00LGIUFC+qYn3T7GRpeCu2WB4UJEtEudq+jS/Defm9JF6Iv2prMLumAarfqiUZPFHHFIqn1/ovkxXAiZWXR3BvZFXTSEumhIy4g+vfAHmp7wdiGEOTogyXXRbB1cXVuJs0EO4FMLv+tJF4zlFN3p7F1+jD1UdLBCPJAoO8Yua7JsuO7anNV8IjozRTaMdayL1uSe2U4fc7gGOyfHgrHvddFmPe+aztiuiPZGy6qsDqGvCnXRWTYT6ZZ8q0VdtFOtuDTcRO+ay5h5REtMZhsYy3m70NzrrnGMA+mLFkbfVZnGOIi+6JWXRhh9z8w4q6W9AG76E5EpjBl2dPj2vMvSx9Lm6Fh1eSSD3gwTGAc3RwePvirNGQcZ0aulmjjAnkhOWR1CPzNvxpLn6FhzeRSbUQQ9GQc/R8eaK6PYjBEx8HEYyZyVccuw457/fcvJY07+bN+q9aocvyiy6d/31mTsNFV85TS+64qxQ6jeYC+tn+CKhVgUqVMBmIiaKr5wGrrPyjhHrg5JL62f6IqFwoheezWvqfyLDYUZ0tH2/9gc01ssVubg9M6JjIzNojvQxIrQZnDzMpcOVg44A2MTvZu3837f74qWbvfzq9vb9nhAIBZHNqsGTIJOzP/MJpnzdj2IlsaC+vb2p3tdtbxPU/rXXMtnc90NkC4RRSfFNB0urLmWX3M933S6ZcngD75wUkzfvmjQ9ZmxkvmiB9s+J6aDrjTG0Zhe80V/aiwGXbmaGN2mS0QbTZdQdJd5M52unvbtM3Hmxlc+V+XHg9NgIwpuesMQ6Jpr37QmFG6lQCYj/QDvamBhVQ7+cAh0+a5dyIau/vmc1vjCrYOuHyw9ot8fKoJv9ElpyRH9/jDo8q2LBl1iPF/0u8NT0ZoaziMtx8HvjoAu34gGXc590bzp3lhy0YjjfP5sv5K+6LdHp8AimvdlhUAXEf2fzR66+qf0i2cHMg8XetHoDU98KLZN680+REUO2b08EvMNleY7b3ZPJtM6pV+0N2R5N0ngJP+jMTvaBm2sskpDlzLE0naO9PJGg45H1d6AtQvltebNBuPoEtYudKVXN+Pj5tZpcSRP40IIrD6qhLEOdLE4pcr2vRU3hS5WAPeojltxIhpb6mtcd7TFiUgIDWqyLNk6WhI+0k14O8gw7JhTu7ckiGhsySaFX/Ek4eiBFxGtTp23E0RUMEcy5s7HCcr5IQcOlopZEBEVzM6JdOejhMRH1zDhOVg66TuNfY1aMGujo39pbeyXw0Ju0R2kUK/vNRI5mAuHsG4SBMDQQP0GtgpH2YZvg4QAAAAASUVORK5CYII="
    ),
)


def ensure_events_table(apps, schema_editor):
    Events = apps.get_model("artTubeApp", "Events")
    with schema_editor.connection.cursor() as cursor:
        tables = schema_editor.connection.introspection.table_names(cursor)
    if Events._meta.db_table not in tables:
        schema_editor.create_model(Events)


def seed_sample_data(apps, schema_editor):
    database = schema_editor.connection.alias
    User = apps.get_model("artTubeApp", "User")
    Employee = apps.get_model("artTubeApp", "Employee")
    Admin = apps.get_model("artTubeApp", "Admin")
    Category = apps.get_model("artTubeApp", "Category")
    Events = apps.get_model("artTubeApp", "Events")
    Request = apps.get_model("artTubeApp", "Request")
    Submissions = apps.get_model("artTubeApp", "Submissions")

    seeded_user_emails = set()
    for user_data in SAMPLE_USERS:
        user, created = User.objects.using(database).get_or_create(
            email=user_data["email"],
            defaults={
                "username": user_data["username"],
                "password": "!",
                "admin_approve": 0,
                "locked": 0,
                "number_2fa": 0,
            },
        )
        if created or (
            user.username == user_data["username"] and user.password == "!"
        ):
            seeded_user_emails.add(user_data["email"])

    categories = {}
    for name in SAMPLE_CATEGORIES:
        category, _ = Category.objects.using(database).get_or_create(name=name)
        categories[name] = category

    employees = {}
    for email in ("employee@gmail.com", "admin@gmail.com"):
        if email not in seeded_user_emails:
            continue
        employee, _ = Employee.objects.using(database).get_or_create(
            email_id=email,
            defaults={"can_approve_req": 1, "deactivated": 0},
        )
        employees[email] = employee

    if "admin@gmail.com" in employees:
        Admin.objects.using(database).get_or_create(
            email_id="admin@gmail.com",
            defaults={"employee_id": employees["admin@gmail.com"].pk},
        )

    for event_data in SAMPLE_EVENTS:
        Events.objects.using(database).get_or_create(
            event_title=event_data["event_title"],
            defaults={
                "event_start": event_data["event_start"],
                "event_end": event_data["event_end"],
            },
        )

    sample_art = (
        {
            "email": "test_user_one@gmail.com",
            "title": "Golden Horizon (Sample)",
            "description": "Generated sample artwork for a fresh ArtTube database.",
            "category": "Landscape",
            "image": SAMPLE_IMAGES[0],
            "published": True,
        },
        {
            "email": "test_user_two@gmail.com",
            "title": "Abstract Forms (Sample)",
            "description": "Generated sample artwork for a fresh ArtTube database.",
            "category": "Abstract",
            "image": SAMPLE_IMAGES[1],
            "published": True,
        },
        {
            "email": "test_user_one@gmail.com",
            "title": "Study in Color (Sample)",
            "description": "A sample request awaiting review.",
            "category": "Digital",
            "image": SAMPLE_IMAGES[0],
            "published": False,
        },
    )
    for art in sample_art:
        if art["email"] not in seeded_user_emails:
            continue
        if art["published"]:
            if "employee@gmail.com" not in employees:
                continue
            Submissions.objects.using(database).get_or_create(
                email_id=art["email"],
                img_title=art["title"],
                defaults={
                    "approval_emp_id": employees["employee@gmail.com"].pk,
                    "img": art["image"],
                    "img_type": "image/png",
                    "img_desc": art["description"],
                    "approved_category_id": categories[art["category"]].pk,
                    "admin_review_id": None,
                },
            )
        else:
            Request.objects.using(database).get_or_create(
                email_id=art["email"],
                img_title=art["title"],
                defaults={
                    "img": art["image"],
                    "img_type": "image/png",
                    "img_desc": art["description"],
                    "img_category_id": categories[art["category"]].pk,
                    "employee_touch": None,
                    "admin_approve": 0,
                    "denied": 0,
                    "denial_reason": None,
                    "time": datetime(2026, 10, 30, 12, tzinfo=timezone.utc),
                },
            )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("artTubeApp", "0002_reconcile_missing_model_columns"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="events",
            options={"db_table": "events", "managed": True},
        ),
        migrations.AlterField(
            model_name="request",
            name="img",
            field=models.BinaryField(),
        ),
        migrations.AlterField(
            model_name="submissions",
            name="img",
            field=models.BinaryField(),
        ),
        migrations.RunPython(
            ensure_events_table,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            seed_sample_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email')
    employee = models.ForeignKey('Employee', models.DO_NOTHING)
    secure_q1 = models.CharField(max_length=30)
    secure_q2 = models.CharField(max_length=30)
    secure_a1 = models.CharField(max_length=30)
    secure_a2 = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'admin'


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'category'


class DjangoContentType(models.Model):
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Employee(models.Model):
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email')
    employee_id = models.CharField(primary_key=True, max_length=30)
    can_approve_req = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'employee'


class Log(models.Model):
    time = models.DateTimeField()
    ip = models.CharField(max_length=45)
    action = models.CharField(unique=True, max_length=255)
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'log'


class Request(models.Model):
    username = models.ForeignKey('User', models.DO_NOTHING, db_column='username', to_field='username')
    img = models.TextField()
    img_type = models.CharField(unique=True, max_length=30)
    img_title = models.CharField(unique=True, max_length=30)
    img_desc = models.CharField(unique=True, max_length=30)
    img_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='img_category')
    admin_approve = models.ForeignKey('User', models.DO_NOTHING, db_column='admin_approve', to_field='admin_approve', related_name='request_admin_approve_set')
    denied = models.IntegerField()
    denial_reason = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'request'


class Submissions(models.Model):
    username = models.ForeignKey('User', models.DO_NOTHING, db_column='username', to_field='username')
    approval_emp = models.ForeignKey(Employee, models.DO_NOTHING)
    img = models.TextField()
    img_title = models.ForeignKey(Request, models.DO_NOTHING, db_column='img_title', to_field='img_title')
    img_desc = models.ForeignKey(Request, models.DO_NOTHING, db_column='img_desc', to_field='img_desc', related_name='submissions_img_desc_set')
    approved_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='approved_category')

    class Meta:
        managed = False
        db_table = 'submissions'


class User(models.Model):
    username = models.CharField(unique=True, max_length=30)
    password = models.CharField(max_length=30)
    email = models.CharField(primary_key=True, max_length=30)
    admin_approve = models.IntegerField(unique=True)
    locked = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user'

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from base64 import b64encode
from django.db import models
from .sanitize import fernet


class Admin(models.Model):
    email = models.OneToOneField('User', models.DO_NOTHING, db_column='email')
    admin_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey('Employee', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'admin'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        managed = True
        db_table = 'category'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
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


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Employee(models.Model):
    email = models.OneToOneField('User', models.DO_NOTHING, db_column='email')
    employee_id = models.AutoField(primary_key=True)
    can_approve_req = models.IntegerField()
    deactivated = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'employee'


class Events(models.Model):
    event_title = models.CharField(max_length=255)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'events'


class Log(models.Model):
    time = models.DateTimeField()
    ip = models.CharField(max_length=45)
    action = models.CharField(max_length=1000)
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'log'


class Occupancy(models.Model):
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email', blank=True, null=True)
    ip = models.CharField(max_length=45)

    class Meta:
        managed = True
        db_table = 'occupancy'


class Request(models.Model):
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email')
    employee_touch = models.IntegerField(blank=True, null=True)
    img = models.BinaryField()
    img_type = models.CharField(max_length=255)
    img_title = models.CharField(max_length=255)
    img_desc = models.CharField(max_length=1000)
    img_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='img_category')
    admin_approve = models.IntegerField()
    denied = models.IntegerField()
    denial_reason = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'request'

    def img_b64(self):
        if self.img:
            return b64encode(bytes(fernet.decrypt(self.img))).decode('utf-8')
        return None


class Submissions(models.Model):
    email = models.ForeignKey('User', models.DO_NOTHING, db_column='email')
    approval_emp = models.ForeignKey(Employee, models.DO_NOTHING)
    admin_touch = models.IntegerField(blank=True, null=True)
    img = models.BinaryField()
    img_type = models.CharField(max_length=255)
    img_title = models.CharField(max_length=255)
    img_desc = models.CharField(max_length=1000)
    approved_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='approved_category')
    admin_review = models.ForeignKey(Admin, models.DO_NOTHING, db_column='admin_review', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'submissions'

    def img_b64(self):
        if self.img:
            return b64encode(bytes(fernet.decrypt(self.img))).decode('utf-8')
        return None


class User(models.Model):
    username = models.CharField(unique=True, max_length=30)
    password = models.CharField(max_length=255)
    email = models.CharField(primary_key=True, max_length=255)
    admin_approve = models.IntegerField()
    locked = models.IntegerField()
    number_2fa = models.IntegerField(db_column='2FA')  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    secure_q1 = models.CharField(max_length=255, blank=True, null=True)
    secure_q2 = models.CharField(max_length=255, blank=True, null=True)
    secure_a1 = models.CharField(max_length=255, blank=True, null=True)
    secure_a2 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user'

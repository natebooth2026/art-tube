from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("artTubeApp", "0003_sample_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="submissions",
            name="admin_touch",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="employee",
            name="deactivated",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="request",
            name="time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

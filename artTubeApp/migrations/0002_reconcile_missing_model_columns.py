from django.db import migrations


MODEL_COLUMNS = {
    "User": ("secure_q1", "secure_q2", "secure_a1", "secure_a2"),
    "Submissions": ("admin_review",),
}


def reconcile_missing_model_columns(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        tables = set(schema_editor.connection.introspection.table_names(cursor))

    for model_name, field_names in MODEL_COLUMNS.items():
        model = apps.get_model("artTubeApp", model_name)
        table_name = model._meta.db_table
        if table_name not in tables:
            raise RuntimeError(f"Expected database table {table_name!r} does not exist.")

        with schema_editor.connection.cursor() as cursor:
            columns = {
                column.name
                for column in schema_editor.connection.introspection.get_table_description(
                    cursor, table_name
                )
            }

        for field_name in field_names:
            if model._meta.get_field(field_name).column not in columns:
                schema_editor.add_field(model, model._meta.get_field(field_name))


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("artTubeApp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            reconcile_missing_model_columns,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

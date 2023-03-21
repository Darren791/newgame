# Generated by Django 4.1.7 on 2023-03-19 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("objects", "0014_defaultobject_defaultcharacter_defaultexit_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="KeyDB",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(db_index=True, max_length=32)),
                ("pending", models.BooleanField(default=False)),
                ("date", models.DateTimeField(auto_now_add=True, null=True)),
                ("comment", models.TextField(blank=True, default="")),
                (
                    "holder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="key_holder",
                        to="objects.objectdb",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="key_owner",
                        to="objects.objectdb",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="key_target",
                        to="objects.objectdb",
                    ),
                ),
            ],
        ),
    ]

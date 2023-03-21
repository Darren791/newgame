# Generated by Django 4.1.7 on 2023-03-19 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("objects", "0014_defaultobject_defaultcharacter_defaultexit_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrgDB",
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
                ("db_key", models.CharField(db_index=True, max_length=128)),
                ("db_acro", models.CharField(blank=True, max_length=12)),
                (
                    "db_leader",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="group_leader",
                        to="objects.objectdb",
                    ),
                ),
                ("db_members", models.ManyToManyField(to="objects.objectdb")),
            ],
        ),
        migrations.CreateModel(
            name="OrgMember",
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
                ("db_rank", models.IntegerField()),
                (
                    "db_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="org_member",
                        to="objects.objectdb",
                    ),
                ),
                (
                    "db_org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="orgs.orgdb"
                    ),
                ),
            ],
        ),
    ]
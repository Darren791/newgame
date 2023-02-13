from django.db import models


class KeyDB(models.Model):
    key = models.CharField(max_length=32, blank=False, db_index=True)
    target = models.ForeignKey(
        "objects.ObjectDB",
        related_name="key_target",
        null=True,
        default=None,
        on_delete=models.CASCADE,
        db_index=True,
    )
    owner = models.ForeignKey(
        "objects.ObjectDB",
        related_name="key_owner",
        on_delete=models.CASCADE,
        db_index=True,
    )
    holder = models.ForeignKey(
        "objects.ObjectDB",
        related_name="key_holder",
        on_delete=models.CASCADE,
        db_index=True,
    )
    pending = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    comment = models.TextField(default="", blank=True, null=False)

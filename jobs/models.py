from django.db import models
from django.db.models.expressions import ExpressionWrapper


class Ticket(models.Model):
    NEW = 0x01
    APP = 0x02
    DENIED = 0x04
    CLOSED = 0x08
    UPDATED = 0x10

    STATUS_CHOICES = [
        (NEW, 'NEW'),
        (APP, "APPROVED"),
        (DENIED, "DENIED"),
        (CLOSED, 'CLOSED'),
        (UPDATED, "UPDATED")
    ]

    title = models.CharField(max_length=128, db_index=True)
    body = models.TextField(blank=False)
    assignee = models.ForeignKey("accounts.AccountDB",
                                 on_delete=models.CASCADE,
                                 null=True,
                                 related_name='assignee_job')
    requester = models.ForeignKey("accounts.AccountDB",
                                  on_delete=models.CASCADE,
                                  null=True,
                                  related_name='requestor_job')
    status = models.BooleanField(default=True, db_index=True)
    bucket = models.CharField(max_length=18, db_index=True)
    opened = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField('Comment')

    def assigned_to(self):
        return self.assignee.name if self.assignee else 'Unassigned'

        
class Comment(models.Model):
    author = models.ForeignKey("objects.ObjectDB",
                               on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=False)
    private = models.BooleanField(default=False)
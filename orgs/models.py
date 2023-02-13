from django.db import models


class OrgDB(models.Model):
    db_key = models.CharField(max_length=128, blank=False, null=False, db_index=True)
    db_acro = models.CharField(max_length=12, blank=True)
    db_leader = models.ForeignKey("objects.ObjectDB", null=True, on_delete=models.SET_NULL, related_name='group_leader')
    db_members = models.ManyToManyField("objects.ObjectDB")

class OrgMember(models.Model):
    db_member = models.ForeignKey("objects.ObjectDB", on_delete=models.CASCADE, related_name="org_member", db_index=True)
    db_org = models.ForeignKey(OrgDB, on_delete=models.CASCADE)
    db_rank = models.IntegerField()
    

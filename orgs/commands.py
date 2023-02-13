from evennia import default_cmds
import world.utils as myutils
import world.headers as headers

from .models import OrgDB, OrgMember


def do_org_create(cmd):
    cmd.caller.msg("IN ORG/CREATE")


def do_org_destroy(cmd):
    cmd.caller.msg("IN ORG/DESTROY")


def do_org_list(cmd):
    cmd.caller.msg("IN ORG/LIST")
    groups = OrgDB.objects.all()
    if groups.count() == 0:
        cmd.caller.msg("There aren't any groups.")
        return



class CmdOrg(default_cmds.MuxCommand):
    key = "org"
    aliases = "orgs"
    help_category = "General"
    switch_options = ("list", "create", "destroy")

    def func(self):
        if not self.switches:
            do_org_list(self)
        elif "create" in self.switches:
            do_org_create(self)
        elif "destroy" in self.switches:
            do_org_destroy(self)
        elif "list" in self.switches:
            do_org_list(self)




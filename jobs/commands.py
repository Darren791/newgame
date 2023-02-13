from evennia import default_cmds
from . api import match_ticket, match_category, all_job_categories
from . models import Ticket
from world.utils import itemize

def all_jobs_by_id():
    """ """
    return Ticket.objects.filter(status=True).order_by('id')


def all_jobs_by_date():
    """ """
    return Ticket.objects.filter(status=True).order_by('opened')


def can_change_cat(ticket, caller):
    """ """
    if caller == ticket.requestor or \
            'job_manager' in caller.permissions.all() or \
            'admin' in caller.permissions.all() or \
            caller == ticket.assignee:
        return True

    return False


def can_open_ticket(caller):
    """ can this object create a new ticket? """
    return not caller.is_guest


def can_comment_ticket(ticket, caller):
    # admin, job_manager perms, original requestor, assignee
    if caller == ticket.requestor or \
            'job_manager' in caller.permissions.all() or \
            'admin' in caller.permissions.all() or \
            caller == ticket.assignee:
        return True

    return False


class CmdJobs(default_cmds.MuxCommand):
    """
    a simple ticket system for Evennia.

    The ticket system (aka the jobs system) is meant to track player requests, bug reports and other
    game issues.

    job/rename <jobid>=<new name>
    job/category <jobid> = <new category>
    job/open <category>/<title>=<text>
    job <jobid> or job/view <jobid>
    job/comment <jobid>=<text>
    job/close <jobid>
    job/reopen <jobid>
    job/all
    job/assign <jobid>=<account>
    job/backup
    job/listcat <category>
    job/cat <job>=<category>

    """

    key = "job"
    aliases = ('jobs', 'tickets', 'myjobs', 'ticket')
    switch_choices = (
        'rename', 'open', 'list', 'mine',
        'assign', 'view', 'comment', 'close', 'reopen',
        'archive', 'cat', 'listcat',
    ) 

    help_category = "Communications"
    account_caller = True

    def do_listcat(self):
        """ List all categories """

        cat = all_job_categories()
        if not cat:
            self.msg("Error: no such category.")
            return
        table = self.styled_table("CAT", "DESCRIPTION", width=80)
        for x in cat:
            table.add_row(*x)
        table.reformat_column(0, width=10)

        self.msg(str(table))

    def do_cat(self):
        """ Change a ticket's category (bucket) """

        if not self.lhs or not self.rhs:
            self.msg("Usage: +job/cat <jobid>=<category>")
            return

        ticket = match_ticket(self.lhs)
        if not ticket:
            self.msg("No such ticket.")
            return

        if not self.can_change_cat(ticket, self.caller):
            self.msg("You do not have permission to modify that ticket.")
            return

        cat = match_category(self.rhs)
        if not cat:
            self.msg("No such category")
            return

        old_bucket = ticket.bucket
        ticket.bucket = cat
        ticket.save()

        self.msg(f"Ticket {ticket.id} category changed from \"{old_bucket}\" to \"{cat}\".")


    def do_rename(self):
        """ Rename a ticket. """
        self.msg("+job/rename")

        if not self.lhs or not self.rhs:
            self.msg("Usage: job/rename <jobid>=<new title>")
            return

        job = match_ticket(self.lhs)
        if not job:
            self.msg(f"No such ticket: \"{self.lhs}\".")
            return
        job.title = self.rhs.strip()
        job.save()
        self.msg(f"Ticket {job.id} title changed to: \"{self.rhs}\".")
    
    def do_open(self):
        """ Open (create) a new ticket. """

        """ Check args """
        if not self.lhs or not self.rhs or '/' not in self.lhs:
            self.msg("Usage: +job/open <bucket>/<subject>=<body>")
            return

        if not can_open_ticket(self.caller):
            self.msg("You do not have permission to open tickets.")
            return

        """ Parse bucket and title from lhs args. """
        bucket, title = self.lhs.split('/')

        # Remove any leading or tailing spaces.
        bucket = bucket.strip()
        title = title.strip()    

        # Make sure that we have a good bucket.
        cat = match_category(bucket)
        if not cat:
            self.msg(f"No such bucket: \"{bucket}\".")
            return

        # Create the job!
        ticket = Ticket(bucket=bucket,
                        requester=self.caller,
                        title=title,
                        body=self.rhs,
                        assignee=None)
        # Save it!
        ticket.save()

        self.msg(f"Job {ticket.id} created.")

    def do_view(self):
        """ View an existing job. """
        jobs = all_jobs_by_id()
        if not jobs:
            self.msg("There are no tickets to display.")
            return

        table = self.styled_table("ID", "BUCKET", "AUTHOR", "ASSIGNED", "TITLE")
        for x in jobs:
            table.add_row(
                x.id,
                x.bucket.upper(),
                x.requester.name,
                x.assigned_to(),
                x.title
            )

        self.msg(str(table))

    def do_comment(self):
        """ Comment an existing job. """
        self.msg("job/comment")
    
    def do_close(self):
        """ Close a job. """
        self.msg("+job/close")
    
    def do_reopen(self):
        """ Reopen a closed job. """
        self.msg("+job/reopen")
    
    def do_assign(self):
        """ Assign a job. """
        self.msg("+job/assign")

    def do_archive(self):
        """ Archives jobs to external file (JSON). """
        pass

    def do_mine(self):
        """ Display my jobs """
        self.msg("My Jobs")

    def func(self):
        """ Command entry point. """

        switch = self.switches[0] if self.switches else "view"

        if switch not in self.switch_choices:
            self.msg(f"'{switch}' is not a valid switch.")
            return

        if self.cmdstring == "myjobs":
            switch = "mine"

        fun = getattr(self, f"do_{switch}", None)
        if fun and callable(fun):
            fun()
        else:
            self.msg(f"There was an error calling the switch handler: {switch}")

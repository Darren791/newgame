from .models import Ticket, Comment
from world.utils import match_all

JOB_CATEGORIES = (
    ('ADMIN', 'Admin use only.'),
    ('APP', 'Issues related to character applications.'),
    ('BUG', 'Report a bug or other implementation error.'),
    ('BUILD', 'Request quota, linking to main grid, etc.'),
    ('CG', 'Chargen related issues.'),
    ('CODE', 'Code issues and requests.'),
    ('FORUM', 'Forum related issues.'),
    ('PITCH', 'Pitch an idea to Staff.'),
    ('PLOT', 'Plot related issues.'),
    ('THEME', 'Theme related issues or requests.'),
    ('TYPO', 'Report a typo.'),
    ('REQ', 'Requests.'),
    ('WIKI', 'Issues related to the game\'s WIKI'),

)    


def all_job_categories():
    return JOB_CATEGORIES


def job_categories():
    return [x[0] for x in JOB_CATEGORIES]


def match_category(cat):
    return match_all(JOB_CATEGORIES, cat)


def all_tickets_by_category(cat):
    return Ticket.objects.filter(category=cat)
    

def _ticket_by_number(num):
    try:
        return Ticket.objects.get(pk=num)
    except:
        return None


def _ticket_by_name(name):
    match = Ticket.objects.filter(title__startswith=name)
    return match.first() if match.count() == 1 else None


def match_ticket(args, **kwargs):
    return _ticket_by_number(int(args)) \
        if args.isnumeric() \
        else _ticket_by_name(args)

    


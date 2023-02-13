import re
from evennia import ObjectDB, AccountDB
from evennia import default_cmds
from evennia.utils import create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from world.headers import header, footer
from world.utils import itemize
from mail.models import Malias


allowed_switches = ("create", "destroy", "add", "remove", "list")
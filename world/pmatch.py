from evennia import ObjectDB, AccountDB
from typeclasses.characters import Character
from evennia.utils import make_iter
from world.utils import parse_int_or_dbref


def pmatch(name, **kwargs):
    """
      Match players by Account or Character, by name, alias, or dbref,
      optionally filtering by connected status.

      Depending on args, returns either an AccountDB or ObjectDB reference,
      or None.

      Credits:
        Darren@Seventh Sea MUSH
    """

    player = kwargs.get("player", None)
    connected = kwargs.get("connected", False)
    match_account = kwargs.get("match_account", False)
    exclude = make_iter(kwargs.get("exclude", ()))

    if num := parse_int_or_dbref(name):
        match = match_account_by_num(num) if match_account else match_player_by_num(num)
    else:
        # Check for 'me' and 'self'.
        if player and name in ("me", "self"):
            match = player
        else:
            match = match_account_by_name(name) if match_account else match_player_by_name(name)

        if not match:
            return match

        if match and connected and not match.sessions.all():
            return None

        return match if match not in exclude else None


def match_account_by_num(num: int):
    try:
        match = AccountDB.objects.get(pk=num)
    except:
        match = None

    return match


def match_player_by_num(num: int):
    try:
        match = ObjectDB.objects.get(pk=num)
    except:
        match = None

    if match and inherits_from(match, Character):
        return match

    return None


def match_player_by_name(name):
    matches = Character.objects.filter(db_key__startswith=name)
    if not matches:
        # If no matches, try a lookup by alias.
        matches = Character.objects.filter(
            db_tags__db_tagtype__iexact="alias",
            **{"db_tags__db_key__iexact": name})

    if matches.count() != 1:
        return None

    return matches.first()


def match_account_by_name(name):
    # Account lookup (by username).
    matches = AccountDB.objects.filter(username__startswith=name)

    if not matches:
        # If no match, try a lookup by alias.
        matches = AccountDB.objects.filter(
            db_tags__db_tagtype__iexact="alias",
            **{"db_tags__db_key__iexact": name})

    if matches.count() != 1:
        return None

    return matches.first()


def match_players(targets=None, delim=','):
    """ Match a comma-separated list of player names/alias. """

    if not targets:
        return None

    matches = set()
    for x in make_iter(targets).split(delim):
        if target := pmatch(x.strip()):
            matches.add(target)
    return matches

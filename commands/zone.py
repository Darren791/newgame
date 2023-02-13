from evennia import default_cmds, utils
from django.conf import settings
from world.utils import capstr

# -----------------------
# Darren@Seventh Sea MUSH
# -----------------------


class CmdZone(default_cmds.MuxCommand):
    """
    Usage:
        zone <room>
        zone <room>=<zone>
        zone/clear <room>

        This is a more convenient way to handle Evennia's tag based zones
        than the raw @tag command. This command automatically handles the
        zone category, it trims excess spaces, and converts any remaining
        spaces into underscores. It also ensures that there is one, and only
        one, tag with the zone category. It also supports adding additional
        zones, or "subzones". For example, you might use "zone" for the main
        zone, and "area" for smaller regions within the main zone.

        Credits: Darren @ 7th Sea MUSH.
    """

    key = "zone"
    aliases = ("area",)
    help_category = "Building"
    switch_options = ("clear",)
    locks = "perm(Builder)"

    def func(self):
        caller = self.caller

        # If they called the command without any args, display a usage
        # message and quit.
        if not self.args:
            caller.msg(f"Usage: {self.cmdstring}[/clear] <room>[=<{self.cmdstring}>]")
            return

        # Find the object they're trying to zone.
        obj = caller.search(self.lhs)

        # If no object was found, we can just quit because search() will
        # have already handled displaying the error message.
        if not obj:
            return

        # Ensure that the target object is a room. Note that this is a
        # design choice and not a limitation of the system! Zones are just
        # tags and all typeclasses can have tags.
        if not utils.inherits_from(obj, settings.BASE_ROOM_TYPECLASS):
            caller.msg(f"Only rooms should have {self.cmdstring}s.")
            return

        # Ensure the caller has permission to modify the room. In this case,
        # we're checking for edit or control (ownership) perms.
        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg(
                f"You don't have permission to change the {self.cmdstring} of {obj.get_display_name(caller)}."
            )
            return

        # Are we just clearing?
        just_clearing = ("clear" in self.switches) if self.switches else False

        # Now let's check to see if there is a zone already set.
        tmp = obj.tags.get(category=self.cmdstring, return_list=True)
        old_zone = tmp[0] if tmp else None

        # Now let's deal with the new zone name. Since zones are tags and
        # tags cannot contain spaces, we'll make things easier for our
        # builders by automatically converting any spaces into underscores.
        # We use split() and join() here rather than replace() to make sure that
        # all of the words of the zone name are seperated by a single space.
        zone = "_".join(self.rhs.split()) if self.rhs else None

        # Now let's handle removing the old zone.
        if (old_zone and zone) or just_clearing:
            if old_zone:
                obj.tags.remove(old_zone, category=self.cmdstring)
                caller.msg(
                    f'Existing {self.cmdstring} "|w{old_zone}|n" removed from {obj.get_display_name(caller)}.'
                )
            else:
                caller.msg(f"There is no old {self.cmdstring} to clear.")

            if just_clearing:
                return

        if zone:
            # Set the new zone.
            obj.tags.add(zone, category=self.cmdstring)
            caller.msg(
                f'{self.cmdstring.capitalize()} of {obj.get_display_name(caller)} set to "|w{zone}|n".'
            )
        else:
            # No new zone was given, just display the current zone (if any).
            if old_zone:
                caller.msg(
                    f'The {self.cmdstring} of {obj.get_display_name(caller)} is "|w{old_zone}|n".'
                )
            else:
                caller.msg(
                    f"Room {obj.get_display_name(caller)} has no {self.cmdstring} set."
                )

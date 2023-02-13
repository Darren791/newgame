import world.messages as MESSAGES
import re
from world.utils import capstr, room
from evennia.utils import is_iter, make_iter

class MessageMixins(object):

    def msg_contents(self, text=None, exclude=None, from_obj=None, mapping=None, **kwargs):
            """
            Emits a message to all objects inside this object.

            Args:
                text (str or tuple): Message to send. If a tuple, this should be
                    on the valid OOB outmessage form `(message, {kwargs})`,
                    where kwargs are optional data passed to the `text`
                    outputfunc.
                exclude (list, optional): A list of objects not to send to.
                from_obj (Object, optional): An object designated as the
                    "sender" of the message. See `DefaultObject.msg()` for
                    more info.
                mapping (dict, optional): A mapping of formatting keys
                    `{"key":<object>, "key2":<object2>,...}. The keys
                    must match `{key}` markers in the `text` if this is a string or
                    in the internal `message` if `text` is a tuple. These
                    formatting statements will be
                    replaced by the return of `<object>.get_display_name(looker)`
                    for every looker in contents that receives the
                    message. This allows for every object to potentially
                    get its own customized string.
            Keyword Args:
                Keyword arguments will be passed on to `obj.msg()` for all
                messaged objects.

            Notes:
                The `mapping` argument is required if `message` contains
                {}-style format syntax. The keys of `mapping` should match
                named format tokens, and its values will have their
                `get_display_name()` function called for  each object in
                the room before substitution. If an item in the mapping does
                not have `get_display_name()`, its string value will be used.

            Example:
                Say Char is a Character object and Npc is an NPC object:

                char.location.msg_contents(
                    "{attacker} kicks {defender}",
                    mapping=dict(attacker=char, defender=npc), exclude=(char, npc))

                This will result in everyone in the room seeing 'Char kicks NPC'
                where everyone may potentially see different results for Char and Npc
                depending on the results of `char.get_display_name(looker)` and
                `npc.get_display_name(looker)` for each particular onlooker

            """
            # we also accept an outcommand on the form (message, {kwargs})
            is_outcmd = text and is_iter(text)
            inmessage = text[0] if is_outcmd else text
            outkwargs = text[1] if is_outcmd and len(text) > 1 else {}

            contents = self.contents
            if exclude:
                exclude = make_iter(exclude)
                contents = [obj for obj in contents if obj not in exclude]
            
            for obj in contents:
                if mapping and not obj.tags.get('quiet'):
                    substitutions = {
                        t: sub.get_display_name(obj) if hasattr(sub, "get_display_name") else str(sub)
                        for t, sub in mapping.items()
                    }
                    outmessage = inmessage.format(**substitutions)
                else:
                    outmessage = inmessage
                obj.msg(text=(outmessage, outkwargs), from_obj=from_obj, **kwargs)


    def pronoun_sub(self, template, player, iobj=None, location=None):

        if not template:
            return ''

        if not player:
            player = self

        if not location:
            location = self.location or self

        # Handle a single-char sub.
        def replace_char(match):
            ret = ''
            m = match.group(1).lower().lstrip('%')
            caps = m.isupper()

            if m == 't':
                # The direct object, this.
                ret = capstr(self.name) if caps else self.name
            elif m == 'n':
                # The enactor, player.
                if player:
                    ret = capstr(player.name) if caps else player.name
            elif m == 'i':
                # The indirect object, secondary target of an action. Usually None.
                if iobj:
                    ret = capstr(iobj.name) if caps else iobj.name
            elif m == 'l':
                # Location
                if location:
                    ret = capstr(location.name) if caps else location.name
            elif m == 'c':
                # outermost container (usually a room)
                r = room(self)
                if r:
                    ret = capstr(r.name) if caps else r.name
            elif m in 'opqrs':
                # Pronouns
                r = self.get('pronoun')
                if r and callable(r):
                    pro = r(f"p{m}")
                    if pro:
                        ret = capstr(pro) if caps else pro
            else:
                # Not a substitution, return as-is.
                ret = match.group(0)

            return ret

        # Handle attribute sub.
        def replace_var(match):
            m = match.group(1).lower()

            if m.startswith("db."):
                m = m.lstrip("db.")
                if self.attributes.has(m):
                    return str(self.attributes.get(m))
                else:
                    return ""
            elif hasattr(self, m):
                a = getattr(self, m)
                return str(a) if a else ""
            else:
                return ""

            # return match.group(0)

        # Handle method sub.
        def replace_fun(match):
            m = match.group(1).lower()
            try:
                fun = getattr(self, m)
            except:
                fun = None

            if fun and callable(fun):
                return str(fun())

            return match.group(0)

        # Single character subs.
        #regexp = re.compile(r"(%\w)+")
        regexp = re.compile(r"(%[A-Za-z#!]+)")
        out = regexp.sub(replace_char, template)

        # Attribute sub.
        regexp = re.compile(r"%\(([A-Za-z0-9_.]+)\)")
        out = regexp.sub(replace_var, out)

        #regexp = re.compile(r"%p\([a-zA-Z]+\)")
        #out = regexp.sub(replace_player, template)

        # Method sub.
        #regexp = re.compile(r"%[fF]\((\w+)\)")
        #out = regexp.sub(replace_fun, out)

        return out


    def list_messages(self, player):

        # Get all the messages defined for this type of object.
        messages = getattr(MESSAGES, f"{self.typename.upper()}_MESSAGES", None)
        if not messages:
            player.msg("No messages have been configured for that type of object.")
            return

        # Loop through:q all of the defined messages for this object type.
        player.msg(f"Messages on |C{self.name_and_dbref}|n:")
        for x in messages:
            # First, attempt to find the message in a db attr on the object.
            atr = self.attributes.get(x, None)
            default = False
            if not atr:
                # Get the message from the defaults defined in messages.py. We
                # don't check for truthiness here since we want any message--
                # even a blank one-- to over-ride the default.
                atr = getattr(MESSAGES, x.upper(), None)
                default = True

            # Display the message.
            player.msg(f"  |w{x}|n: {atr if atr else ''} {'[|Cdefault|n]' if default and atr else ''}")

        # Display the "end of data" marker.
        player.msg("---")


    # Generate a message.
    def generate_message(self, message=None, omessage=None, caller=None, **kwargs):
        if not caller:
            return ''
            
        # Override loc?
        loc = kwargs.get('location', caller.location) or self.location

        # Define an indirect object?
        iobj = kwargs.get('iobj', None)
        
        # Don't show automatic messages to players set QUIET.
        quiet = caller.tags.get('quiet')
        
        if message and not quiet:
            # Grab the msg attribute.  First try the object, then check for
            # a default in the Messages module.
            a = self.attributes.get(message, None) or getattr(MESSAGES, message.upper(), None)
        
            # If 'a' is None then no message was found, so just exit. 
            # If 'a' is not None, and begins with a '@', then ignore the
            # message and exit.  This allows us to 'block' specific messages
            # on objects, even if there is a default.
            if a and not a.startswith('@'):
                msg = self.pronoun_sub(a, caller, iobj=iobj, location=loc)
                msg and caller.msg(msg)

        # We don't check quiet here because the enactor won't see this message. We sent it
        # along to msg_contents() instead and it'll be filtered there.      
        if omessage:
            # Grab the msg attribute either from the object or the messages module.
            a = self.attributes.get(omessage, None) or getattr(MESSAGES, omessage.upper(), None)

            if a and not a.startswith('@'):
                msg = f"{caller.name} {self.pronoun_sub(a, caller, iobj=iobj, location=loc)}"
                msg and loc.msg_contents(msg, exclude=caller, **{"from_obj":caller, "quiet":quiet})

def announce_move_from(self, destination, msg=None, mapping=None, **kwargs):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        Args:
            destination (Object): The place we are going to.
            msg (str, optional): a replacement message.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.

        """
        if not self.location:
            return

        location = self.location
        location.generate_message('leave', 'oleave', caller=self, location=location, iobj=destination)

        #location.msg_contents(string, exclude=(self,), from_obj=self, mapping=mapping)

def announce_move_to(self, source_location, msg=None, mapping=None, **kwargs):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.

        Args:
            source_location (Object): The place we came from
            msg (str, optional): the replacement message if location.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            You can override this method and call its parent with a
            message to simply change the default message.  In the string,
            you can use the following as mappings (between braces):
                object: the object which is moving.
                exit: the exit from which the object is moving (if found).
                origin: the location of the object before the move.
                destination: the location of the object after moving.

        """

        if not source_location and self.location.has_account:
            # This was created from nowhere and added to an account's
            # inventory; it's probably the result of a create command.
            string = "You now have %s in your possession." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        if self.location:  
            self.location.generate_message('arrive', 'oarrive', caller=self, iobj=source_location)
            #destination.msg_contents(string, exclude=(self,), from_obj=self, mapping=mapping)

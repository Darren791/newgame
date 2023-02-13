from evennia import default_cmds
from evennia.locks.lockhandler import LockException
from evennia import CmdSet
from evennia.utils import evtable
from typeclasses.characters import Character
from typeclasses.objects import Object
import world.headers as headers
from .board_utils import *
from .boards import DefaultBoard
from .models import Post

import world.utils as utils
from django.conf import settings

# Editor callback: load the text to edit into the editor.
def _bbpost_load(caller):
    return caller.db.evmenu_target.db.desc or ""


# Editor callback: save the editor text.
def _bbpost_save(caller, buf):
    """
    Save line buffer to the desc prop. This should
    return True if successful and also report its status to the user.
    """
    caller.db.evmenu_target.db.desc = buf
    caller.msg("Saved.")
    return True


# Editor callback: Leave the editor.
def _bbpost_quit(caller):
    caller.attributes.remove("evmenu_target")
    caller.msg("Exited editor.")


def is_positive_int(string):
    """
    Tests whether the given string is a plain, positive integer.

    Args:
        string (str): A string to test.

    Returns:
        True if the string is an integer greater than 0, False if not.
    """
    try:
        test = int(string)
        if test > 0:
            return True
        return False
    except ValueError:
        return False


class BoardAdminCmd(default_cmds.MuxCommand):
    """
    bbadmin/create <name>
    bbadmin/lock <board>[=lock]

    The first form of the command will create a new board.  The name must be unique,
    and cannot be solely an integer string.

    The second form of the command will set a lock for the given board.  The lock
    is a standard Evennia lock function string; the valid access types are:

       read:    ability to see/read the bboard
       post:    ability to post to the bboard
       edit:    ability to edit all posts on the bboard
       delete:  ability to delete all posts on the bboard
       pin:     ability to pin or unpin posts on the bboard

    Wizards and Immortals have all permissions by default.

    """

    key = "bbadmin"
    aliases = ["bbadmin"]
    locks = "cmd:perm(Wizards) OR perm(bbadmin)"
    help_category = "Communications"
    switch_options = ("create", "delete", "lock", "maxdays", "maxposts")

    def func(self):
        if "create" in self.switches:
            testboard = DefaultBoard.objects.get_board_exact(self.args)

            if not self.args:
                self.msg("You must provide a board name!")
                return

            if is_int(self.args):
                self.msg("A board name cannot be an integer.")
                return

            if testboard:
                self.msg("Board '" + self.args + "' already exists!")
                return

            board = DefaultBoard(db_key=self.args)
            board.save()
            self.msg("Created board '" + self.args + "'")
            return

        if "delete" in self.switches:
            board = DefaultBoard.objects.get_board(self.lhs)
            if board:
                self.msg(f"Board {board} deleted.")
                board.delete()
            else:
                self.msg("No such board.")
            return

        if "lock" in self.switches:
            if not self.args:
                self.msg("You must provide parameters!")
                return

            if not self.lhs:
                self.msg("You must provide a bboard name!")
                return

            board = DefaultBoard.objects.get_board(self.lhs)
            if not board:
                self.msg("No board matches '" + self.lhs + "'")
                return

            if not self.rhs:
                string = "Current locks on %s: %s" % (board.name, board.locks)
                self.msg(string)
                return

            try:
                board.locks.add(self.rhs)
            except (LockException, err):
                self.msg(err)
                return

            self.msg("Lock(s) applied.")
            string = "Current locks on %s: %s" % (board.name, board.locks)
            self.msg(string)
            return

        if "maxdays" in self.switches:
            if not self.args:
                self.msg("You must provide parameters!")
                return

            if not self.lhs:
                self.msg("You must provide a bboard name!")
                return

            if self.rhs and not is_positive_int(self.rhs):
                self.msg("Your max days value must be a positive integer.")
                return

            board = DefaultBoard.objects.get_board(self.lhs)
            if not board:
                self.msg("No board matches '" + self.lhs + "'")
                return

            if not self.rhs:
                board.db_expiry_duration = None
                self.msg("Cleared maximum day duration on board.")
            else:
                board.db_expiry_duration = int(self.rhs)
                self.msg(
                    "Board expiry set to " + str(board.db_expiry_duration) + " days."
                )

            board.save()
            return

        if "maxposts" in self.switches:
            if not self.args:
                self.msg("You must provide parameters!")
                return

            if not self.lhs:
                self.msg("You must provide a bboard name!")
                return

            if self.rhs and not is_positive_int(self.rhs):
                self.msg("Your max posts value must be a positive integer.")
                return

            board = DefaultBoard.objects.get_board(self.lhs)
            if not board:
                self.msg("No board matches '" + self.lhs + "'")
                return

            if not self.rhs:
                board.db_expiry_maxposts = None
                self.msg("Cleared maximum post count on board.")
            else:
                board.db_expiry_maxposts = int(self.rhs)
                self.msg(
                    "Board post maximum set to "
                    + str(board.db_expiry_maxposts)
                    + " posts."
                )

            board.save()
            return

        self.msg(
            "Unknown switch.  Please see |555help " + self.cmdstring + "|n for help."
        )


class BoardCmd(default_cmds.MuxCommand):
    """
    Paxboards is a bulletin board (forum) system for Evennia.
    
    |C[bboard [[board][/post]]
    |Cbbread [board][/post]]
        Read a post on the board.
        
    |C[bboard/post || bbpost] <board>/<subject>=<post>|n
        Create a new post on the indicated board.

    |C[bboard/sub || bbsub] <board>|n
        Subscribe to the indicated board. Subscribing means being notified
        whenever new posts are made to the board.

    |C[bboard/unsub || bbunsub] <board>|n
        Unsubscribe from a board. This means you will no longer be notified
        whenever new messages are posted to the board.

    |C[bboard/edit || bbedit] <board>/<post>=<newpost>|n
        Edit a post you have made, say, to add additonal text, or fix a typo.

    |C[bboard/delete || bbdelete] <board>/<post>|n
        Delete a post. You must have "delete" perms.

    |C[bboard/scan || bbscan] [board]|n
        Display a list of boards with unread posts.

    |C[bboard/new bboard/next || bbnew || bbnext] [board]|n
        Display the next unread post in the indicated board, or globally,
        if no parameters are given.

    |C[bboard/catchup || bbcatchup] [board or "all"]|n
        Mark all new posts as read.

    |C[bboard/search || bbsearch] [board/]<search>|n
        Search a given board for arbitrary text.

    |C[bboard/reply || bbreply] <board>/<post>=<reply>|n
        Reply to a post.


    |CCredits|n:
        This started out as Paxboards but has been refactored several times
        since then. I'm keeping the name as a nod to it's origin.
    """

    key = "bboard"
    locks = "cmd:all()"
    switch_options = ("read",
        "delete",
        "post",
        "reply",
        "edit",
        "search",
        "sub",
        "unsub",
        "catchup",
        "pin",
        "unpin",
        "new",
        "scan",
        "next"
        )

    aliases = (
        "bbread",
        "bbdelete",
        "bbpost",
        "bbreply",
        "bbedit",
        "bbsearch",
        "bbsub",
        "bbunsub",
        "bbcatchup",
        "bbpin",
        "bbunpin",
        "bbnew",
        "bbscan",
        "bbnext"
    )
    help_category = "Communications"
    arg_regex = r"(?:^(?:\s+|\/).*$)|^$"
    account_caller = True

    def resolve_id(self, string):
        """
        Helper function which, given a string, will resolve it into a board or post.
        The string should be in the format "<board>[/postnum]", where board is either
        the name of a board or a number within those the player can see, while postnum
        should be an integer.

        Args:
            string: The string to resolve

        Returns:
            A dictionary containing 'board' (for a board), 'post' (if applicable), and the
            post number (just for convenience).

        """

        readargs = string.split("/", 1)
        boardname = readargs[0]

        if not 1 <= len(readargs) <= 2:
            self.msg("Unable to parse post identifier '%s'." % string)

        postnum = 0
        if len(readargs) == 2:
            try:
                postnum = int(readargs[1])
            except ValueError:
                self.msg(
                    "The post identifier '%s' must be a positive integer." % readargs[1]
                )
                return None

        board = DefaultBoard.objects.get_visible_board(self.account, boardname)
        if not board:
            self.msg("Unable to find a board matching '%s'." % string)
            return None

        if len(readargs) == 1:
            return {"board": board, "post": None, "postnum": 0}

        posts = board.posts(self.account)

        if not (0 < postnum <= len(posts)):
            self.msg("There's no post with that number.")
            return

        post = posts[postnum - 1]

        return {"board": board, "post": post, "postnum": postnum}


    def func(self):
        caller = self.account
        switch = self.switches[0] if self.switches else None

        boards = DefaultBoard.objects.get_all_visible_boards(caller)
        shortcut = False

        if self.cmdstring in self.aliases:
            shortcut = True

        if self.cmdstring == "bbread" or switch == "read":
            self.board_read(boards)
        elif self.cmdstring in ("bbpin", "'bbunpin",) or switch in ("pin", "unpin",):
            self.board_pin(boards)
        elif self.cmdstring == "bbscan" or switch == "scan":
            self.board_scan(boards)
        elif self.cmdstring in ("bbnew", "bbnext",) or switch in ("new", "next",):
            self.board_new(boards)
        elif self.cmdstring == "bbcatchup" or switch == "catchup":
            self.board_catchup(boards)
        elif self.cmdstring == "bbpost" or switch == "post":
            self.board_post(boards)
        elif self.cmdstring == "bbreply" or switch == "reply":
            self.board_reply(boards)
        elif self.cmdstring in ("bbsub", "bbunsub",) or switch in ("sub", "unsub",):
            self.board_sub(boards)
        elif self.cmdstring == "bbsearch" or switch == "search":
            self.board_search(boards)
        elif self.cmdstring == "bbedit" or switch == "edit":
            self.board_edit(boards)
        elif self.cmdstring == "bbdelete" or switch == "delete":
            self.board_delete(boards)
        else:
            self.msg("No such command")


    def board_delete(self, boards):
        result = self.resolve_id(self.lhs)

        # No valid results
        if not result:
            return

        post = result["post"]

        # No post
        if not post:
            self.msg("You must provide a post to delete.")
            return

        if not post.has_access(self.caller, "delete"):
            self.msg("You can't delete that post!")
            return

        # TODO: Should we delete this or just unlink it?
        replies = Post.objects.filter(db_parent=post)
        for r in replies:
            r.db_parent = post.db_parent
            r.save()

        post.delete()
        self.msg("Post deleted.")
        return


    def board_edit(self, boards):
        result = self.resolve_id(self.lhs)

        # No valid results
        if not result:
            return

        post = result["post"]

        # No post
        if not post:
            self.msg("You must provide a post to edit.")
            return

        if not post.has_access(self.caller, "edit"):
            self.msg("You can't edit that post!")
            return

        post.db_text = self.rhs
        post.save()

        self.msg("Post updated.")
        return
        

    def board_search(self, boards):
        if not self.lhs:
            self.msg("You must provide a search term.")
            return

        readargs = self.lhs.split("/", 1)
        searchterm = None
        boardname = None
        board = None
        if len(readargs) == 1:
            if self.rhs:
                searchterm = self.rhs
                boardname = self.lhs
            else:
                searchterm = self.lhs
        elif len(readargs) == 2:
            searchterm = readargs[1]
            boardname = readargs[0]

        if boardname:
            board = DefaultBoard.objects.get_visible_board(self.caller, boardname)
            if not board:
                self.msg(f"Unable to find a unique board batching '{boardname}'")
                return

        posts = Post.objects.search(searchterm, board)
        if len(posts) == 0:
            self.msg("No posts matching search term.")
            return

        table = self.styled_table("", "Poster", "Subject", "Date")
        for post in posts:
            postnum = post.post_num
            if postnum:
                if boardname:
                    postid = boardname + "/" + str(postnum)
                else:
                    postid = post.db_board.name + "/" + str(postnum)
            else:
                postid = post.db_board.name

            datestring = str(post.db_date_created.year) + "/"
            datestring += str(post.db_date_created.month).rjust(2, "0") + "/"
            datestring += str(post.db_date_created.day).rjust(2, "0")

            table.add_row(postid, post.db_poster_name, post.db_subject, datestring)

        self.msg(table)
        return


    def board_sub(self, boards):
        sub = True
        if "unsub" in self.switches or self.cmdstring == "bbunsub":
            sub = False

        if not self.lhs:
            self.msg(
                f"You must provide a bboard to {'subscribe' if sub else 'unsubscribe'} to."
            )
            return

        board = DefaultBoard.objects.get_visible_board(self.caller, self.lhs)
        if not board:
            self.msg(f"Unable to find a unique board matching '{self.lhs}'.")
            return

        board.set_subscribed(self.caller, sub)
        self.msg(
            f"Subscribed to |c{board.name}|n."
            if sub
            else f"Unsubscribed from |c{board.name}|n."
        )
        return


    def board_reply(self, boards):
        if self.caller.is_guest:
            self.caller.msg("Guests may not do that.")
            return
            
        if not self.lhs:
            self.msg("You must provide a board and post to reply to.")
            return

        result = self.resolve_id(self.lhs)

        if not result:
            self.msg("You must provide a board and post to reply to.")
            return

        board = result["board"]
        post = result["post"]
        if not board:
            self.msg(f"Unable to find a board and post matching '{self.lhs}'.")
            return

        if not post:
            self.msg("You must provide a post to reply to.")
            return

        if not self.rhs:
            self.msg("You may not create an empty reply. Try adding some text.")
            return

        # Take the read permissions as a default, in case 'post' permissions aren't
        # set.  If a board has NO permissions set, it'll be accessible to everyone.
        can_read = board.access(caller, access_type="read", default=True)

        if not board.access(caller, access_type="post", default=can_read):
            self.msg("You don't have permission to post to '%s'." % board.name)
            return

        while post.db_parent:
            post = post.db_parent

        postplayer = self.account
        postobject = None
        postname = self.account.name

        if self.caller is Object or self.caller is Character:
            postobject = self.caller
            postname = postobject.name

        reply = board.create_post(
            author_name=postname,
            author_player=postplayer,
            author_object=postobject,
            subject=f"Re: {post.db_subject}",
            parent=post,
            text=self.rhs,
        )

        if reply:
            self.msg("Posted.")

        return


    def board_post(self, boards):
        if self.caller.is_guest:
            self.caller.msg("Sorry. Guests may not do that.")
            return

        if not self.lhs:
            self.msg("You must provide the name or number of the board to post to.")
            return

        readargs = self.lhs.split("/", 1)
        boardname = readargs[0]

        if len(readargs) == 1:
            self.msg("You must provide a subject.")
            return

        if not self.rhs:
            self.msg("You may not create empty posts. Try adding some text.")
            return

        board = DefaultBoard.objects.get_visible_board(self.caller, boardname)
        if not board:
            self.msg(f"Unable to find a unique board matching '{self.lhs}'.")
            return

        # Take the read permissions as a default, in case 'post' permissions aren't
        # set.  If a board has NO permissions set, it'll be accessible to everyone.
        can_read = board.access(self.caller, access_type="read", default=True)

        if not board.access(self.caller, access_type="post", default=can_read):
            self.msg(f"You don't have permission to post to '{board.name}'.")
            return

        postplayer = self.account
        postobject = None
        postname = self.account.name

        if self.caller is Character:
            postobject = self.caller
            postname = postobject.name

        post = board.create_post(
            author_name=postname,
            author_player=postplayer,
            author_object=postobject,
            subject=readargs[1],
            text=self.rhs,
        )

        if post:
            self.msg("Posted.")

        return


    def board_catchup(self, boards):
        if not self.lhs:
            self.msg(
                f"If you want to catchup all boards, do |555 {self.cmdstring} all|n."
            )
            return

        if self.lhs == "all":
            boards = DefaultBoard.objects.get_all_visible_boards(self.caller)
            for b in boards:
                b.mark_all_read(self.caller)

            self.msg("All boards marked read.")
            return

        result = self.resolve_id(self.lhs)
        board = result["board"]
        if not board:
            self.msg("Unable to find a board matching '%s'." % self.lhs)
            return

        board.mark_all_read(self.caller)
        self.msg("All posts on '%s' marked as read." % board.name)
        return


    def board_new(self, boards):
        if not self.lhs:
            for b in boards:
                if b.subscribers().filter(pk=self.caller.pk).exists():
                    posts = b.posts(self.caller)
                    for p in posts:
                        if p.is_unread:
                            p.display_post(self.caller)
                            p.mark_read(self.caller, True)
                            return

            self.msg("There are no unread posts on the bulletin board.")
            return

        result = self.resolve_id(self.lhs)
        board = result["board"]
        if not board:
            self.msg("Unable to find a board matching '" + self.lhs + "'!")
            return

        posts = board.posts(self.caller)
        postcounter = 0
        for p in posts:
            postcounter += 1
            if p.is_unread:
                p.display_post(self.caller)
                p.mark_read(self.caller, True)
                return

        self.msg("No unread posts!")
        return

    def board_scan(self, boards):
        table = self.styled_table("#", "Name", "Unread", "Total", "Sub'd")
        counter = 0
        has_unread = False
        for board in boards:
            counter += 1

            subbed = " "
            if board.subscribers().filter(pk=self.caller.pk).exists():
                subbed = "X"

            if board.unread_count > 0:
                has_unread = True
                table.add_row(
                    counter,
                    board.name,
                    board.unread_count,
                    board.total_count,
                    subbed,
                )
                
        table.reformat_column(4, width=3)
        if has_unread:
            self.msg(str(table))
        else:
            self.msg("No unread posts!")
        return
    


    def board_pin(self, boards):
        result = self.resolve_id(self.lhs)
        if not result:
            return

        post = result["post"]
        board = result["board"]

        if not post:
            self.msg("Unable to find post matching " + self.lhs)
            return

        if not board.access(self.caller, access_type="pin", default=False):
            self.msg("You don't have permission to pin posts on that board.")
            return

        pinvalue = "pin" in self.switches
        post.db_pinned = pinvalue
        post.save()

        self.msg("Pinned.") if pinvalue else self.msg("Unpinned.")
        return


    def board_read(self, boards):
        # Nothing in front of the '='
        if not self.lhs:
            if not boards:
                self.caller.msg("There are no accessible boards.")
                return

            table = self.styled_table(
                "Num", "Name", "Unread", "Total", "S", width=self.client_width()
            )
            counter = 0
            for board in boards:
                counter += 1

                subbed = " "
                if board.subscribers().filter(pk=self.caller.pk).exists():
                    subbed = "X"

                table.add_row(
                    f"{str(counter):>3}",
                    f"|w{board.name}|n",
                    board.unread_count,
                    board.total_count,
                    subbed                       
                )

                table.reformat(width=self.client_width())
                table.reformat_column(0, width=8, justify="right")
                # table.reformat_column(1, width=45)
                table.reformat_column(2, width=10)
                table.reformat_column(3, width=10)
                table.reformat_column(4, width=4, justify="center")

            self.msg(
                headers.banner(
                    f"{settings.SERVERNAME} Bulletin Board System",
                    width=self.client_width(),
                    player=self.caller
                )
            )
            
            self.msg(str(table))
            self.msg(
                headers.ubanner(
                    f"{len(boards)} board{'' if len(boards) == 1 else 's'} found.",
                    width=self.client_width(),
                    player=self.caller,
                )
            )
        else:
            result = self.resolve_id(self.lhs)

            if not result:
                return

            board = result["board"]
            post = result["post"]

            if not post:
                posts = board.posts(player=self.caller)
                if not posts:
                    self.msg("No posts on %s." % board.name)
                    return
                self.msg(self.styled_header(f"{board.name}"))
                table = self.styled_table(
                    "", "Subject", "Author", "Date", width=self.client_width()
                )
                table.reformat_column(0, width=14)
                table.reformat_column(2, width=18)
                table.reformat_column(3, width=14)
                counter = 0
                for post in posts:
                    counter += 1

                    unreadstring = "  "
                    if post.is_unread:
                        unreadstring = "|555*|n "

                    datestring = str(post.db_date_created.year) + "/"
                    datestring += (
                        str(post.db_date_created.month).rjust(2, "0") + "/"
                    )
                    datestring += str(post.db_date_created.day).rjust(2, "0")

                    table.add_row(
                        unreadstring + self.lhs + "/" + str(counter),
                        f"|C{post.subject}|n",
                        post.db_poster_name,
                        datestring,
                    )

                self.msg(str(table))
                self.msg(self.styled_footer())
                self.caller.attributes.add("_bb_read", (board.id, post.id))
            else:
                if "thread" in self.switches:
                    while post.db_parent:
                        post = post.db_parent

                post.display_post(self.caller, show_replies=("thread" in self.switches))
                post.db_readers.add(self.caller)
                post.save()

                return



class BoardCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(BoardAdminCmd())
        self.add(BoardCmd())
"""
  A basic news system.

  Written by Darren@SeventhSea MUSH.
"""

from evennia import default_cmds, ObjectDB
from evennia.comms.models import Msg
from evennia.utils import create, datetime_format
from evennia.utils.ansi import ANSIString
from django.conf import settings
from world.headers import banner


class CmdNews(default_cmds.MuxCommand):
    """
    Syntax: news
            news ##
            news/add subject=body
            news/purge
            news/remove ##
            news/list

    When called with no arguments, displays the list of available news
    articles.  To read a news item, give the number of the post that you
    want to read e.g. `news 1` to read the first article.

    Switches
      list   - Display all news.
      purge  - Deletes all new articles. Requires Admin perms.
      add    - Creates a new news article. Requires Admin perms.
      remove - Deletes a news article. Requires Admin perms.

    """

    key = "news"
    locks = "cmd:all()"
    help_category = "Comms"
    switch_options = ("add", "remove", "purge", "list")

    # Can this player create new posts?
    def can_post(self, who):
        if who.is_superuser:
            return True
        if who.account.permissions.get("Admin"):
            return True
        if who.permissions.get("news_editor"):
            return True
        return False

    # Can this player read this post?
    def can_read(self, who, what=None):
        return True

    # Can this player delete a post?
    def can_delete(self, who, what):

        if who.is_superuser:
            return True

        if who.account.permissions.get("Admin"):
            who.msg("debug: news perms Admin")
            return True

        if who.permsions.get("news_editor"):
            who.msg("debug: news perms news_editor")
            return True

        if what.tags.get("sticky", category="news"):
            who.msg("debug: not admin and not news_editor and sticky post")
            return False

        return False

    # Read a news post.
    def do_read(self):
        # Ensure they passed a number otherwise int() will raise an error.
        # We use abs() here to ensure they don't enter a negative number,
        # which would skew our results since we're using it as an array
        # index.
        try:
            index = abs(int(self.args))
        except ValueError:
            self.caller.msg("Article index must be a number.")
            return

        # Find all news articles. This returns a QuerySet.
        news = self.get_all_news()

        # Make sure there is some news.
        if news.count() == 0:
            # If the QuerySet is empty, then there isn't any news.  Complain and
            # exit.
            self.caller.msg("There isn't any news.")
            return

        # Python starts counting at 0 rather than 1 so we need to convert
        # the number that the player gave us.  Make sure it's over 0 first
        # otherwise we'll end up with a negative number which will pull
        # articles from the back of the list rather than the front.
        if index > 0:
            index -= 1

        # Ensure that the index is within range.  We use news.count() rather
        # than len(news) here to prevent unnecessary evaluation of the
        # QuerySet.
        if index < 0 or index >= news.count():
            self.caller.msg("Article index out of range.")
            return

        # Get the article
        message = news[index]
        out = []

        if not self.can_read(self.caller):
            self.caller.msg("Sorry. You do not have permission to read that post.")
            return

        # Display the article
        out.append(
            banner(f"{settings.SERVERNAME} News System", player=self.caller, width=79)
        )
        out.append(self.styled_separator(message.header, width=79))
        out.append(message.message)
        out.append(self.styled_footer(f"{index+1} of {news.count()}", width=79))
        self.caller.msg(ANSIString("\n").join(out))

    def send_news(self, subject, message, caller):
        new_message = create.create_message(
            self.caller, message, receivers=None, header=subject
        )
        new_message.tags.add("news", category="news")

        if new_message:
            caller.msg("Your news article has been published.")

    def get_all_news(self):
        """
        This probably doesn't need it's own function but it will
        make it easier to update the query should that become
        necessary.
        """
        return Msg.objects.get_by_tag(category="news")

    # Create a new article.

    def do_add(self):

        if not self.can_post(self.caller):
            self.caller.msg("You do not have permission to publish news articles.")
            return

        # Make sure they gave a subject.
        if not self.lhs:
            self.caller.msg("The article subject cannot be blank.")
            return

        # Make sure the article isn't empty.
        if not self.rhs:
            self.caller.msg("The article body must contain some text.")
            return

        # Create the news article.
        self.send_news(self.lhs, self.rhs, self.caller)

    def do_remove(self):
        """Delete a news article"""

        if (not self.caller.is_superuser) and (
            self.caller.account.permissions.get("Admin")
        ):
            self.caller.msg("You do not have permission to delete news articles.")
            return

        # Ensure they supplied an arg.
        if not self.args:
            self.caller.msg("You must give the news article to be removed.")
            return

        # Convert the arg into a number.
        try:
            index = abs(int(self.args))
        except ValueError:
            self.caller.msg("The article index must be a number.")
            return

        # Get all the news. This returns a QuerySet.
        news = self.get_all_news()
        if not news:
            self.caller.msg("There isn't any news.")
            return

        if index > 0:
            index -= 1

        # Make sure that it's within range.
        if index < 0 or index >= news.count():
            self.caller.msg(f"The article index must be between 1 and {news.count()}.")
            return

        # Grab the article.
        article = news[index]

        # This shouldn't be necessary as an error would be thrown if the
        # preceeding statement failed but eh, years of paranoia from writing
        # mainly in C...
        if article:
            # Delete the article.
            article.delete()

            # Let the player know they succeeded.
            self.caller.msg(f"News article {index+1} deleted.")

    # Delete all news.

    def do_purge(self):
        if (not self.caller.is_superuser) and (
            not self.caller.account.permissions.get("Admin")
        ):
            self.caller.msg("You do not have permission to delete news articles,")
            return

        news = self.get_all_news()
        if not news:
            self.caller.msg("There isn't any news.")
            return

        for x in news:
            x.delete()

        self.caller.msg("All news articles purged.")

    # Display a list of news articles.
    def do_list(self):

        # Get all news. This returns a QuerySet.
        news = self.get_all_news()

        # Make sure there is some news.
        if news.count() == 0:
            self.caller.msg("There isn't any news.")
            return

        index = 1

        # Create a table.
        table = self.styled_table("ID", "Subject", "Date", width=79)
        # Make it the player's screenwidth.
        table.reformat(width=79)

        # Add each article to the table.
        for message in news:
            table.add_row(
                str(index), message.header, message.db_date_created.strftime("%x")
            )
            index += 1

        # Fix the formatting for a prettier display.
        table.reformat_column(0, width=8, align="r")
        table.reformat_column(2, width=12)

        # Display a header.
        # self.caller.msg(self.styled_header("Available News Articles"))
        self.caller.msg(banner("Available News Articles", player=self.caller, width=79))

        # Display the table of news articles.
        self.caller.msg(str(table))

    # Command entrypoint.
    def func(self):
        if not self.switches:
            if not self.args:
                switch = "list"
            else:
                switch = "read"
        else:
            switch = self.switches[0]

        # We could just use switches here but eh, this is more fun (lol).
        try:
            fun = getattr(self, f"do_{switch}")
        except AttributeError:
            self.caller.msg("No handler has been defined for this switch.")
            return

        if callable(fun):
            fun()
        else:
            self.caller.msg("Handler is not a callable object.")

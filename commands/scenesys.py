 
from evennia import ObjectDB, DefaultRoom, DefaultCharacter, default_cmds


class CmdScene(default_cmds.MuxCommand):
    """
    The SceneSys is a work in progress!
    
    Syntax:
      scene||scene/list		: Display all public scenes.

      scene/start		: Start a new scene.  This spawns a copy of the
                                  current room with all descriptions, etc
                                  intact and moves you to it.
                                  
      scene/invite <who>	: Invite a player/list of players to your scene.
      
      scene/kick <reason>	: Kick someone out of your scene.  You must
                                  provide a reason.  
                                  
      scene/log			: Toggles logging in the room.
      scene/stop		: Stop (closes) a scene.
      scene/leave		: Returns you to the original room.
      scene/recall <lines>	: Recalls logging The default is 20 lines.

      scene/private		: Marks the scene as private, meaning that
                                  only those participants you have invited,
                                  will be able to join.
      
    """
    
    key = "scene"
    aliases = "scenes"
    help_category="General"
    switch_options = ("start", "stop", "invite", "kick", "list", "private")
    
    def can_start_scene(self, who: DefaultCharacter) -> bool:
        pass
        
    def can_stop_scene(self, who: DefaultCharacter) -> bool:
        pass
        
    def can_invite(self, who: DefaultCharacter) -> bool:
        pass
        
    def can_kick(self, who: DefaultCharacter) -> bool:
        pass
        

    def do_invite(self):
        pass
        
    def do_start(self):
        pass
        
    def do_stop(self):
        pass
        
    def do_kick(self):
        pass
        
    def do_private(self):
        pass

    def make_temp_room(self):
        pass

    def func(self):
        switch = "list" if not self.switches else self.switches[0]
        caller = self.caller
        caller.msg(f"Switch={switch}")





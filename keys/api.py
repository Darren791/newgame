from .models import KeyDB
import world.utils as myutils
from typeclasses.characters import Character

def match_key(key: str, player: Character) -> KeyDB:
    ret = None
    i: int = 0

    if i := myutils.parse_int_or_dbref(key):
        try:
            key = KeyDB.objects.get(pk=i)
        except:
            pass
        
        if key and key.holder is player:
            ret = key
    else:
        key = KeyDB.objects.filter(key__startswith=key, holder=player)
        if key.count() == 1:
            ret = key.first()
    
    return ret

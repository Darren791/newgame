from .models import KeyDB

class KeyHandler(object):
    def __init__(self, obj):
        self.obj = obj
        self.cache = []
        self.init_cache()

    def init_cache(self):
        self.cache = [x.target for x in KeyDB.objects.filter(
            holder=self.obj, pending=False)]

    def add(self, key):
        if key and not key in self.cache:
            self.cache.add(key)

    def remove(self, key):
        if key and key in self.cache:
            self.cache.remove(key)

    def has_key_for(self, thing):
        return True if (self.cache and self.cache.count(thing)) else False

    def all(self):
        return self.cache or []

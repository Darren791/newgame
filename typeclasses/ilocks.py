"""
"""


class iLockManager():
    """
    """

    def __init__(self, obj):
        """
        """
        self.obj = obj
        self.cache = set()
        self.load()

    def add(self, what):
        """
        """
        if what and what.is_character:
            self.cache.add(what)
            self.save()

    def save(self):
        """
        """
        self.obj.attributes.add("blocklist", self.cache or set())

    def reset_cache(self):
        """
        """
        if self.cache:
            self.cache.clear()
        else:
            self.cache = set()
        self.obj.attributes.remove("blocklist")

    def load(self):
        """
        """
        self.cache = self.obj.attributes.get("blocklist", set())

    def remove(self, what):
        """
        """
        if what:
            self.cache.discard(what)
            self.save()

    def all(self):
        """
        """
        return set(self.cache)

    def __len__(self):
        """
        """
        return len(self.cache)

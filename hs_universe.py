class HS_Universes:
    objlist = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(SingletonClass, cls).__new__(cls)
          cls.objlist = []
        return cls.isinstance

    def add_to_universe(self, cls):
        pass

    def remove_from_universe(self, cls):
        pass

    def all(self):
        return self.objlist

class Universe:
    name = "New Universe"
    num = 0
    objlist = []

    def __init__(self):
        self.name = ""
        self.num = len(self.objlist) + 1


def init_universes():
  pass





hs = Universe()
print(hs)

hs2=Universe()
print(hs2)

print(hs == hs2)
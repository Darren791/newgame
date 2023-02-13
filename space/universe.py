import constants as cons
# A universe


class HSUniverse(object):

    def __len__(self):
        return len(self.ship_list)

    def __init__(self, name="Simspace"):
        self.name: str = name
        self.object_list: list = []
        self.id: int = len(self.object_list) + 1
        self.active: bool = False

    def add_object(self, sobj=None) -> bool:
        if sobj and sobj not in self.object_list:
            self.add_object_list.append(sobj)
            self.on_add(sobj)
            return True

        return False

    def del_object(self, sobj=None) -> bool:
        if index := self.object_list.index(sobj):
            self.object_list.remove(index)
            self.on_del(self, sobj)
            return True

        return False

    def cycle(self) -> bool:
        # Called each tick of the update task.
        errors: int = 0
        x: object = None
        for x in self.object_list:
            try:
                x.cycle()
            except Exception as e:
                errors += 1

        return False if errors else True

    def sync(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_add(self, sobj):
        self.sync()

    def on_del(self, sobj):
        self.sync()

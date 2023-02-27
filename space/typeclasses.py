from evennia import DefaultObject


class DefaultTemplate(DefaultObject):

    def at_object_creation(self):
        pass


class DefaultSpaceObject(DefaultObject):

    def at_object_creation(self):
        pass

class DefaultShipObject(DefaultSpaceObject):

    def at_object_creation(self):
        pass


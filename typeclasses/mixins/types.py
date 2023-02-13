class TypeMixins(object):
    @property
    def is_guest(self):
        return False

    @property
    def is_room(self):
        return False

    @property
    def is_character(self):
        return False

    @property
    def is_account(self):
        return False

    @property
    def is_thing(self):
        return False

    @property
    def is_place(self):
        return False

    @property
    def is_exit(self):
        return False

    @property
    def is_guest_account(self):
        return False        
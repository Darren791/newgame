class OwnerMixins(object):

    def manager(self):
        return self.db.owner or None

    def init_owner(self, **kwargs):
        creator = self._createdict["report_to"] if hasattr(self, "_createdict") else None
        if not creator:
            return
        else:
            if hasattr(creator, "account"):
                self.tags.add(f"#{creator.account.id}", "owner")
            else:
                self.tags.add(f"#{creator.id}", "owner")
            self.db.owner = creator
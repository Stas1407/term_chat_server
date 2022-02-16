
class Room:
    def __init__(self, name, is_public):
        self.name = name
        self.is_public = is_public
        self.members = []
    
    def number_of_members(self):
        return len(self.members)

    def join(self, member):
        self.members.append(member)

    def leave(self, member):
        self.members.remove(member)

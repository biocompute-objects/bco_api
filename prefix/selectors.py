

def is_accessible_by(self, user):
    """If no authorized_groups are specified, it's accessible by everyone"""
    if self.authorized_users.exists():
        return self.authorized_users.filter(id=user.id).exists()
    return True
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


ROLE_TO_GROUP = {
    User.Role.READER: "Readers",
    User.Role.JOURNALIST: "Journalists",
    User.Role.EDITOR: "Editors",
}


@receiver(post_save, sender=User)
def sync_user_group(sender, instance: User, created: bool, **kwargs) -> None:
    """
    Ensure the user belongs to the group that matches their role.
    Removes the user from the other role groups to keep things consistent.
    """
    target_group_name = ROLE_TO_GROUP.get(instance.role)
    if not target_group_name:
        return

    target_group, _ = Group.objects.get_or_create(name=target_group_name)

    role_group_names = set(ROLE_TO_GROUP.values())
    groups_to_remove = instance.groups.filter(name__in=role_group_names).exclude(
        name=target_group_name
    )
    if groups_to_remove.exists():
        instance.groups.remove(*groups_to_remove)

    if not instance.groups.filter(name=target_group_name).exists():
        instance.groups.add(target_group)

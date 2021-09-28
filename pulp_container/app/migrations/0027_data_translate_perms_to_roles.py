# Generated by Django 3.2.10 on 2022-01-21 17:54

import re
from django.conf import settings
from django.db import migrations


CONTAINER_VIEWSET_NAMES = [
    "content/container/blobs",
    "content/container/manifests",
    "content/container/tags",
    "contentguards/core/rbac",
    "distributions/container/container",
    "pulp_container/namespaces",
    "remotes/container/container",
    "repositories/container/container",
    "repositories/container/container-push",
    "repositories/container/container-push/versions",
    "repositories/container/container/versions",
]

CONTAINER_NAMESPACE_ROLE_TRANSLATOR = {
    "owners": "container.containernamespace_owner",
    "collaborators": "container.containernamespace_collaborator",
    "consumers": "container.containernamespace_consumer",
}

CONTAINER_DISTRIBUTION_ROLE_TRANSLATOR = {
    "owners": "container.containerdistribution_owner",
    "collaborators": "container.containerdistribution_collaborator",
    "consumers": "container.containerdistribution_consumer",
}

# app_label, codename, rolename
GLOBAL_PERMISSION_ROLE_TRANSLATOR = [
    ("container", "add_containerremote", "container.containerremote_creator"),
    ("container", "add_containerrepository", "container.containerrepository_creator"),
    ("container", "add_containerdistribution", "container.containerdistribution_creator"),
    ("container", "add_containernamespace", "container.containernamespace_creator"),
]

# list_of((app_label, codename)), rolename
# !!! ORDER MATTERS !!!
# This should only contain objects for which we didn't create groups
OBJECT_PERMISSION_ROLE_TRANSLATOR = [
    ((
        ("container", "view_containerremote"),
        ("container", "change_containerremote"),
        ("container", "delete_containerremote"),
    ), "container.containerremote_owner"),
    ((
        ("container", "view_containerremote"),
    ), "container.containerremote_viewer"),
    ((
        ("container", "view_containerrepository"),
        ("container", "change_containerrepository"),
        ("container", "delete_containerrepository"),
        ("container", "delete_containerrepository_versions"),
        ("container", "sync_containerrepository"),
        ("container", "modify_content_containerrepository"),
        ("container", "build_image_containerrepository"),
    ), "container.containerrepository_owner"),
    ((
        ("container", "view_containerrepository"),
        ("container", "delete_containerrepository_versions"),
        ("container", "sync_containerrepository"),
        ("container", "modify_content_containerrepository"),
        ("container", "build_image_containerrepository"),
    ), "container.containerrepository_content_manager"),
    ((
        ("container", "view_containerrepository"),
    ), "container.containerrepository_viewer"),
]


def translate_groups_to_roles(apps, schema_editor):
    AccessPolicy = apps.get_model("core", "AccessPolicy")
    if any(AccessPolicy.objects.filter(viewset_name__in=CONTAINER_VIEWSET_NAMES).values_list("customized", flat=True)):
        print("Container access policies have been modified. Translating the auto-generated grous to roles will not be attemted.")
        return

    ContentType = apps.get_model("contenttypes", "ContentType")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Group = apps.get_model("core", "Group")
    Role = apps.get_model("core", "Role")
    UserRole = apps.get_model("core", "UserRole")
    ContainerNamespace = apps.get_model("container", "ContainerNamespace")
    ContainerDistribution = apps.get_model("container", "ContainerDistribution")
    namespace_ctype = ContentType.objects.get_for_model(ContainerNamespace, for_concrete_model=False)
    distribution_ctype = ContentType.objects.get_for_model(ContainerDistribution, for_concrete_model=False)

    user_roles = []
    groups_to_delete = set()

    # Find namespace groups and transform into user roles
    name_expression = re.compile(r"^container\.namespace\.(.*)\.(.*)")
    for group in Group.objects.filter(name__startswith="container.namespace."):
        match = name_expression.match(group.name)
        if match:
            role_type = match.group(1)
            name = match.group(2)
            namespace = ContainerNamespace.objects.get(name=name)
            role_name = CONTAINER_NAMESPACE_ROLE_TRANSLATOR.get(role_type)
            if role_name:  # Auto-generated group has been identified
                if group.user_set.exists():  # It has users; need to assign the role
                    role, _ = Role.objects.get_or_create(name=role_name, defaults={"locked": True})
                    user_roles.extend((UserRole(user=user, role=role, content_type=namespace_ctype, object_id=namespace.pk) for user in group.user_set.all()))
                groups_to_delete.add(group.pk)

        # Handle batches
        if len(user_roles) > 1000:
            UserRole.objects.bulk_create(user_roles)
            user_roles.clear()
        if len(groups_to_delete) > 1000:
            Group.objects.filter(pk__in=groups_to_delete).delete()
            groups_to_delete.clear()

    # Find distribution groups and transform into user roles
    name_expression = re.compile(r"^container\.distribution\.(.*)\.(.*)")
    for group in Group.objects.filter(name__startswith="container.distribution."):
        match = name_expression.match(group.name)
        if match:
            role_type = match.group(1)
            uuid = match.group(2)
            distribution = ContainerDistribution.objects.get(pk=uuid)
            role_name = CONTAINER_DISTRIBUTION_ROLE_TRANSLATOR.get(role_type)
            if role_name:  # Auto-generated group has been identified
                if group.user_set.exists():  # It has users; need to assign the role
                    role, _ = Role.objects.get_or_create(name=role_name, defaults={"locked": True})
                    user_roles.extend((UserRole(user=user, role=role, content_type=distribution_ctype, object_id=distribution.pk) for user in group.user_set.all()))
                groups_to_delete.add(group.pk)

        # Handle batches
        if len(user_roles) > 1000:
            UserRole.objects.bulk_create(user_roles)
            user_roles.clear()
        if len(groups_to_delete) > 1000:
            Group.objects.filter(pk__in=groups_to_delete).delete()
            groups_to_delete.clear()

    # Persist leftovers
    UserRole.objects.bulk_create(user_roles)
    Group.objects.filter(pk__in=groups_to_delete).delete()


def translate_permissions_to_roles(apps, schema_editor):
    AccessPolicy = apps.get_model("core", "AccessPolicy")
    if any(AccessPolicy.objects.filter(viewset_name__in=CONTAINER_VIEWSET_NAMES).values_list("customized", flat=True)):
        print("Container access policies have been modified. Translating the assigned permissions to roles will not be attemted.")
        return

    ContentType = apps.get_model("contenttypes", "ContentType")
    User = apps.get_model(settings.AUTH_USER_MODEL)

    Group = apps.get_model("core", "Group")
    Role = apps.get_model("core", "Role")
    UserRole = apps.get_model("core", "UserRole")
    GroupRole = apps.get_model("core", "GroupRole")
    Permission = apps.get_model("auth", "Permission")
    UserPermission = apps.get_model(User.user_permissions.through._meta.app_label, User.user_permissions.through._meta.model_name)
    GroupPermission = apps.get_model("auth", "Group_permissions")
    UserObjectPermission = apps.get_model("guardian", "UserObjectPermission")
    GroupObjectPermission = apps.get_model("guardian", "GroupObjectPermission")
    ContainerNamespace = apps.get_model("container", "ContainerNamespace")
    ContainerDistribution = apps.get_model("container", "ContainerDistribution")

    user_roles = []
    group_roles = []

    # Find global permissions and transform into user/group roles
    for app_label, codename, role_name in GLOBAL_PERMISSION_ROLE_TRANSLATOR:
        perm = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if perm:
            role, _ = Role.objects.get_or_create(name=role_name, defaults={"locked": True})
            user_permissions = UserPermission.objects.filter(permission=perm)
            user_roles.extend(UserRole(user=user_permission.user, role=role) for user_permission in user_permissions)
            user_permissions.delete()
            group_permissions = GroupPermission.objects.filter(permission=perm)
            group_roles.extend(GroupRole(group=group_permission.group, role=role) for group_permission in group_permissions)
            group_permissions.delete()

            # Handle batches
            if len(user_roles) > 1000:
                UserRole.objects.bulk_create(user_roles)
                user_roles.clear()
            if len(group_roles) > 1000:
                GroupRole.objects.bulk_create(group_roles)
                group_roles.clear()

    # Find object permissions and transform into user/group roles
    for permission_names, rolename in OBJECT_PERMISSION_ROLE_TRANSLATOR:
        perms = [Permission.objects.filter(content_type__app_label=app_label, codename=codename).first() for app_label, codename in permission_names]
        if all(perms):
            for uop in UserObjectPermission.objects.filter(permission=perms[0]):
                other_uop = [
                    UserObjectPermission.objects.filter(permission=perm, user=uop.user, content_type=uop.content_type, object_pk=uop.object_pk).first()
                    for perm in perms[1:]
                ]
                if all(other_uop):
                    user_roles.append(UserRole(user=uop.user, role=role, content_type=uop.content_type, object_id=uop.object_pk))
                    uop.delete()
                    [uop.delete() for uop in other_uop]

            for gop in GroupObjectPermission.objects.filter(permission=perms[0]):
                other_gop = [
                    GroupObjectPermission.objects.filter(permission=perm, group=gop.group, content_type=gop.content_type, object_pk=gop.object_pk).first()
                    for perm in perms[1:]
                ]
                if all(other_gop):
                    group_roles.append(GroupRole(group=gop.group, role=role, content_type=gop.content_type, object_id=gop.object_pk))
                    gop.delete()
                    [gop.delete() for gop in other_gop]

            # Handle batches
            if len(user_roles) > 1000:
                UserRole.objects.bulk_create(user_roles)
                user_roles.clear()
            if len(group_roles) > 1000:
                GroupRole.objects.bulk_create(group_roles)
                group_roles.clear()

    # Persist leftovers
    UserRole.objects.bulk_create(user_roles)
    GroupRole.objects.bulk_create(group_roles)


class Migration(migrations.Migration):

    dependencies = [
        ('container', '0026_manifest_signing_service'),
        ('core', '0080_proxy_group_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('guardian', '0002_generic_permissions_index'),
    ]

    operations = [
        migrations.RunPython(code=translate_groups_to_roles, reverse_code=migrations.RunPython.noop, elidable=True),
        migrations.RunPython(code=translate_permissions_to_roles, reverse_code=migrations.RunPython.noop, elidable=True),
    ]

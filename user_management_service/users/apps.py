from django.apps import AppConfig
from django.db.models.signals import post_migrate
import uuid

def create_default_admin_role(sender, **kwargs):
    from users.models.role import Role, Permission

    # Ensure default permissions exist
    permissions = ["manage_users", "view_reports", "edit_settings"]
    permission_objs = []
    
    for perm in permissions:
        obj, _ = Permission.objects.get_or_create(name=perm, defaults={"description": f"Allows {perm}"})
        permission_objs.append(obj)

    # Create default admin role if it doesn't exist
    admin_role, created = Role.objects.get_or_create(
        name="Admin",
        defaults={"id": uuid.uuid4(), "description": "Administrator with full access"},
    )

    if created:
        admin_role.permissions.set(permission_objs)
        print("Default Admin role created.")

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        post_migrate.connect(create_default_admin_role, sender=self)

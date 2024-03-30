from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, registration_number, first_name, last_name, role, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        if not first_name:
            raise ValueError("First name is required")
        if not first_name:
            raise ValueError("Last name is required")
        if not registration_number:
            raise ValueError("Registration number is required")
        if not role:
            role = 'Stu'

        email = self.normalize_email(email)
        user = self.model(email=email, registration_number=registration_number, first_name=first_name, last_name=last_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, registration_number, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_user(email, registration_number, first_name, last_name, 'Org', password, **extra_fields)

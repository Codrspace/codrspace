from django.contrib.auth.models import User


class ModelBackend(object):
    """
    Custom authentiction backend
    """
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username=None, password=None, user=None):
        """
        Modified version of django's authenticate.

        Will accept a user object, bypassing the password check.
        Returns the user for auto_login purposes
        """
        if user:
            if hasattr(user, 'auto_login'):
                if not user.is_anonymous() and user.auto_login:
                    return user
        else:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

from src.services.auth import (
    authenticateUser,
    logout,
    getUserFromSession,
    getCurrentSession,
)


class AuthController:
    def login(self, username, password):
        """Authenticates a user and starts a session."""
        try:
            return authenticateUser(username, password)
        except Exception:
            return False

    def logout(self):
        """Ends the current user session."""
        try:
            logout()
            return True
        except Exception:
            return False

    def get_current_user(self):
        """Retrieves information about the currently logged-in user."""
        try:
            return getUserFromSession()
        except Exception:
            return None

    def is_authenticated(self):
        """Checks if a user is currently logged in."""
        try:
            return getCurrentSession() is not None
        except Exception:
            return False

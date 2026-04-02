from src.services.user import (
    addUser,
    deleteUser,
    getAllUsers,
    getUser,
    updateUser,
)


class UserController:
    def get_users(self, query="", user_type="all"):
        users = getAllUsers(user_type)
        rows = [self._orm_to_dict(u) for u in users]

        normalized_query = (query or "").strip().lower()
        if normalized_query:
            rows = [
                u
                for u in rows
                if normalized_query in u["name"].lower()
                or normalized_query in (u["email"] or "").lower()
                or normalized_query in (u["contact"] or "").lower()
                or normalized_query in (u["address"] or "").lower()
                or normalized_query in (u["date"] or "").lower()
            ]
        return rows

    def get_user_by_id(self, user_id):
        return getUser(user_id)

    def validate_user_form(self, name, email, contact=None, address=None, user_type="user"):
        errors = {}

        cleaned_name = (name or "").strip()
        if not cleaned_name:
            errors["name"] = "Name is required"

        cleaned_email = (email or "").strip().lower()
        if not cleaned_email:
            errors["email"] = "Email is required"
        elif "@" not in cleaned_email or "." not in cleaned_email:
            errors["email"] = "Invalid email address"

        cleaned_contact = (contact or "").strip()
        if cleaned_contact and not cleaned_contact.isdigit():
            errors["contact"] = "Contact must be numeric"

        payload = {
            "name": cleaned_name,
            "email": cleaned_email,
            "contact": cleaned_contact or None,
            "address": (address or "").strip() or None,
            "user_type": user_type,
        }
        return len(errors) == 0, errors, payload

    def save_user(self, user_id, name, email, contact=None, address=None, user_type="user"):
        is_valid, errors, payload = self.validate_user_form(
            name=name,
            email=email,
            contact=contact,
            address=address,
            user_type=user_type,
        )
        if not is_valid:
            return False, "Please fix errors.", errors

        try:
            if user_id:
                updateUser(user_id, **payload)
                return True, "User updated successfully.", {}

            addUser(**payload)
            return True, "User added successfully.", {}
        except ValueError as exc:
            return False, str(exc), {}

    def delete_user(self, user_id):
        try:
            deleteUser(user_id)
            return True, "User deleted successfully."
        except Exception as exc:
            return False, str(exc)

    def _orm_to_dict(self, user):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "contact": user.contact or "",
            "address": user.address or "",
            "date": user.date.strftime("%Y-%m-%d %H:%M:%S") if user.date else "",
            "type": user.type,
        }

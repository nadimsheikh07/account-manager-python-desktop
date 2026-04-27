from src.services.category import (
    addCategory,
    deleteCategory,
    getAllCategories,
    getCategory,
    updateCategory,
)


class CategoryController:
    def get_categories(self, query=""):
        categories = getAllCategories()
        rows = [self._orm_to_dict(c) for c in categories]

        normalized_query = (query or "").strip().lower()
        if normalized_query:
            rows = [
                item
                for item in rows
                if normalized_query in item["name"].lower()
                or normalized_query in (item["description"] or "").lower()
                or normalized_query in str(item["tax"])
            ]
        return rows

    def get_category_by_id(self, category_id):
        return getCategory(category_id)

    def validate_category_form(self, name, description=None, parent_id=None, tax_text="0"):
        errors = {}

        cleaned_name = (name or "").strip()
        if not cleaned_name:
            errors["name"] = "Name is required"

        cleaned_tax_text = (tax_text or "").strip()
        parsed_tax = None
        try:
            parsed_tax = float(cleaned_tax_text or "0")
            if parsed_tax < 0:
                raise ValueError
        except ValueError:
            errors["tax"] = "Invalid tax"

        payload = {
            "name": cleaned_name,
            "description": (description or "").strip() or None,
            "parent_id": parent_id,
            "tax": parsed_tax,
        }
        return len(errors) == 0, errors, payload

    def save_category(self, category_id, name, description=None, parent_id=None, tax_text="0"):
        is_valid, errors, payload = self.validate_category_form(
            name=name,
            description=description,
            parent_id=parent_id,
            tax_text=tax_text,
        )
        if not is_valid:
            return False, "Please fix errors.", errors

        try:
            if category_id:
                updateCategory(category_id, **payload)
                return True, "Category updated successfully.", {}
            
            addCategory(
                payload["name"],
                payload["description"],
                payload["parent_id"],
                payload["tax"],
            )
            return True, "Category added successfully.", {}
        except ValueError as exc:
            return False, str(exc), {}

    def delete_category(self, category_id):
        try:
            deleteCategory(category_id)
            return True, "Category deleted successfully."
        except Exception as exc:
            return False, str(exc)

    def _orm_to_dict(self, category):
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description or "",
            "tax": category.tax,
            "parent_id": category.parent_id,
            "date": category.date.strftime("%Y-%m-%d %H:%M:%S") if category.date else "",
        }

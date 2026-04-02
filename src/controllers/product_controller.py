from src.services.product import (
    addProduct,
    deleteProduct,
    getAllProducts,
    getProduct,
    updateProduct,
)
from src.services.category import getAllCategories


class ProductController:
    def get_categories(self):
        return getAllCategories()

    def get_product_by_id(self, product_id):
        return getProduct(product_id)

    def get_products(self, query=""):
        products = getAllProducts()
        rows = [self._orm_to_dict(p) for p in products]

        normalized_query = (query or "").strip().lower()
        if normalized_query:
            rows = [
                item
                for item in rows
                if normalized_query in item["name"].lower()
                or normalized_query in (item["sku"] or "").lower()
                or normalized_query in str(item["price"])
            ]
        return rows

    def validate_product_form(self, name, price_text, category_id):
        errors = {}

        cleaned_name = (name or "").strip()
        if not cleaned_name:
            errors["name"] = "Name is required"

        cleaned_price_text = (price_text or "").strip()
        parsed_price = None
        try:
            parsed_price = float(cleaned_price_text)
            if parsed_price < 0:
                raise ValueError
        except ValueError:
            errors["price"] = "Invalid price"

        if not category_id:
            errors["category"] = "Category is required"

        payload = {
            "name": cleaned_name,
            "sku": None,
            "price": parsed_price,
            "category_id": category_id,
        }
        return len(errors) == 0, errors, payload

    def save_product(self, product_id, name, sku, price_text, category_id):
        is_valid, errors, payload = self.validate_product_form(
            name=name, price_text=price_text, category_id=category_id
        )
        if not is_valid:
            return False, "Please fix errors.", errors

        payload["sku"] = (sku or "").strip() or None
        try:
            if product_id:
                updateProduct(product_id, **payload)
                return True, "Product updated successfully.", {}
            addProduct(
                payload["name"],
                payload["category_id"],
                payload["price"],
                payload["sku"],
            )
            return True, "Product added successfully.", {}
        except ValueError as exc:
            return False, str(exc), {}

    def delete_product(self, product_id):
        deleteProduct(product_id)
        return True, "Product deleted successfully."

    def _orm_to_dict(self, product):
        return {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": product.price,
            "category": getattr(product.category, "name", "") or "",
        }

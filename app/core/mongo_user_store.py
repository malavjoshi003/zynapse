"""
MongoDB User Store — ZYNAPSE
Replaces CSV-backed user_store.py with MongoDB collections.
"""

import hashlib
import logging
from datetime import datetime

from pymongo.errors import PyMongoError

from app.core.database import (
    users_col,
    user_products_col,
    products_col,
)

logger = logging.getLogger(__name__)


def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================= USERS =================

def get_user(email):
    return users_col().find_one(
        {"email": email.lower()},
        {"_id": 0},
    )


def register_user(
    email,
    password,
    name,
    phone="",
    department="",
    city="",
    role="Analyst",
):
    if get_user(email):
        return None, "Email already registered"

    doc = {
        "email": email.lower(),
        "password_hash": _hash(password),
        "name": name,
        "phone": phone,
        "department": department,
        "city": city,
        "role": role,
        "joined": datetime.now().strftime("%Y-%m-%d"),
    }

    users_col().insert_one(doc)
    return get_user(email), None


def login_user(email, password):
    user = get_user(email)

    if not user:
        return None, "Email not found"

    if user["password_hash"] != _hash(password):
        return None, "Incorrect password"

    return user, None


def update_user(email, updates):
    user = get_user(email)

    if not user:
        return None, "User not found"

    set_fields = {}
    allowed = ["name", "phone", "department", "city", "role"]

    for key, value in updates.items():
        if key in allowed and value:
            set_fields[key] = value

    if updates.get("new_password"):
        set_fields["password_hash"] = _hash(updates["new_password"])

    if set_fields:
        users_col().update_one(
            {"email": email.lower()},
            {"$set": set_fields},
        )

    return get_user(email), None


def safe_user(user):
    """Return user data without the password hash and MongoDB ID."""
    return {
        key: value
        for key, value in user.items()
        if key not in ("password_hash", "_id")
    }


# ================= USER PRODUCTS =================

def _next_asin():
    """Get the maximum ASIN across both collections, then add one."""
    max_product = 0
    product = products_col().find_one(sort=[("asin", -1)])

    if product:
        max_product = int(product.get("asin", 0))

    max_user = 0
    user_product = user_products_col().find_one(
        sort=[("asin", -1)]
    )

    if user_product:
        max_user = int(user_product.get("asin", 0))

    return max(max_product, max_user) + 1


def _next_id():
    user_product = user_products_col().find_one(
        sort=[("id", -1)]
    )

    if user_product:
        return int(user_product.get("id", 0)) + 1

    return 1


def add_user_product(
    owner_email,
    title,
    category,
    price,
    stars,
    bought,
    is_best_seller,
    description="",
    image_filename="",
):
    new_id = _next_id()
    new_asin = _next_asin()

    doc = {
        "asin": new_asin,
        "id": new_id,
        "owner_email": owner_email.lower(),
        "title": title,
        "categoryName": category,
        "price": price,
        "stars": stars,
        "boughtInLastMonth": bought,
        "isBestSeller": is_best_seller,
        "description": description,
        "image_filename": image_filename,
        "added_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    user_products_col().insert_one(doc)

    return user_products_col().find_one(
        {"asin": new_asin},
        {"_id": 0},
    )


def get_user_products(owner_email):
    return list(
        user_products_col().find(
            {"owner_email": owner_email.lower()},
            {"_id": 0},
        )
    )


EDITABLE_FIELDS = {
    "title",
    "categoryName",
    "price",
    "stars",
    "boughtInLastMonth",
    "isBestSeller",
    "description",
}


def update_user_product(owner_email, product_id, updates):
    """Update editable fields on a user-owned product."""
    clean = {
        key: value
        for key, value in updates.items()
        if key in EDITABLE_FIELDS
    }

    if not clean:
        return None, "no editable fields supplied"

    clean["updated_on"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    product_filter = {
        "id": int(product_id),
        "owner_email": owner_email.lower(),
    }

    result = user_products_col().update_one(
        product_filter,
        {"$set": clean},
    )

    if result.matched_count == 0:
        return None, "product not found or not owned by user"

    doc = user_products_col().find_one(
        product_filter,
        {"_id": 0},
    )

    return doc, None


def delete_user_product(owner_email, product_id):
    result = user_products_col().delete_one(
        {
            "owner_email": owner_email.lower(),
            "id": int(product_id),
        }
    )

    return result.deleted_count > 0


def get_all_user_products():
    """Allow CSV catalog browsing when MongoDB is unavailable."""
    try:
        return list(
            user_products_col().find({}, {"_id": 0})
        )
    except PyMongoError:
        logger.warning(
            "MongoDB unavailable; showing catalog without user products."
        )
        return []
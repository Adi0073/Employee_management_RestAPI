"""
MongoDB connection handling using PyMongo.

Exposes a single MongoClient instance and helper accessors for the
`users` and `employees` collections, plus index setup that runs once
at application startup.
"""

import logging

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings

logger = logging.getLogger("worksphere.database")

client: MongoClient = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
database = client[settings.MONGO_DB_NAME]

users_collection = database["users"]
employees_collection = database["employees"]


def connect_to_mongo() -> None:
    """Verify the MongoDB connection and create indexes. Call on startup."""
    try:
        client.admin.command("ping")
        logger.info("Connected to MongoDB at %s", settings.MONGO_URI)
    except ServerSelectionTimeoutError as exc:
        logger.error("Could not connect to MongoDB: %s", exc)
        raise

    # Unique index on user email to prevent duplicate accounts.
    users_collection.create_index([("email", ASCENDING)], unique=True)

    # Unique index on employee_id and email, plus indexes used for
    # search/filter/sort to keep query performance reasonable.
    employees_collection.create_index([("employee_id", ASCENDING)], unique=True)
    employees_collection.create_index([("email", ASCENDING)], unique=True)
    employees_collection.create_index([("department", ASCENDING)])
    employees_collection.create_index([("designation", ASCENDING)])
    employees_collection.create_index([("first_name", ASCENDING)])
    employees_collection.create_index([("salary", ASCENDING)])
    employees_collection.create_index([("joining_date", ASCENDING)])


def close_mongo_connection() -> None:
    """Close the MongoDB client connection. Call on shutdown."""
    client.close()
    logger.info("MongoDB connection closed")

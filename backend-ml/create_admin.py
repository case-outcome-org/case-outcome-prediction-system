from datetime import datetime, timezone
from getpass import getpass
import re
import sqlite3

from main import DB_FILE, get_connection, hash_password


def main():
    print("Create a private Admin account. Password input will not be displayed.")
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().casefold()
    if not name:
        raise SystemExit("Name is required.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise SystemExit("Enter a valid email address.")

    password = getpass("Admin password (at least 8 characters): ")
    confirmation = getpass("Confirm admin password: ")
    if len(password) < 8 or len(password) > 128:
        raise SystemExit("Password must be between 8 and 128 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    try:
        with get_connection() as connection:
            connection.execute(
                """INSERT INTO users (name, email, password_hash, role, created_at)
                   VALUES (?, ?, ?, 'Admin', ?)""",
                (
                    name,
                    email,
                    hash_password(password),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
    except sqlite3.IntegrityError as exc:
        raise SystemExit("An account already exists for this email.") from exc

    print(f"Admin account created for {email}.")
    print(f"Accounts are stored in: {DB_FILE}")
    print("You can now log in through the frontend using this email and password.")


if __name__ == "__main__":
    main()

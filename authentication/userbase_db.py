import hashlib
import os
from sqlite3 import connect

class UserManager:
    """
    Class that handles authentication with database backend
    """
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
            ''')
            conn.commit()
        self.create_user("max", "12345")

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return password_hash.hex(), salt.hex()

    def _verify_password(self, stored_hash, stored_salt, provided_password):
        salt_bytes = bytes.fromhex(stored_salt)
        provided_hash, _ = self._hash_password(provided_password, salt_bytes)
        return stored_hash == provided_hash

    def create_user(self, username: str, password: str) -> bool:
        """
        Create a new user in the database
        :param username: logon name
        :param password: password to save
        :return: True if user was created
        """
        if self.check_user_exists(username):
            return False
        password_hash, salt = self._hash_password(password)
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                (username, password_hash, salt)
            )
            conn.commit()
        return True

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate against the database
        :param username: username to check
        :param password: password to check
        :return: True if authenticated
        """
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT password_hash, salt FROM users WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
        if result is None:
            return False
        stored_hash, stored_salt = result
        return self._verify_password(stored_hash, stored_salt, password)

    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the database
        :param username: username to delete
        :return: True on success
        """
        if not self.check_user_exists(username):
            return False
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
        return True

    def change_user_password(self, username: str, password: str) -> bool:
        """
        Change the password for a user
        :param username: username to change
        :param password: new password
        :return: True on success
        """
        if not self.check_user_exists(username):
            return False
        password_hash, salt = self._hash_password(password)
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET password_hash = ?, salt = ? WHERE username = ?',
                (password_hash, salt, username)
            )
            conn.commit()
        return True

    def check_user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database
        :param username: logon name to look for
        :return: True if user exists
        """
        with connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM users WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
        return result is not None

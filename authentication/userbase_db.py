

class UserManager:
    """
    Class that handles authentication with database backend
    """
    def create_user(self, username: str, password: str) -> bool:
        """
        Create a new user in the database
        :param username: logon name
        :param password: password to save
        :return: True if user was created
        """

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate against the database
        :param username: username to check
        :param password: password to check
        :return: True if authenticated
        """
        pass

    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the database
        :param username: username to delete
        :return: True on success
        """
        pass

    def change_user_password(self, username: str, password: str) -> bool:
        """
        Change the password for a user
        :param username: username to change
        :param password: new password
        :return: True on success
        """
        pass

    def check_user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database
        :param username: logon name to look for
        :return: True if user exists
        """
        pass

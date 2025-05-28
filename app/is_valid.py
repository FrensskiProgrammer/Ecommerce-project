class IsValidData:
    """Класс предназначен для проверки корректности всех входных данных из схем"""

    def is_valid_username(self, username: str) -> bool:
        """Метод экземпляра для проверки корректности имя пользователя"""

        return (
            (username != "string")
            and (not (username.isspace()))
            and (len(username) > 4)
        )

    def is_valid_email(self, email: str) -> bool:
        """Метод экземпляра для проверки корректности почты"""

        return (
            ("@" in email)
            and (len(email) > 4)
            and (not (email.endswith("@")))
            and (not (email.startswith("@")))
        )

    def is_valid_password(self, password: str) -> bool:
        """Метод экземпляра для проверки корректности пароля"""

        return (
            (len(password) > 5)
            and (not (password.isspace()))
            and (password != "string")
        )

    def is_valid_title(self, title: str) -> bool:
        """Метод экземпляра для проверки корректности названия задачи"""

        return (
            isinstance(title, str)
            and (len(title) > 4)
            and (not (title.isspace()))
            and (title != "string")
        )

    def is_valid_description(self, description: str) -> bool:
        """Метод экземпляра для проверки корректности описания задачи"""

        return self.is_valid_title(description)

    def is_valid_status(self, status: str) -> bool:
        """Метод экземпляра для проверки корректности статуса задачи(статус может быть new, active или completed)"""

        return status in ("new", "active", "completed")

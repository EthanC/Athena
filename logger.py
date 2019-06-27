from datetime import datetime

from colorama import Fore, init


class Log:
    """Class containing logging functions intended to reduce messy code."""

    # Initialize Colorama
    init(autoreset=True)

    def now(self):
        """Return the current local time in 12-hour format."""

        return datetime.now().strftime("%I:%M:%S")

    def Intro(self, message: str):
        """Print the specified message in Cyan."""

        print(Fore.CYAN + message)

    def Print(self, message: str):
        """Print the specified message in White with the current time."""

        print(f"[{Log.now(self)}] {message}")

    def Info(self, message: str):
        """Print the specified message in Blue with the current time."""

        print(Fore.BLUE + f"[{Log.now(self)}] {message}")

    def Success(self, message: str):
        """Print the specified message in Green with the current time."""

        print(Fore.GREEN + f"[{Log.now(self)}] {message}")

    def Error(self, message: str):
        """Print the specified message in Red with the current time."""

        print(Fore.RED + f"[{Log.now(self)}] {message}")

    def Warn(self, message: str):
        """Print the specified message in Yellow with the current time."""

        print(Fore.YELLOW + f"[{Log.now(self)}] {message}")

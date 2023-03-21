from src.models.user import User
from getpass import getpass

print("Wat is je naam?")
display_name = input()

print("Wat is je email?")
email = input()

print("Wat is je wachtwoord?")
password = getpass()

User(
    display_name=display_name,
    email=email,
    password=password
).persist()

print(f"Completed seeding user {email}")

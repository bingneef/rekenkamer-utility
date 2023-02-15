from app.models.user import User
from getpass import getpass

print("Wat is je naam?")
display_name = input()

print("Wat is je email?")
email = input()

print("Wat is je wachtwoord?")
password = getpass()

print("Wat is de search api key?")
search_api_key = getpass()

User(
    display_name=display_name,
    email=email,
    search_api_key=search_api_key,
    password=password
).persist()

print(f"Completed seeding user {email}")

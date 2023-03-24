from src.util.auth import get_verification_code
import dotenv


def main():
    dotenv.load_dotenv()

    print("Wat is de email?")
    email = input()

    print(f"Verification code for {email} is {get_verification_code(email)}")


if __name__ == "__main__":
    main()

from src.util.auth import get_verification_code
import dotenv
import sys


def main():
    dotenv.load_dotenv()

    if len(sys.argv) < 2:
        print("Please provide an email as a command-line argument.")
        return

    email = sys.argv[1]

    print("---------------------------")
    print(f"Verification code for {email} is {get_verification_code(email)}")
    print("---------------------------")


if __name__ == "__main__":
    main()

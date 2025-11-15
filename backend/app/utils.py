# Utility functions
import secrets
import string


def generate_random_token(length: int = 32) -> str:
    """Generate a random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def format_currency(amount: float, currency: str = "₽") -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} {currency}"

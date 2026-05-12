import pytest

from vault.password_generator import (
    MIN_PASSWORD_LENGTH,
    PasswordGenerationError,
    generate_password,
)


def test_generate_password_uses_default_length() -> None:
    password = generate_password()

    assert len(password) >= MIN_PASSWORD_LENGTH


def test_generate_password_uses_custom_length() -> None:
    password = generate_password(length=32)

    assert len(password) == 32


def test_generate_password_without_symbols() -> None:
    password = generate_password(length=32, use_symbols=False)

    assert password.isalnum()


def test_generate_password_rejects_too_short_length() -> None:
    with pytest.raises(PasswordGenerationError):
        generate_password(length=MIN_PASSWORD_LENGTH - 1)


def test_generate_passwords_are_different() -> None:
    first_password = generate_password()
    second_password = generate_password()

    assert first_password != second_password
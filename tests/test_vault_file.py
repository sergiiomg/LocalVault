import json

import pytest

from vault.entries import add_entry, create_entry
from vault.vault_file import (
    InvalidMasterPasswordError,
    InvalidVaultFileError,
    VaultAlreadyExistsError,
    VaultNotFoundError,
    create_vault,
    open_vault,
    save_vault,
)


MASTER_PASSWORD = "VeryStrongMasterPassword123!"


def test_create_and_open_vault(tmp_path) -> None:
    vault_path = tmp_path / "test.vault"

    create_vault(vault_path, MASTER_PASSWORD)
    vault_data = open_vault(vault_path, MASTER_PASSWORD)

    assert vault_path.exists()
    assert vault_data == {"entries": []}


def test_create_vault_rejects_existing_file(tmp_path) -> None:
    vault_path = tmp_path / "test.vault"

    create_vault(vault_path, MASTER_PASSWORD)

    with pytest.raises(VaultAlreadyExistsError):
        create_vault(vault_path, MASTER_PASSWORD)


def test_open_vault_rejects_missing_file(tmp_path) -> None:
    vault_path = tmp_path / "missing.vault"

    with pytest.raises(VaultNotFoundError):
        open_vault(vault_path, MASTER_PASSWORD)


def test_open_vault_rejects_wrong_password(tmp_path) -> None:
    vault_path = tmp_path / "test.vault"

    create_vault(vault_path, MASTER_PASSWORD)

    with pytest.raises(InvalidMasterPasswordError):
        open_vault(vault_path, "WrongPassword123!")


def test_vault_file_does_not_store_plaintext(tmp_path) -> None:
    vault_path = tmp_path / "test.vault"

    create_vault(vault_path, MASTER_PASSWORD)

    vault_data = open_vault(vault_path, MASTER_PASSWORD)
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="SuperSecretPassword123!",
        url="https://github.com",
        notes="Test account",
    )

    add_entry(vault_data, entry)
    save_vault(vault_path, vault_data, MASTER_PASSWORD)

    raw_content = vault_path.read_text(encoding="utf-8")

    assert "GitHub" not in raw_content
    assert "sergiio@example.com" not in raw_content
    assert "SuperSecretPassword123!" not in raw_content


def test_save_and_reopen_vault_with_entry(tmp_path) -> None:
    vault_path = tmp_path / "test.vault"

    create_vault(vault_path, MASTER_PASSWORD)

    vault_data = open_vault(vault_path, MASTER_PASSWORD)
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="SuperSecretPassword123!",
    )

    add_entry(vault_data, entry)
    save_vault(vault_path, vault_data, MASTER_PASSWORD)

    reopened_vault_data = open_vault(vault_path, MASTER_PASSWORD)

    assert len(reopened_vault_data["entries"]) == 1
    assert reopened_vault_data["entries"][0]["service"] == "GitHub"


def test_open_vault_rejects_invalid_json(tmp_path) -> None:
    vault_path = tmp_path / "broken.vault"
    vault_path.write_text("not valid json", encoding="utf-8")

    with pytest.raises(InvalidVaultFileError):
        open_vault(vault_path, MASTER_PASSWORD)


def test_open_vault_rejects_null_json(tmp_path) -> None:
    vault_path = tmp_path / "broken.vault"
    vault_path.write_text("null", encoding="utf-8")

    with pytest.raises(InvalidVaultFileError):
        open_vault(vault_path, MASTER_PASSWORD)


def test_open_vault_rejects_missing_required_fields(tmp_path) -> None:
    vault_path = tmp_path / "broken.vault"
    vault_path.write_text(
        json.dumps({"version": 1}),
        encoding="utf-8",
    )

    with pytest.raises(InvalidVaultFileError):
        open_vault(vault_path, MASTER_PASSWORD)
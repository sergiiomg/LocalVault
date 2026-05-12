from vault.audit import audit_vault
from vault.entries import add_entry, create_entry


def test_audit_reports_no_issues_for_good_entry() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
        url="https://github.com",
        notes="Test account",
    )

    add_entry(vault_data, entry)

    warnings = audit_vault(vault_data)

    assert warnings == []


def test_audit_detects_missing_username() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="",
        password="StrongPassword123!123456",
        url="https://github.com",
    )

    add_entry(vault_data, entry)

    warnings = audit_vault(vault_data)

    assert any("username/email is empty" in warning for warning in warnings)


def test_audit_detects_short_password() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="Short1!123456",
        url="https://github.com",
    )

    add_entry(vault_data, entry)

    warnings = audit_vault(vault_data)

    assert any("password is shorter" in warning for warning in warnings)


def test_audit_detects_reused_password() -> None:
    vault_data = {"entries": []}

    first_entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="SamePassword123!123456",
        url="https://github.com",
    )
    second_entry = create_entry(
        service="GitLab",
        username="sergiio@example.com",
        password="SamePassword123!123456",
        url="https://gitlab.com",
    )

    add_entry(vault_data, first_entry)
    add_entry(vault_data, second_entry)

    warnings = audit_vault(vault_data)

    assert any("Reused password detected" in warning for warning in warnings)


def test_audit_detects_missing_url() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
        url="",
    )

    add_entry(vault_data, entry)

    warnings = audit_vault(vault_data)

    assert any("URL is missing" in warning for warning in warnings)
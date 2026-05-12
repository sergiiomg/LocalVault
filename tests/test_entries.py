from vault.entries import (
    add_entry,
    create_entry,
    delete_entry,
    find_entries,
    get_entries,
)


def test_create_entry_contains_expected_fields() -> None:
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
        url="https://github.com",
        notes="Test account",
    )

    assert entry["id"]
    assert entry["service"] == "GitHub"
    assert entry["username"] == "sergiio@example.com"
    assert entry["password"] == "StrongPassword123!123456"
    assert entry["url"] == "https://github.com"
    assert entry["notes"] == "Test account"
    assert entry["created_at"]
    assert entry["updated_at"]


def test_add_entry_adds_entry_to_vault_data() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
    )

    add_entry(vault_data, entry)

    assert len(vault_data["entries"]) == 1
    assert vault_data["entries"][0]["service"] == "GitHub"


def test_get_entries_creates_entries_list_if_missing() -> None:
    vault_data = {}

    entries = get_entries(vault_data)

    assert entries == []
    assert vault_data["entries"] == []


def test_find_entries_by_service() -> None:
    vault_data = {"entries": []}

    github_entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
    )
    gitlab_entry = create_entry(
        service="GitLab",
        username="sergiio@example.com",
        password="AnotherStrongPassword123!123456",
    )

    add_entry(vault_data, github_entry)
    add_entry(vault_data, gitlab_entry)

    results = find_entries(vault_data, "github")

    assert len(results) == 1
    assert results[0]["service"] == "GitHub"


def test_delete_entry_removes_entry() -> None:
    vault_data = {"entries": []}
    entry = create_entry(
        service="GitHub",
        username="sergiio@example.com",
        password="StrongPassword123!123456",
    )

    add_entry(vault_data, entry)

    was_deleted = delete_entry(vault_data, entry["id"])

    assert was_deleted is True
    assert vault_data["entries"] == []


def test_delete_entry_returns_false_when_not_found() -> None:
    vault_data = {"entries": []}

    was_deleted = delete_entry(vault_data, "missing-id")

    assert was_deleted is False
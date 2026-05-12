from typing import Any

REQUIRED_ENTRY_FIELDS = {
    "id",
    "service",
    "username",
    "password",
    "url",
    "notes",
    "created_at",
    "updated_at",
    }

class VaultValidationError(ValueError):
    pass

def validate_vault_file_content(vault_file_content: Any) -> None:
    # Validamos la estructura externa del archivo .vault
    if not isinstance(vault_file_content, dict):
        raise VaultValidationError("Vault file content must be a JSON object.")
    
    required_top_level_fields = {
        "version",
        "kdf",
        "cipher",
        "salt",
        "ciphertext",
    }

    missing_fields = required_top_level_fields - vault_file_content.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise VaultValidationError(f"Vault file is missing required fields: {missing}")

    if vault_file_content["version"] != 1:
        raise VaultValidationError("Unsupported vault version.")

    if not isinstance(vault_file_content["kdf"], dict):
        raise VaultValidationError("Vault field 'kdf' must be an object.")

    if not isinstance(vault_file_content["cipher"], dict):
        raise VaultValidationError("Vault field 'cipher' must be an object.")

    if vault_file_content["kdf"].get("name") != "argon2id":
        raise VaultValidationError("Unsupported key derivation function.")

    if vault_file_content["cipher"].get("name") != "AES-256-GCM":
        raise VaultValidationError("Unsupported cipher.")

    if not isinstance(vault_file_content["salt"], str):
        raise VaultValidationError("Vault field 'salt' must be a string.")

    if not isinstance(vault_file_content["ciphertext"], str):
        raise VaultValidationError("Vault field 'ciphertext' must be a string.")

    if not isinstance(vault_file_content["cipher"].get("nonce"), str):
        raise VaultValidationError("Vault cipher field 'nonce' must be a string.")
    
def validate_vault_data(vault_data: Any) -> None:
    # Validamos los datos ya descifrados
    if not isinstance(vault_data, dict):
        raise VaultValidationError("Vault data must be a JSON object.")
        
    if "entries" not in vault_data:
        raise VaultValidationError("Decrypted vault data is missing 'entries' field.")
        
    entries = vault_data["entries"]

    if not isinstance(entries, list):
        raise VaultValidationError("Vault 'entries' field must be a list.")
        
    for i, entry in enumerate(entries, start=1):
        validate_entry(entry, i)

def validate_entry(entry: Any, index: int) -> None:
    # Validamos cada entrada individualmente, comprobando que tiene los campos requeridos y que son del tipo correcto.
    if not isinstance(entry, dict):
        raise VaultValidationError(f"Entry {index} must be a JSON object.")
    
    missing_fields = REQUIRED_ENTRY_FIELDS - entry.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise VaultValidationError(f"Entry {index} is missing required fields: {missing}")

    string_fields = REQUIRED_ENTRY_FIELDS

    for field in string_fields:
        if not isinstance(entry[field], str):
            raise VaultValidationError(f"Entry {index} field '{field}' must be a string.")
        
    if not entry["id"]:
        raise VaultValidationError(f"Entry #{index} has an empty id.")

    if not entry["service"]:
        raise VaultValidationError(f"Entry #{index} has an empty service.")

    if not entry["password"]:
        raise VaultValidationError(f"Entry #{index} has an empty password.")
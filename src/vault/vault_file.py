# Funciones para crear y abrir archivos .vault, que contienen los datos cifrados y la información de la clave.

import json
import os
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from vault.backup import create_backup
from vault.crypto import encrypt_data, decrypt_data
from vault.validation import (
    VaultValidationError,
    validate_vault_data,
    validate_vault_file_content,
)

VAULT_VERSION = 1

class VaultError(Exception):
    pass

class VaultNotFoundError(VaultError):
    pass

class VaultAlreadyExistsError(VaultError):
    pass

class InvalidMasterPasswordError(VaultError):
    pass

class InvalidVaultFileError(VaultError):
    pass

def create_empty_vault_data() -> dict[str, any]:
    # Con esta funcion creamos la estrucutra inicial de los datos del vault.
    return{
        "entries": []
    }

def build_vault_file_content(
    vault_data: dict[str, Any],
    master_password: str,
) -> dict[str, Any]:
    plaintext = json.dumps(vault_data, indent=2).encode("utf-8")
    encrypted = encrypt_data(plaintext, master_password)

    return {
        "version": VAULT_VERSION,
        "kdf": {
            "name": "argon2id",
            "time_cost": 3,
            "memory_cost": 65536,
            "parallelism": 4,
        },
        "cipher": {
            "name": "AES-256-GCM",
            "nonce": encrypted.nonce,
        },
        "salt": encrypted.salt,
        "ciphertext": encrypted.ciphertext,
    }

def write_text_atomic(path: Path, content: str) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    temporary_path.write_text(content, encoding="utf-8")
    os.replace(temporary_path, path)


def save_vault(vault_path: Path, vault_data: dict[str, Any], master_password: str, create_backup_before_save: bool = True,) -> None:
    # Guardamos el vault cifrado en el disco.
    if create_backup_before_save:
        create_backup(vault_path)

    vault_file_content = build_vault_file_content(vault_data, master_password)

    serialized_vault = json.dumps(vault_file_content, indent=2)

    write_text_atomic(vault_path, serialized_vault)

def create_vault(vault_path: Path, master_password: str) -> None:
    # Esta función crea un nuevo vault. Primero comprueba que el archivo no existe para evitar sobrescribir un vault existente.
    if vault_path.exists():
        raise VaultAlreadyExistsError(f"El archivo {vault_path} ya existe.")
    
    vault_data = create_empty_vault_data()
    save_vault(vault_path, vault_data, master_password, create_backup_before_save=False)

def read_vault_file_content(vault_path: Path) -> dict[str, Any]:
    if not vault_path.exists():
        raise VaultNotFoundError(f"El archivo {vault_path} no existe.")
    
    try:
        raw_content = vault_path.read_text(encoding='utf-8')
        vault_file_content = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise InvalidVaultFileError(f"El archivo {vault_path} no contiene un JSON válido.") from exc
    except OSError as exc:
        raise InvalidVaultFileError(f"Error al leer el archivo {vault_path}.") from exc
    
    try:
        validate_vault_file_content(vault_file_content)
    except VaultValidationError as exc:
        raise InvalidVaultFileError(str(exc)) from exc
    
    return vault_file_content
    

def open_vault(vault_path: Path, master_password: str) -> dict[str, Any]:
    # Esta función abre un vault existente. Primero comprueba que este existe. Después lee el contenido del vault.
    # Después lo desencripta usando la contraseña maestra y finalmente devuelve los datos del vault como un diccionario de Python.
    # Si la contraseña maestra es incorrecta o el archivo está corrupto, se lanza una excepción InvalidMasterPasswordError.
    if not vault_path.exists():
        raise VaultNotFoundError(f"El archivo {vault_path} no existe.")
    
    vault_file_content = read_vault_file_content(vault_path)

    if vault_file_content is None:
        raise ValueError(
            "Invalid vault file: the file contains null instead of encrypted vault data."
        )

    try:
        plaintext = decrypt_data(
            ciphertext_b64=vault_file_content["ciphertext"],
            master_password=master_password,
            salt_b64=vault_file_content["salt"],
            nonce_b64=vault_file_content["cipher"]["nonce"]
        )

    except InvalidTag as exc:
        raise InvalidMasterPasswordError("La contraseña maestra es incorrecta o el archivo está corrupto.") from exc
    
    try:
        vault_data = json.loads(plaintext.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise InvalidVaultFileError("El contenido del vault descifrado no es un JSON válido.") from exc
    
    try:
        validate_vault_data(vault_data)
    except VaultValidationError as exc:
        raise InvalidVaultFileError(str(exc)) from exc
    
    return json.loads(plaintext.decode('utf-8'))
# Funciones para crear y abrir archivos .vault, que contienen los datos cifrados y la información de la clave.

import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag

from vault.crypto import encrypt_data, decrypt_data

VAULT_VERSION = 1

class VaultError(Exception):
    pass

class VaultNotFoundError(VaultError):
    pass

class VaultAlreadyExistsError(VaultError):
    pass

class InvalidMasterPasswordError(VaultError):
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


def save_vault(vault_path: Path, vault_data: dict[str, Any], master_password: str) -> None:
    # Guardamos el vault cifrado en el disco.
    vault_file_content = build_vault_file_content(vault_data, master_password)

    vault_path.write_text(
        json.dumps(vault_file_content, indent=2),
        encoding="utf-8",
    )

def create_vault(vault_path: Path, master_password: str) -> None:
    # Esta función crea un nuevo vault. Primero comprueba que el archivo no existe para evitar sobrescribir un vault existente.
    if vault_path.exists():
        raise VaultAlreadyExistsError(f"El archivo {vault_path} ya existe.")
    
    vault_data = create_empty_vault_data()
    save_vault(vault_path, vault_data, master_password)
    

def open_vault(vault_path: Path, master_password: str) -> dict[str, Any]:
    # Esta función abre un vault existente. Primero comprueba que este existe. Después lee el contenido del vault.
    # Después lo desencripta usando la contraseña maestra y finalmente devuelve los datos del vault como un diccionario de Python.
    # Si la contraseña maestra es incorrecta o el archivo está corrupto, se lanza una excepción InvalidMasterPasswordError.
    if not vault_path.exists():
        raise VaultNotFoundError(f"El archivo {vault_path} no existe.")
    
    vault_file_content = json.loads(vault_path.read_text(encoding='utf-8'))

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
    
    return json.loads(plaintext.decode('utf-8'))
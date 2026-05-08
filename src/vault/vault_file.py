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

def create_vault(vault_path: Path, master_password: str) -> None:
    # Con esta funcion creamos un vault. Primero comprobamos si este ya existe. Si no es así pasamos a texto plano la estructura inicial del vault.
    # Después encriptamos ese texto plano y finalmente escribimos el archivo .vault con la información de la versión, el kdf, el cipher, el salt y el texto cifrado.
    if vault_path.exists():
        raise VaultAlreadyExistsError(f"El archivo {vault_path} ya existe.")
    
    vault_data = create_empty_vault_data()
    plaintext = json.dumps(vault_data, indent=2).encode('utf-8')

    encrypted = encrypt_data(plaintext, master_password)

    vault_file_content = {
        "version": VAULT_VERSION,
        "kdf":{
            "name": "argon2id",
            "time_cost": 3,
            "memory_cost": 65536,
            "parallelism": 4,
        },
        "cipher": {
            "name": "AES-256-GCM",
            "nonce": encrypted.nonce
        },
        "salt": encrypted.salt,
        "ciphertext": encrypted.ciphertext
    }

    vault_path.write_text(
        json.dumps(vault_file_content, indent=2),
        encoding='utf-8'
    )

def open_vault(vault_path: Path, master_password: str) -> dict[str, Any]:
    # Esta función abre un vault existente. Primero comprueba que este existe. Después lee el contenido del vault.
    # Después lo desencripta usando la contraseña maestra y finalmente devuelve los datos del vault como un diccionario de Python.
    # Si la contraseña maestra es incorrecta o el archivo está corrupto, se lanza una excepción InvalidMasterPasswordError.
    if not vault_path.exists():
        raise VaultNotFoundError(f"El archivo {vault_path} no existe.")
    
    vault_file_content = json.loads(vault_path.read_text(encoding='utf-8'))

    try:
        plaintext = decrypt_data(
            ciphertext_b64 = vault_file_content["ciphertext"],
            master_password = master_password,
            salt_b64 = vault_file_content["salt"],
            nonce_b64 = vault_file_content["cipher"]["nonce"]
        )
    except InvalidTag as exc:
        raise InvalidMasterPasswordError("La contraseña maestra es incorrecta o el archivo está corrupto.") from exc
    
    return json.loads(plaintext.decode('utf-8'))
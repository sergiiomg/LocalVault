import argparse
from getpass import getpass
from pathlib import Path

from vault.vault_file import (
    InvalidMasterPasswordError,
    VaultAlreadyExistsError,
    VaultNotFoundError,
    create_vault,
    open_vault
)

def handle_create (args: argparse.Namespace) -> None:
    vault_path = Path(args.vault_path)

    master_password = getpass("Introduce la contraseña maestra para el nuevo vault: ")
    confirm_password = getpass("Confirma la contraseña maestra: ")

    if master_password != confirm_password:
        print("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")
        return

    if not master_password:
        print("La contraseña maestra no puede estar vacía. Por favor, inténtalo de nuevo.")
        return

    try:
        create_vault(vault_path, master_password)
    except VaultAlreadyExistsError :
        print(f"El archivo {vault_path} ya existe. Por favor, elige otro nombre o elimina el archivo existente.")
        return

    print(f"Vault creado exitosamente en {vault_path}.")

def handle_open(args: argparse.Namespace) -> None:

    vault_path = Path(args.vault_path)

    master_password = getpass("Contraseña maestra: ")

    try:
        vault_data = open_vault(vault_path, master_password)
    except VaultNotFoundError:
        print(f"Error: vault no encontrado en {vault_path}")
        return
    except InvalidMasterPasswordError:
        print("Error: contraseña maestra inválida.")
        return
    
    entry_count = len(vault_data.get("entries", []))

    print(f"Vault abierto exitosamente. Contiene {entry_count} entradas.")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog= "vault",
        description= "Una aplicación de línea de comandos para gestionar un vault de contraseñas cifrado."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Crear un nuevo vault cifrado."
    )

    create_parser.add_argument(
        "vault_path",
        help="La ruta donde se guardará el nuevo vault (ejemplo: myvault.vault)."
    )

    create_parser.set_defaults(func=handle_create)

    open_parser = subparsers.add_parser(
        "open",
        help="Abrir un vault existente y mostrar su contenido."
    )

    open_parser.add_argument(
        "vault_path",
        help="La ruta del vault que deseas abrir (ejemplo: myvault.vault)."
    )
    open_parser.set_defaults(func=handle_open)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":    
    main()
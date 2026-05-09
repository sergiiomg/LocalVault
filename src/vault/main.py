import argparse
from getpass import getpass
from pathlib import Path

from vault.entries import(
    add_entry,
    create_entry,
    delete_entry,
    find_entries,
    get_entries
)

from vault.vault_file import (
    InvalidMasterPasswordError,
    VaultAlreadyExistsError,
    VaultNotFoundError,
    create_vault,
    open_vault,
    save_vault
)

# Evitamos duplicar código para pedir la contraseña maestra. Se centraliza todo en una función.
def ask_master_password() -> str:
    return getpass("Contraseña maestra:")


# Abrimos el vault. Devuelve los datos y la contraseña maestrea. Devuelve la contraseña porque luego tiene que cifrarlo todo.
def unlock_vault(vault_path: Path) -> tuple[dict, str] | None:
    master_password = ask_master_password()

    try:
        vault_data = open_vault(vault_path, master_password)
    except VaultNotFoundError:
        print(f"Error: vault no encontrado en {vault_path}")
        return None
    except InvalidMasterPasswordError:
        print("Error: contraseña maestra inválida.")
        return None
    
    return vault_data, master_password

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

    unlocked = unlock_vault(vault_path)

    if unlocked is None:
        return
    
    vault_data, _master_password = unlocked
    entry_count = len(get_entries(vault_data))

    print(f"Vault abierto exitosamente. Contiene {entry_count} entradas.")

def handle_add(args: argparse.Namespace) -> None:
    vault_path = Path(args.vault_path)

    unlocked = unlock_vault(vault_path)

    if unlocked is None:
        return

    vault_data, master_password = unlocked

    print("\nNueva entrada:")
    print("------------")

    service = input("Service: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    url = input("URL (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    if not service:
        return("Error: service cannot be empty")
    
    if not password:
        return("Error: password cannot be empty")
    
    entry = create_entry(
        service=service,
        username=username,
        password=password,
        url=url,
        notes=notes
    )

    add_entry(vault_data, entry)
    save_vault(vault_path, vault_data, master_password)

    print(f"Entry added successfully.: {service}")

def handle_list(args: argparse.Namespace) -> None:

    vault_path = Path(args.vault_path)

    unlocked = unlock_vault(vault_path)

    if unlocked is None:
        return
        
    vault_data, _master_password = unlocked
    entries = get_entries(vault_data)

    if not entries:
        print("No entries found in the vault.")
        return
        
    print("\nEntradas guardadas")
    print("-----------------")

    for i, entry in enumerate(entries, start=1):
        service = entry.get("service", "")
        username = entry.get("username", "")
        url = entry.get("url", "")

        print(f"{i}. Service: {service}")
        print(f"   Username: {username}")

        if url:
            print(f"   URL: {url}")

def handle_get(args: argparse.Namespace) -> None:
    vault_path = Path(args.vault_path)

    unlocked = unlock_vault(vault_path)

    if unlocked is None:
        return
    
    vault_data, _master_password = unlocked
    results = find_entries(vault_data, args.query)

    if not results:
        print("No se encontraron entradas que coincidan con la consulta.")
        return
    
    if len(results) > 1:
        print("Se encontraron varias entradas que coinciden con la consulta. Por favor, refina tu búsqueda.")
        print()

        for entry in results:
            print(f"Service: {entry.get('service', '')}, Username: {entry.get('username', '')}")

        return
    
    entry = results[0]
    
    print("\Detalles de la entrada:")
    print("-------------------")
    print(f"Service: {entry.get('service', '')}")
    print(f"Username: {entry.get('username', '')}")
    print(f"Password: {entry.get('password', '')}")
    print(f"URL: {entry.get('url', '')}")
    print(f"Notes: {entry.get('notes', '')}")
    print(f"Created at: {entry.get('created_at', '')}")
    print(f"Updated at: {entry.get('updated_at', '')}")
    
def handle_delete(args: argparse.Namespace) -> None:
    vault_path = Path(args.vault_path)

    unlocked = unlock_vault(vault_path)

    if unlocked is None:
        return
    
    vault_data, master_password = unlocked
    results = find_entries(vault_data, args.query)

    if not results:
        print("No se encontraron entradas que coincidan con la consulta.")
        return
    
    if len(results) > 1:
        print("Se encontraron varias entradas que coinciden con la consulta. Por favor, refina tu búsqueda.")
        print()

        for entry in results:
            print(f"Service: {entry.get('service', '')}, Username: {entry.get('username', '')}")

        return
    
    entry = results[0]

    service = entry.get("service", "")
    username = entry.get("username", "")

    print(f"¿Estás seguro de que deseas eliminar la entrada para {service} ({username})?")
    confirmation = input("Escribe 'yes' para confirmar: ").strip().lower()

    if confirmation != "yes":
        print("Eliminación cancelada.")
        return
    
    was_deleted = delete_entry(vault_data, entry["id"])

    if not was_deleted:
        print("Error: no se pudo eliminar la entrada.")
        return
    
    save_vault(vault_path, vault_data, master_password)

    print(f"Entrada para {service} ({username}) eliminada exitosamente.")


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

    add_parser = subparsers.add_parser(
        "add",
        help="Add a new password entry",
    )
    add_parser.add_argument(
        "vault_path",
        help="Path to the vault file",
    )
    add_parser.set_defaults(func=handle_add)

    list_parser = subparsers.add_parser(
        "list",
        help="List saved entries",
    )
    list_parser.add_argument(
        "vault_path",
        help="Path to the vault file",
    )
    list_parser.set_defaults(func=handle_list)

    get_parser = subparsers.add_parser(
        "get",
        help="Show a saved entry",
    )
    get_parser.add_argument(
        "vault_path",
        help="Path to the vault file",
    )
    get_parser.add_argument(
        "query",
        help="Search query, for example: github",
    )
    get_parser.set_defaults(func=handle_get)

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a saved entry",
    )
    delete_parser.add_argument(
        "vault_path",
        help="Path to the vault file",
    )
    delete_parser.add_argument(
        "query",
        help="Search query, for example: github",
    )
    delete_parser.set_defaults(func=handle_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":    
    main()
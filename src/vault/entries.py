# Gestionamos las entradas del vault

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

def get_current_timestamp() -> str:
    # Devuelve la fecha y hora actual en formato ISO 8601
    return datetime.now(timezone.utc).isoformat()

def create_entry(
        # Creamos una nueva entrada para el vault
        service: str,
        username: str,
        password: str,
        url: str = "",
        notes: str = "",
) -> dict[str, Any]:
    now = get_current_timestamp()

    return{
        "id": str(uuid4()),
        "service": service,
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "created_at": now,
        "updated_at": now,
    }

def get_entries(vault_data: dict[str, Any]) -> list[dict[str, Any]]:
    # Devuelve la lista de entradas del vault
    return vault_data.setdefault("entries", [])

def add_entry(vault_data: dict[str, Any], entry: dict[str, Any]) -> list[dict[str, Any]]:
    # Añade una nueva entrada al vault. No guarda en el disco, solo modifica datos en memoria.
    entries = get_entries(vault_data)
    entries.append(entry)

def find_entries(vault_data: dict[str, Any], query: str) -> list[dict[str, Any]]:
    # Busca entradas en el vault que coincidan con la consulta. La búsqueda es insensible a mayúsculas y minúsculas.
    entries = get_entries(vault_data)
    normalized_query = query.lower().strip()

    results = []

    for entry in entries:
        service = entry.get("service", "").lower()
        username = entry.get("username", "").lower()
        url = entry.get("url", "").lower()

        if(
            normalized_query in service or
            normalized_query in username or
            normalized_query in url
        ):
            results.append(entry)
    
    return results

def delete_entry(vault_data: dict[str, Any], entry_id: str) -> bool:
    entries = get_entries(vault_data)

    for i, entry in enumerate(entries):
        if entry.get("id") == entry_id:
            del entries[i]
            return True
        
    return False
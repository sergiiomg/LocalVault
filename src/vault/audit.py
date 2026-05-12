from collections import defaultdict
from typing import Any

MIN_RECOMMENDED_PASSWORD_LENGTH = 16

def audit_vault(vault_data: dict[str, Any]) -> list[str]:
    # Realizamos una auditória de seguridad en el vault para identificar posibles problemas como contraseñas débiles, reutilizadas o entradas con campos vacíos.
    warnings = []
    entries = vault_data.get("entries", [])

    warnings.extend(find_empty_usernames(entries))
    warnings.extend(find_weak_passwords(entries))
    warnings.extend(find_reused_passwords(entries))
    warnings.extend(find_missing_urls(entries))

    return warnings

def find_empty_usernames(entries: list[dict[str, Any]]) -> list[str]:
    # Buscamos las entradas que tienen el campo de nombre de usuario vacío
    warnings = []

    for entry in entries:
        if not entry.get("username", "").strip():
            service = entry.get("service", "Unknown service")
            warnings.append(f"{service}: username/email is empty.")
    
    return warnings

def find_weak_passwords(entries: list[dict[str, Any]]) -> list[str]:
    # Buscamos las entradas que tienen contraseñas débiles, como contraseñas cortas, sin mezcla de mayúsculas y minúsculas o sin dígitos.
    warnings = []

    for entry in entries:
        service = entry.get("service", "Unknown Service")
        password = entry.get("password", "")

        if len(password) < MIN_RECOMMENDED_PASSWORD_LENGTH:
            warnings.append(
                f"{service}: password is shorter than "
                f"{MIN_RECOMMENDED_PASSWORD_LENGTH} characters."
            )

        if password.lower() == password or password.upper() == password:
            warnings.append(
                f"{service}: password should mix uppercase and lowercase letters."
            )

        if not any(character.isdigit() for character in password):
            warnings.append(f"{service}: password does not contain digits.")

    return warnings

def find_reused_passwords(entries: list[dict[str, Any]]) -> list[str]:
    # Buscamos contraseñas que se repiten en varias entradas
    warnings = []
    password_to_services = defaultdict(list)

    for entry in entries:
        password = entry.get("password", "")
        service = entry.get("service", "Unknown Service")

        if password:
            password_to_services[password].append(service)

    for services in password_to_services.values():
        if len(services) > 1:
            service_list = ", ".join(services)
            warnings.append(f"Reused password detected in: {service_list}.")
            
    return warnings

def find_missing_urls(entries: list[dict[str, Any]]) -> list[str]:
    # Buscamos entradas que no tienen un URL asociado
    warnings = []

    for entry in entries:
        if not entry.get("url", "").strip():
            service = entry.get("service", "Unknown Service")
            warnings.append(f"{service}: URL is missing.")
    
    return warnings
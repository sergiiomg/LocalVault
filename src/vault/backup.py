from datetime import datetime, timezone
from pathlib import Path
import shutil
BACKUP_DIRECTORY_NAME = ".vault_backups"
MAX_BACKUPS = 5

def create_backup(vault_path: Path) -> None:
    # Si el vault existe, crea una copia. 
    if not vault_path.exists():
        return
    
    backup_directorty = vault_path.parent / BACKUP_DIRECTORY_NAME
    backup_directorty.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{vault_path.stem}_{timestamp}{vault_path.suffix}.bak"
    backup_path = backup_directorty / backup_name

    shutil.copy2(vault_path, backup_directorty)

    return backup_path

def cleanup_old_backups(backup_directory: Path, vault_path: Path) -> None:
    # Elimina las copias de seguridad más antiguas, manteniendo solo las MAX_BACKUPS más recientes.
    backup_pattern = f"{vault_path.stem}_*{vault_path.suffix}.bak"
    backups = sorted(
        backup_directory.glob(backup_pattern), 
        key=lambda p: p.stat().st_mtime, 
        reverse=True
    )
    for old_backup in backups[MAX_BACKUPS:]:
        old_backup.unlink()
import time
import pyperclip

DEFAULT_TIMEOUT = 30  # segundos que la contraseña permanecerá en el portapapeles

class ClipboardError(RuntimeError):
    pass

def copy_to_clipboard(text: str) -> None:
    # Copia el texto al portapapeles. Si ocurre un error, se lanza una excepción ClipboardError.
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as error:
        raise ClipboardError(f"Error al copiar al portapapeles.") from error
    
def clear_clipboard_if_unchanged(original_text: str, delay_seconds: int) -> None:
    # Limpia el portapapeles después de un retraso, pero solo si el contenido no ha cambiado. Si ocurre un error, se lanza una excepción ClipboardError.
    if delay_seconds <= 0:
        return
    
    time.sleep(delay_seconds)

    try:
        current_clipboard = pyperclip.paste()
    except pyperclip.PyperclipException as error:
        raise ClipboardError("Error al acceder al portapapeles.") from error

    if current_clipboard == original_text:
        try:
            pyperclip.copy("")
        except pyperclip.PyperclipException as error:
            raise ClipboardError("Error al limpiar el portapapeles.") from error
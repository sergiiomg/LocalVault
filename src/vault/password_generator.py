import secrets # Es un random seguro para generar contraseñas.
import string # Nos da acceso a conjuntos de caracteres predefinidos como letras y dígitos.

DEFAULT_PASSWORD_LENGTH = 24
MIN_PASSWORD_LENGTH = 16

LOWERCASE_LETTERS = string.ascii_lowercase
UPPERCASE_LETTERS = string.ascii_uppercase
DIGITS = string.digits
SIMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

AMBIGUOUS_CHARACTERS = "Il1O0"

class PasswordGenerationError(ValueError):
    pass

def remove_ambiguous_characters(characters: str) -> str:
    return "".join(
        character for character in characters
        if character not in AMBIGUOUS_CHARACTERS
    )

def build_alphabet(
        # Esta función construye el conjunto de caracteres permitidos a la hora de generar contraseñas.
        # Por defecto incluye letras mayúsculas, minúsculas, dígitos y símbolos. También tiene opciones para excluir símbolos y caracteres ambiguos.
        use_symbols: bool = True,
        avoid_ambiguous: bool = True,
) -> str:
    alphabet = LOWERCASE_LETTERS + UPPERCASE_LETTERS + DIGITS

    if use_symbols: 
        alphabet += SIMBOLS

    if avoid_ambiguous:
        alphabet = remove_ambiguous_characters(alphabet)

    return alphabet

def generate_password(
        # Comprueba que la longitud de la contraseña es al menos el mínimo requerido. Luego construye el alfabeto de caracteres permitido y finalmente genera una contraseña aleatoria seleccionando caracteres del alfabeto.
        length: int = DEFAULT_PASSWORD_LENGTH,
        use_symbols: bool = True,
        avoid_ambiguous: bool = True,
) -> str:
    if length < MIN_PASSWORD_LENGTH:
        raise PasswordGenerationError(
            f"Password length must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    
    alphabet = build_alphabet(
        use_symbols=use_symbols,
        avoid_ambiguous=avoid_ambiguous,
    )

    if not alphabet:
        raise PasswordGenerationError("No characters available to generate password.")
    
    return "".join(secrets.choice(alphabet) for _ in range(length))
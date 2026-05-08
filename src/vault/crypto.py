# Funciones de cifrado, descifrado y derivación de clave

import base64 # Para codificar y decodificar datos en base64. Los datos cifrados son bytes, pero JSON trabaja con strings, así que los convertimos a base64 para poder almacenarlos como texto.
import os # Generamos bytes aleatorios seguros
from dataclasses import dataclass # Nos permite crear una estructura limpia para devolver los resultados del cifrado

from argon2.low_level import Type, hash_secret_raw # Convierte la contraseña amestra en una clave de cifrado segura utilizando Argon2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM # Cifra y verifica los datos

SALT_SIZE = 16 # Tamaño del salt en bytes
NONCE_SIZE = 12 # Tamaño del nonce en bytes (96 bits, recomendado para AES-GCM)
KEY_SIZE = 32 # Tamaño de la clave en bytes (256 bits)


# Esto configura lo "caro" que sale derivar la clave. Si alguien intenta probar millones de contraseñas, cada nitento le cuesta tiempo y memoria.
ARGON2_TIME_COST = 3 # Número de iteraciones (tiempo de ejecución)
ARGON2_MEMORY_COST = 64 * 1024 # Memoria utilizada en KB (64 MB)
ARGON2_PARALLELISM = 4 # Número de hilos (paralelismo)

@dataclass(frozen=True)
class EncryptionResult:
    # Estructura para almacenar el resultado del cifrado, incluyendo el salt, nonce y texto cifrado
    salt: str
    nonce: str
    ciphertext: str

def encode_base64(data: bytes) -> str:
    # Codifica bytes a una cadena base64
    return base64.b64encode(data).decode('utf-8')

def decode_base64(data: str) -> bytes:
    # Decodifica una cadena base64 a bytes
    return base64.b64decode(data.encode('utf-8'))

def generate_salt() -> bytes:
    # Genera un salt aleatorio seguro
    return os.urandom(SALT_SIZE)

def generate_nonce() -> bytes:
    # Genera un nonce aleatorio seguro
    return os.urandom(NONCE_SIZE)

def derive_key(master_password: str, salt: bytes) -> bytes:
    # Esta función recibe la contraseña maestra y el salt. Devuelve una clave criptográfica de 32 bytes.
    return hash_secret_raw(
        secret = master_password.encode('utf-8'),
        salt = salt,
        time_cost = ARGON2_TIME_COST,
        memory_cost = ARGON2_MEMORY_COST,
        parallelism = ARGON2_PARALLELISM,
        hash_len = KEY_SIZE,
        type = Type.I
    )

def encrypt_data(plaintext: str, master_password: str) -> EncryptionResult:
    # Esta funcion recibe datos sin cifrar.

    salt = generate_salt() # Generamos un salt nuevo para cada cifrado
    nonce = generate_nonce() # Generamos un nonce nuevo para cada cifrado
    key = derive_key(master_password, salt) # Derivamos la clave usando la contraseña maestra y el salt

    aesgcm = AESGCM(key) # Creamos un objeto AES-GCM con la clave derivada
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None) # Ciframos el texto plano usando el nonce y la clave

    return EncryptionResult(
        salt = encode_base64(salt), # Codificamos el salt a base64 para almacenarlo como texto
        nonce = encode_base64(nonce), # Codificamos el nonce a base64 para almacenarlo como texto
        ciphertext = encode_base64(ciphertext) # Codificamos el texto cifrado a base64 para almacenarlo como texto
    )

def decrypt_data(ciphertext_b64: str, master_password: str, salt_b64: str, nonce_b64: str) -> bytes:
    salt = decode_base64(salt_b64) # Decodificamos el salt de base64 a bytes
    nonce = decode_base64(nonce_b64) # Decodificamos el nonce de
    ciphertext = decode_base64(ciphertext_b64) # Decodificamos el texto cifrado de base64 a bytes

    key = derive_key(master_password, salt) # Derivamos la clave usando la contraseña maestra y el salt

    aesgcm = AESGCM(key) # Creamos un objeto AES-GCM con la clave derivada
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None) # Desciframos el texto cifrado usando el nonce y la clave. Si la contraseña es incorrecta o los datos han sido manipulados, esta función lanzará una excepción.
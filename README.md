# VAULT

VAULT is a local-first encrypted password manager built with Python.

The project repository is named **LocalVault**, while the application itself is called **VAULT**.

## Goal

The goal of this project is to build a simple, secure and educational password manager that stores credentials inside an encrypted local vault file.

## Planned Features

- Create an encrypted vault
- Unlock a vault using a master password
- Add password entries
- List saved services
- View and edit entries
- Generate strong passwords
- Copy passwords to clipboard
- Run locally without requiring a cloud account

## Tech Stack

- Python
- Argon2id for key derivation
- AES-GCM for encryption
- JSON for the internal vault structure
- CLI first, GUI later

## Security Notice

This project is educational and should not be used to store real passwords until it has been properly reviewed and tested.
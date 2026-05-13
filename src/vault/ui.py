import tkinter.messagebox as messagebox
from pathlib import Path
from typing import Any

import customtkinter as ctk

from vault.clipboard import ClipboardError, copy_to_clipboard
from vault.entries import add_entry, create_entry, find_entries, get_entries
from vault.password_generator import (
    DEFAULT_PASSWORD_LENGTH,
    PasswordGenerationError,
    generate_password,
)
from vault.vault_file import (
    InvalidMasterPasswordError,
    InvalidVaultFileError,
    VaultNotFoundError,
    open_vault,
    save_vault,
)


class VaultApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("VAULT")
        self.geometry("1080x700")
        self.minsize(960, 620)

        self.configure(fg_color="#0f1117")

        self.vault_path: Path | None = None
        self.master_password: str | None = None
        self.vault_data: dict[str, Any] | None = None
        self.selected_entry: dict[str, Any] | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame: ctk.CTkFrame | None = None
        self.main_frame: ctk.CTkFrame | None = None

        self.search_entry: ctk.CTkEntry | None = None
        self.entries_frame: ctk.CTkScrollableFrame | None = None

        self.detail_title_label: ctk.CTkLabel | None = None
        self.detail_username_label: ctk.CTkLabel | None = None
        self.detail_url_label: ctk.CTkLabel | None = None
        self.detail_notes_label: ctk.CTkLabel | None = None
        self.detail_dates_label: ctk.CTkLabel | None = None

        self.copy_button: ctk.CTkButton | None = None
        self.delete_button: ctk.CTkButton | None = None

        self.show_login_screen()

    def clear_screen(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self) -> None:
        self.clear_screen()

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        self.login_frame = ctk.CTkFrame(
            outer,
            width=500,
            height=500,
            corner_radius=10,
            fg_color="#151923",
            border_width=1,
            border_color="#252a35",
        )
        self.login_frame.grid(row=0, column=0, padx=40, pady=40)
        self.login_frame.grid_propagate(False)
        self.login_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self.login_frame,
            text="VAULT",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#f3f4f6",
        )
        title_label.grid(row=0, column=0, padx=34, pady=(58, 6), sticky="w")

        subtitle_label = ctk.CTkLabel(
            self.login_frame,
            text="Encrypted password vault",
            font=ctk.CTkFont(size=14),
            text_color="#8b93a3",
        )
        subtitle_label.grid(row=1, column=0, padx=34, pady=(0, 36), sticky="w")

        self.vault_path_entry = ctk.CTkEntry(
            self.login_frame,
            width=432,
            height=42,
            corner_radius=6,
            placeholder_text="Vault path",
            fg_color="#0f1219",
            border_color="#252a35",
        )
        self.vault_path_entry.grid(row=2, column=0, padx=34, pady=8, sticky="ew")
        self.vault_path_entry.insert(0, "my-passwords.vault")

        self.master_password_entry = ctk.CTkEntry(
            self.login_frame,
            width=432,
            height=42,
            corner_radius=6,
            placeholder_text="Master password",
            show="*",
            fg_color="#0f1219",
            border_color="#252a35",
        )
        self.master_password_entry.grid(row=3, column=0, padx=34, pady=8, sticky="ew")
        self.master_password_entry.bind("<Return>", lambda _event: self.open_vault_from_login())

        open_button = ctk.CTkButton(
            self.login_frame,
            text="Open vault",
            height=42,
            corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.open_vault_from_login,
        )
        open_button.grid(row=4, column=0, padx=34, pady=(24, 12), sticky="ew")

        hint_label = ctk.CTkLabel(
            self.login_frame,
            text="Open an existing local vault file.",
            text_color="#6b7280",
            font=ctk.CTkFont(size=13),
        )
        hint_label.grid(row=5, column=0, padx=34, pady=(12, 30), sticky="w")

    def open_vault_from_login(self) -> None:
        vault_path_text = self.vault_path_entry.get().strip()
        master_password = self.master_password_entry.get()

        if not vault_path_text:
            messagebox.showerror("Error", "Vault path cannot be empty.")
            return

        if not master_password:
            messagebox.showerror("Error", "Master password cannot be empty.")
            return

        vault_path = Path(vault_path_text)

        try:
            vault_data = open_vault(vault_path, master_password)
        except VaultNotFoundError:
            messagebox.showerror("Error", f"Vault not found:\n{vault_path}")
            return
        except InvalidMasterPasswordError:
            messagebox.showerror("Error", "Invalid master password or corrupted vault.")
            return
        except InvalidVaultFileError as error:
            messagebox.showerror("Error", f"Invalid vault file:\n{error}")
            return

        self.vault_path = vault_path
        self.master_password = master_password
        self.vault_data = vault_data

        self.show_main_screen()

    def show_main_screen(self) -> None:
        self.clear_screen()

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f1117")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_columnconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_detail_panel()
        self.refresh_entries_list()

    def build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self.main_frame,
            width=330,
            corner_radius=0,
            fg_color="#10131a",
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(4, weight=1)

        app_label = ctk.CTkLabel(
            sidebar,
            text="VAULT",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#f3f4f6",
        )
        app_label.grid(row=0, column=0, padx=24, pady=(28, 4), sticky="w")

        vault_label = ctk.CTkLabel(
            sidebar,
            text=str(self.vault_path),
            text_color="#8b93a3",
            font=ctk.CTkFont(size=13),
            wraplength=270,
            justify="left",
        )
        vault_label.grid(row=1, column=0, padx=24, pady=(0, 22), sticky="w")

        self.search_entry = ctk.CTkEntry(
            sidebar,
            height=40,
            corner_radius=6,
            placeholder_text="Search entries",
            fg_color="#0f1219",
            border_color="#252a35",
        )
        self.search_entry.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_entries_list())

        section_label = ctk.CTkLabel(
            sidebar,
            text="ENTRIES",
            text_color="#6b7280",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        section_label.grid(row=3, column=0, padx=24, pady=(0, 6), sticky="w")

        self.entries_frame = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_button_color="#252a35",
            scrollbar_button_hover_color="#353b49",
        )
        self.entries_frame.grid(row=4, column=0, padx=14, pady=(0, 12), sticky="nsew")

        add_button = ctk.CTkButton(
            sidebar,
            text="+ Add entry",
            height=40,
            corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.show_add_entry_window,
        )
        add_button.grid(row=5, column=0, padx=20, pady=(8, 8), sticky="ew")

        lock_button = ctk.CTkButton(
            sidebar,
            text="Lock vault",
            height=38,
            corner_radius=6,
            fg_color="#252a35",
            hover_color="#353b49",
            command=self.lock_vault,
        )
        lock_button.grid(row=6, column=0, padx=20, pady=(0, 24), sticky="ew")

    def build_detail_panel(self) -> None:
        detail_panel = ctk.CTkFrame(
            self.main_frame,
            corner_radius=10,
            fg_color="#151923",
            border_width=1,
            border_color="#252a35",
        )
        detail_panel.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
        detail_panel.grid_columnconfigure(0, weight=1)
        detail_panel.grid_rowconfigure(5, weight=1)

        eyebrow = ctk.CTkLabel(
            detail_panel,
            text="SELECTED ENTRY",
            text_color="#6b7280",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        eyebrow.grid(row=0, column=0, padx=28, pady=(28, 6), sticky="w")

        self.detail_title_label = ctk.CTkLabel(
            detail_panel,
            text="No entry selected",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#f3f4f6",
            anchor="w",
        )
        self.detail_title_label.grid(row=1, column=0, padx=28, pady=(0, 12), sticky="ew")

        info_card = ctk.CTkFrame(
            detail_panel,
            corner_radius=8,
            fg_color="#0f1219",
            border_width=1,
            border_color="#1d222c",
        )
        info_card.grid(row=2, column=0, padx=28, pady=10, sticky="ew")
        info_card.grid_columnconfigure(0, weight=1)

        self.detail_username_label = ctk.CTkLabel(
            info_card,
            text="Username/email: —",
            text_color="#d1d5db",
            font=ctk.CTkFont(size=15),
            anchor="w",
        )
        self.detail_username_label.grid(row=0, column=0, padx=18, pady=(16, 7), sticky="ew")

        self.detail_url_label = ctk.CTkLabel(
            info_card,
            text="URL: —",
            text_color="#d1d5db",
            font=ctk.CTkFont(size=15),
            anchor="w",
        )
        self.detail_url_label.grid(row=1, column=0, padx=18, pady=7, sticky="ew")

        self.detail_dates_label = ctk.CTkLabel(
            info_card,
            text="Created: —    Updated: —",
            text_color="#8b93a3",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        self.detail_dates_label.grid(row=2, column=0, padx=18, pady=(7, 16), sticky="ew")

        notes_title = ctk.CTkLabel(
            detail_panel,
            text="Notes",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#f3f4f6",
        )
        notes_title.grid(row=3, column=0, padx=28, pady=(18, 6), sticky="w")

        notes_card = ctk.CTkFrame(
            detail_panel,
            corner_radius=8,
            fg_color="#0f1219",
            border_width=1,
            border_color="#1d222c",
        )
        notes_card.grid(row=4, column=0, padx=28, pady=(0, 12), sticky="nsew")
        notes_card.grid_columnconfigure(0, weight=1)
        notes_card.grid_rowconfigure(0, weight=1)

        self.detail_notes_label = ctk.CTkLabel(
            notes_card,
            text="Select an entry from the left panel.",
            text_color="#8b93a3",
            font=ctk.CTkFont(size=15),
            justify="left",
            anchor="nw",
            wraplength=620,
        )
        self.detail_notes_label.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")

        button_frame = ctk.CTkFrame(detail_panel, fg_color="transparent")
        button_frame.grid(row=6, column=0, padx=28, pady=(12, 28), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.copy_button = ctk.CTkButton(
            button_frame,
            text="Copy password",
            height=42,
            corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.copy_selected_password,
            state="disabled",
        )
        self.copy_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete entry",
            height=42,
            corner_radius=6,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.delete_selected_entry,
            state="disabled",
        )
        self.delete_button.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def refresh_entries_list(self) -> None:
        if self.entries_frame is None or self.vault_data is None:
            return

        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        query = ""

        if self.search_entry is not None:
            query = self.search_entry.get().strip()

        entries = find_entries(self.vault_data, query) if query else get_entries(self.vault_data)

        if not entries:
            empty_card = ctk.CTkFrame(
                self.entries_frame,
                corner_radius=8,
                fg_color="#151923",
                border_width=1,
                border_color="#1d222c",
            )
            empty_card.pack(fill="x", padx=6, pady=10)

            empty_label = ctk.CTkLabel(
                empty_card,
                text="No entries found",
                text_color="#8b93a3",
                font=ctk.CTkFont(size=14),
            )
            empty_label.pack(padx=14, pady=22)
            return

        for entry in entries:
            service = entry.get("service", "Unknown service")
            username = entry.get("username", "")

            card = ctk.CTkFrame(
                self.entries_frame,
                corner_radius=8,
                fg_color="#151923",
                border_width=1,
                border_color="#1d222c",
            )
            card.pack(fill="x", padx=6, pady=5)

            button_text = service
            if username:
                button_text += f"\n{username}"

            entry_button = ctk.CTkButton(
                card,
                text=button_text,
                height=58,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#202633",
                anchor="w",
                text_color="#f3f4f6",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda selected=entry: self.select_entry(selected),
            )
            entry_button.pack(fill="x", padx=3, pady=3)

    def select_entry(self, entry: dict[str, Any]) -> None:
        self.selected_entry = entry

        service = entry.get("service", "") or "Untitled entry"
        username = entry.get("username", "") or "—"
        url = entry.get("url", "") or "—"
        notes = entry.get("notes", "") or "No notes."
        created_at = entry.get("created_at", "") or "—"
        updated_at = entry.get("updated_at", "") or "—"

        if self.detail_title_label is not None:
            self.detail_title_label.configure(text=service)

        if self.detail_username_label is not None:
            self.detail_username_label.configure(text=f"Username/email: {username}")

        if self.detail_url_label is not None:
            self.detail_url_label.configure(text=f"URL: {url}")

        if self.detail_dates_label is not None:
            self.detail_dates_label.configure(
                text=f"Created: {created_at}    Updated: {updated_at}"
            )

        if self.detail_notes_label is not None:
            self.detail_notes_label.configure(text=notes)

        if self.copy_button is not None:
            self.copy_button.configure(state="normal")

        if self.delete_button is not None:
            self.delete_button.configure(state="normal")

    def copy_selected_password(self) -> None:
        if self.selected_entry is None:
            messagebox.showinfo("No entry selected", "Select an entry first.")
            return

        password = self.selected_entry.get("password", "")

        if not password:
            messagebox.showerror("Error", "Selected entry has no password.")
            return

        try:
            copy_to_clipboard(password)
        except ClipboardError as error:
            messagebox.showerror("Clipboard error", str(error))
            return

        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def delete_selected_entry(self) -> None:
        if self.selected_entry is None:
            messagebox.showinfo("No entry selected", "Select an entry first.")
            return

        if self.vault_data is None or self.vault_path is None or self.master_password is None:
            messagebox.showerror("Error", "Vault is not unlocked.")
            return

        service = self.selected_entry.get("service", "Unknown service")

        confirmed = messagebox.askyesno(
            "Confirm delete",
            f"Delete entry '{service}'?",
        )

        if not confirmed:
            return

        entries = get_entries(self.vault_data)
        entry_id = self.selected_entry.get("id")

        self.vault_data["entries"] = [
            entry for entry in entries
            if entry.get("id") != entry_id
        ]

        save_vault(self.vault_path, self.vault_data, self.master_password)

        self.selected_entry = None
        self.refresh_entries_list()
        self.clear_detail_panel()

        messagebox.showinfo("Deleted", f"Entry deleted: {service}")

    def clear_detail_panel(self) -> None:
        if self.detail_title_label is not None:
            self.detail_title_label.configure(text="No entry selected")

        if self.detail_username_label is not None:
            self.detail_username_label.configure(text="Username/email: —")

        if self.detail_url_label is not None:
            self.detail_url_label.configure(text="URL: —")

        if self.detail_dates_label is not None:
            self.detail_dates_label.configure(text="Created: —    Updated: —")

        if self.detail_notes_label is not None:
            self.detail_notes_label.configure(text="Select an entry from the left panel.")

        if self.copy_button is not None:
            self.copy_button.configure(state="disabled")

        if self.delete_button is not None:
            self.delete_button.configure(state="disabled")

    def show_add_entry_window(self) -> None:
        if self.vault_data is None or self.vault_path is None or self.master_password is None:
            messagebox.showerror("Error", "Vault is not unlocked.")
            return

        window = ctk.CTkToplevel(self)
        window.title("Add entry")
        window.geometry("560x650")
        window.resizable(False, False)
        window.configure(fg_color="#0f1117")
        window.grab_set()

        window.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(
            window,
            corner_radius=10,
            fg_color="#151923",
            border_width=1,
            border_color="#252a35",
        )
        form.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            form,
            text="Add new entry",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=26, pady=(28, 18), sticky="w")

        service_entry = ctk.CTkEntry(
            form,
            height=42,
            corner_radius=6,
            placeholder_text="Service",
            fg_color="#10131a",
            border_color="#2c3340",
        )
        service_entry.grid(row=1, column=0, padx=26, pady=7, sticky="ew")

        username_entry = ctk.CTkEntry(
            form,
            height=42,
            corner_radius=6,
            placeholder_text="Username/email",
            fg_color="#10131a",
            border_color="#2c3340",
        )
        username_entry.grid(row=2, column=0, padx=26, pady=7, sticky="ew")

        password_entry = ctk.CTkEntry(
            form,
            height=42,
            corner_radius=6,
            placeholder_text="Password",
            show="*",
            fg_color="#10131a",
            border_color="#2c3340",
        )
        password_entry.grid(row=3, column=0, padx=26, pady=7, sticky="ew")

        url_entry = ctk.CTkEntry(
            form,
            height=42,
            corner_radius=6,
            placeholder_text="URL",
            fg_color="#10131a",
            border_color="#2c3340",
        )
        url_entry.grid(row=4, column=0, padx=26, pady=7, sticky="ew")

        notes_label = ctk.CTkLabel(
            form,
            text="Notes",
            text_color="#9ca3af",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        notes_label.grid(row=5, column=0, padx=26, pady=(14, 4), sticky="w")

        notes_entry = ctk.CTkTextbox(
            form,
            height=130,
            corner_radius=6,
            fg_color="#10131a",
            border_width=1,
            border_color="#2c3340",
        )
        notes_entry.grid(row=6, column=0, padx=26, pady=(0, 8), sticky="ew")

        def generate_into_password_field() -> None:
            try:
                password = generate_password(length=DEFAULT_PASSWORD_LENGTH)
            except PasswordGenerationError as error:
                messagebox.showerror("Error", str(error))
                return

            password_entry.configure(show="")
            password_entry.delete(0, "end")
            password_entry.insert(0, password)

        generate_button = ctk.CTkButton(
            form,
            text="Generate password",
            height=42,
            corner_radius=6,
            fg_color="#252a35",
            hover_color="#303746",
            command=generate_into_password_field,
        )
        generate_button.grid(row=7, column=0, padx=26, pady=(14, 8), sticky="ew")

        def save_entry_from_form() -> None:
            service = service_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            url = url_entry.get().strip()
            notes = notes_entry.get("1.0", "end").strip()

            if not service:
                messagebox.showerror("Error", "Service cannot be empty.")
                return

            if not password:
                messagebox.showerror("Error", "Password cannot be empty.")
                return

            entry = create_entry(
                service=service,
                username=username,
                password=password,
                url=url,
                notes=notes,
            )

            add_entry(self.vault_data, entry)
            save_vault(self.vault_path, self.vault_data, self.master_password)

            self.refresh_entries_list()
            window.destroy()

            messagebox.showinfo("Saved", f"Entry added: {service}")

        save_button = ctk.CTkButton(
            form,
            text="Save entry",
            height=44,
            corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=save_entry_from_form,
        )
        save_button.grid(row=8, column=0, padx=26, pady=(8, 26), sticky="ew")

    def lock_vault(self) -> None:
        self.vault_path = None
        self.master_password = None
        self.vault_data = None
        self.selected_entry = None
        self.show_login_screen()


def run_app() -> None:
    app = VaultApp()
    app.mainloop()
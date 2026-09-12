"""Shared visual theme for the Zero Study desktop app."""
import tkinter as tk
from tkinter import ttk

BG = "#FBF6EE"
CARD_BG = "#FFFFFF"
ACCENT = "#FF7A45"
ACCENT_DARK = "#E85F2A"
TEXT = "#2B2418"
MUTED = "#8A7F6D"
BORDER = "#F0E4D2"
ROW_ALT = "#FDF1E2"

FONT_TITLE = ("Helvetica", 24, "bold")
FONT_SUBTITLE = ("Helvetica", 13)
FONT_HEADING = ("Helvetica", 14, "bold")
FONT_BODY = ("Helvetica", 12)
FONT_BUTTON = ("Helvetica", 12, "bold")


def apply_theme(root: tk.Tk) -> None:
    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD_BG)

    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SUBTITLE)
    style.configure("Heading.TLabel", background=BG, foreground=TEXT, font=FONT_HEADING)

    style.configure(
        "TNotebook", background=BG, borderwidth=0, tabmargins=(12, 10, 12, 0)
    )
    style.configure(
        "TNotebook.Tab",
        background=BG,
        foreground=MUTED,
        font=("Helvetica", 12, "bold"),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", CARD_BG)],
        foreground=[("selected", ACCENT_DARK)],
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="white",
        font=FONT_BUTTON,
        padding=(14, 8),
        borderwidth=0,
        focuscolor=ACCENT,
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_DARK), ("disabled", BORDER)],
        foreground=[("disabled", MUTED)],
    )

    style.configure(
        "Secondary.TButton",
        background=CARD_BG,
        foreground=ACCENT_DARK,
        font=FONT_BUTTON,
        padding=(14, 8),
        borderwidth=1,
        relief="solid",
    )
    style.map("Secondary.TButton", background=[("active", ROW_ALT)])

    style.configure(
        "TEntry", fieldbackground=CARD_BG, background=CARD_BG, foreground=TEXT,
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=6,
    )
    style.configure(
        "TCombobox", fieldbackground=CARD_BG, background=CARD_BG, foreground=TEXT, padding=6,
    )

    style.configure(
        "Treeview",
        background=CARD_BG,
        fieldbackground=CARD_BG,
        foreground=TEXT,
        rowheight=28,
        font=FONT_BODY,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=BG,
        foreground=MUTED,
        font=("Helvetica", 11, "bold"),
        borderwidth=0,
        relief="flat",
    )
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])


def style_treeview_stripes(tree: ttk.Treeview) -> None:
    tree.tag_configure("odd", background=ROW_ALT)
    tree.tag_configure("even", background=CARD_BG)

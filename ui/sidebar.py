import customtkinter as ctk
import os
import json
from PIL import Image, ImageTk

from services.printer_service import listar_impressoras
from src.config import resource_path

class Sidebar:
    def __init__(self, master, app, on_preset_change=None, on_scaling_change=None):
        self.app = app
        self.master = master
        self.on_preset_change = on_preset_change
        self.on_scaling_change = on_scaling_change

        self.sidebar = ctk.CTkFrame(master, width=280, corner_radius=0, fg_color="#F2F4F7")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self._build_logo()
        self._build_printers()
        self._build_presets()
        self._build_scaling()
        self._load_signature()

    # ------------------------
    # LOGO
    # ------------------------
    def _build_logo(self):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(pady=(30, 10), padx=10)

        logo_path = resource_path("assets/img/logo_transparente.png")

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                proporcao = 240 / img.size[0]
                size = (240, int(img.size[1] * proporcao))

                self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                ctk.CTkLabel(frame, image=self.logo_img, text="").pack()
                return
            except:
                pass

        ctk.CTkLabel(frame, text="RFID MARLUVAS", font=("Montserrat", 24, "bold")).pack()

    # ------------------------
    # IMPRESSORAS
    # ------------------------
    def _build_printers(self):
        ctk.CTkLabel(self.sidebar, text="DISPOSITIVOS", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)

        self.combo_printers = ctk.CTkComboBox(
            self.sidebar,
            values=listar_impressoras(),
            variable=self.app.printer_var,
            width=220
        )
        self.combo_printers.pack(pady=5, padx=20)

    # ------------------------
    # PRESETS
    # ------------------------
    def _build_presets(self):
        ctk.CTkLabel(self.sidebar, text="TAMANHO ETIQUETA", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)

        self.combo_presets = ctk.CTkComboBox(
            self.sidebar,
            values=["95x25 mm", "100x50 mm"],
            command=self._on_preset_change,
            width=220
        )
        self.combo_presets.set("95x25 mm")
        self.combo_presets.pack(pady=5, padx=20)

    def _on_preset_change(self, valor):
        self.app.on_preset_change(valor)
        
    # ------------------------
    # SCALING
    # ------------------------
    def _build_scaling(self):
        ctk.CTkLabel(self.sidebar, text="Escala da Interface", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30, pady=(15, 0))

        self.combo_scaling = ctk.CTkComboBox(
            self.sidebar,
            values=["110%", "100%", "90%", "80%", "75%"],
            command=self._on_scaling_change,
            width=220
        )

        valor_atual = int(self._carregar_scaling() * 100)
        self.combo_scaling.set(f"{valor_atual}%")
        self.combo_scaling.pack(pady=5, padx=20)

    def _on_scaling_change(self, valor):
        scale = int(valor.replace("%", "")) / 100

        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)
        self._salvar_scaling(scale)

        if self.on_scaling_change:
            self.on_scaling_change(scale)

    def _carregar_scaling(self):
        try:
            with open("config.json") as f:
                return float(json.load(f).get("scaling", 1.0))
        except:
            return 1.0

    def _salvar_scaling(self, valor):
        with open("config.json", "w") as f:
            json.dump({"scaling": valor}, f)


    # ------------------------
    # ASSINATURA
    # ------------------------
    def _load_signature(self):
        path = resource_path("assets/img/assinatura.png")

        if os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((150, 60))
                self.img_sig = ImageTk.PhotoImage(img)

                ctk.CTkLabel(self.sidebar, image=self.img_sig, text="").pack(side="bottom", pady=30)
                ctk.CTkLabel(self.sidebar, text="Developed by:", font=("Segoe UI", 9), text_color="gray").pack(side="bottom")
            except Exception as e:
                print("Erro assinatura:", e)
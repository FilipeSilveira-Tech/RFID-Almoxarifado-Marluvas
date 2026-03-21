import customtkinter as ctk
from services.database import init_db, obter_proximo_epc
from ui.sidebar import Sidebar
from ui.tab_impressao import TabImpressao
from ui.tab_historico import TabHistorico
from ui.tab_ativos import TabAtivos

class AppRFID(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RFID Almoxarifado Marluvas - v1.1.0")
        self.geometry("1280x850")

        init_db()
        self.epc_inicial = obter_proximo_epc()
        self.printer_var = ctk.StringVar()

        self.conf_width_mm = ctk.StringVar(value="95")
        self.conf_height_mm = ctk.StringVar(value="25")
        self.conf_dpi = ctk.StringVar(value="8")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, app=self)

        self.conf_width_mm = ctk.StringVar(value="95")
        self.conf_height_mm = ctk.StringVar(value="25")

        # Tabs
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=20,
            fg_color="white",
            segmented_button_selected_color="#1A73E8"
        )
        self.tabview.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.tab_print = self.tabview.add("Emissão de Etiquetas")
        self.tab_history = self.tabview.add("Histórico Etiquetas")
        self.tab_ativos = self.tabview.add("Consulta de Ativos")
        

        # Instanciar abas
        self.impressao = TabImpressao(self.tab_print, app=self)
        self.historico = TabHistorico(self.tab_history, app=self)
        self.ativos = TabAtivos(self.tab_ativos, app=self)
    

    #--------
    # EVENTOS GLOBAIS
    # -------
    def on_preset_change(self, valor):
        largura, altura = valor.replace(" mm", "").split("x")

        self.conf_width_mm.set(largura)
        self.conf_height_mm.set(altura)

        if hasattr(self, "impressao"):
            self.impressao.gerar_preview()
        
        if hasattr(self, "historico"):
            self.historico.atualizar_tabela_historico()

    def get_printer(self):
        return self.combo_printers.get()
        
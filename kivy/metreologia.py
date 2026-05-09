from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

DADOS_CLIMA = {
    "lisboa": {"temp":"22°C", "condicao":"Sol"},
    "porto": {"temp": "18°C", "condicao": "Nublado"},
    "coimbra": {"temp": "13°C", "condicao": "Chuva"},
    "setubal": {"temp": "24°C", "condicao": "Parcialmente Nublado"},
}

class TelaClima(BoxLayout):
    resultado = StringProperty("Insira uma cidade e carregue em pesquisar")
    
    def buscar_clima(self):
        cidade = self.ids.entrada.text.lower().strip()
        if cidade in DADOS_CLIMA:
            clima = DADOS_CLIMA[cidade]
            self.resultado = f"{cidade.title()}: {clima['temp']} - {clima['condicao']}"
        else:
            self.resultado = f"{cidade.title()}: não encontrada na base de dados"

class Clima(App):
    def build(self):
        return TelaClima()

Clima().run()
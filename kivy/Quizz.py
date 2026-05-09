from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label

PERGUNTAS = [
    {
        "pergunta": "Qual é o total de QI dos alunos?",
        "respostas": ["-1", "5", "498"],
        "correta": "-1"
    },
    {
        "pergunta": "Qual é a capital de Portugal?",
        "respostas": ["Porto", "Lisboa", "Coimbra"],
        "correta": "Lisboa"
    },
    {
        "pergunta": "Quantos continentes existem?",
        "respostas": ["5", "6", "7"],
        "correta": "7"
    },
    {
        "pergunta": "Qual é o melhor país da Europa?",
        "respostas": ["USA", "Barreiro", "Finlandia"],
        "correta": "Barreiro"
    },
    {
        "pergunta": "Quantas pontes há no rio Tejo?",
        "respostas": ["2", "16", "13"],
        "correta": "16"
    }
]

class QuizLayout(BoxLayout):
    pergunta_text = StringProperty("")
    opcoes = ListProperty([])
    pontuacao = NumericProperty(0)
    index = NumericProperty(0)
    
    def on_kv_post(self, base_widget):
        self.carregar_proxima()
    
    def carregar_proxima(self):
        if self.index < len(PERGUNTAS):
            pergunta_atual = PERGUNTAS[self.index]
            self.pergunta_text = pergunta_atual["pergunta"]
            self.opcoes = pergunta_atual["respostas"]
        else:
            self.pergunta_text = "Fim do Quiz!"
            self.opcoes = []
            self.ids.resposta1.disabled = True
            self.ids.resposta2.disabled = True
            self.ids.resposta3.disabled = True
    
    def responder(self, resposta_escolhida):
        if self.index >= len(PERGUNTAS):
            return
        correta = PERGUNTAS[self.index]["correta"]
        if resposta_escolhida == correta:
            self.pontuacao += 1
            self.mostrar_popup("Certo!", "Resposta Correta!")
        else:
            self.mostrar_popup("Errado", f"A resposta correta era: {correta}")
        self.index += 1
        self.carregar_proxima()
    
    def mostrar_popup(self, titulo, mensagem):
        popup = Popup(title=titulo, content=Label(text=mensagem),
                     size_hint=(None, None), size=(300, 200))
        popup.open()

class QuizApp(App):
    def build(self):
        return QuizLayout()

QuizApp().run()

import sys
import datetime
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QVBoxLayout, QTimeEdit, QMessageBox, QListWidget, QHBoxLayout
)

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("PyQt Clock")
window.setGeometry(300, 300, 400, 500)

# Lista para armazenar múltiplos alarmes
alarme_hora = []
alarme_editando = None

def atualizar_hora():
    now = QTime.currentTime()
    label_hora.setText(now.toString("HH:mm:ss"))
    
    if now.second() == 0:
        hora_atual = now.toString("HH:mm")
        for alarme in alarme_hora:
            if alarme.toString("HH:mm") == hora_atual:
                disparar_alarme()
                atualizar_lista()
                break

def disparar_alarme():
    global alarme_hora
    QTimer.singleShot(2000, limpar)
    QMessageBox.information(window, "ALARME!", "🐷 ALARME! Hora de acordar")

def limpar():
    global alarme_hora
    # Função para limpar após o alarme (pode ser implementada depois)
    pass

def atualizar_lista():
    lista_alarme.clear()
    for alarme in alarme_hora:
        lista_alarme.addItem(alarme.toString("HH:mm"))

def defenir_alarme():
    global alarme_hora
    hora = input_alarme.time()
    alarme_hora.append(hora)
    atualizar_lista()

def editar_alarme():
    pass

def remove_alarme():
    index = lista_alarme.currentRow()
    if index < 0:
        return
    alarme_hora.pop(index)
    atualizar_lista()

central = QWidget()
layout = QVBoxLayout()

label_hora = QLabel()
label_hora.setStyleSheet("font-size:32px; text-align:center;")
layout.addWidget(label_hora)

lista_alarme = QListWidget()
lista_alarme.setMaximumHeight(120)
layout.addWidget(lista_alarme)

botoes_layout = QHBoxLayout()
btn_editar = QPushButton("Editar")
btn_editar.clicked.connect(editar_alarme)
btn_remover = QPushButton("Remover")
btn_remover.clicked.connect(remove_alarme)
botoes_layout.addWidget(btn_editar)
botoes_layout.addWidget(btn_remover)
layout.addLayout(botoes_layout)

input_alarme = QTimeEdit()
input_alarme.setDisplayFormat("HH:mm")
layout.addWidget(input_alarme)

btn_add_alarma = QPushButton("Add Alarma")
btn_add_alarma.clicked.connect(defenir_alarme)
layout.addWidget(btn_add_alarma)

central.setLayout(layout)
window.setCentralWidget(central)

# Configurar timer para atualizar a hora a cada segundo
timer = QTimer()
timer.timeout.connect(atualizar_hora)
timer.start(1000)

# Atualizar a hora imediatamente
atualizar_hora()

window.show()
sys.exit(app.exec_())


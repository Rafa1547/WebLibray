import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem
)

# Lista de Contactos
contactos = []
# Caminho do arquivo JSON relativo ao script
script_dir = os.path.dirname(os.path.abspath(__file__))
ficheiro_json = os.path.join(script_dir, "contactos.json")

def carregar_contactos():
    global contactos
    try:
        with open(ficheiro_json, "r", encoding="utf-8") as file:
            dados = json.load(file)2
            if isinstance(dados, list):
                contactos = dados
            else:
                contactos = []
    except FileNotFoundError:
        contactos = []
    except json.JSONDecodeError:
        contactos = []

def save_contactos():
    with open(ficheiro_json, "w", encoding="utf-8") as file:
        json.dump(contactos, file, indent=4, ensure_ascii=False)

def atualizar_tabela():
    tabela.setRowCount(0)
    tabela.setRowCount(len(contactos))
    for i, c in enumerate(contactos):
        nome = str(c.get("nome", ""))
        telefone = str(c.get("telefone", ""))
        email = str(c.get("email", ""))
        tabela.setItem(i, 0, QTableWidgetItem(nome))
        tabela.setItem(i, 1, QTableWidgetItem(telefone))
        tabela.setItem(i, 2, QTableWidgetItem(email))

def add_contact():
    nome = input_nome.text().strip()
    tel = input_telefone.text().strip()
    email = input_email.text().strip()
    if nome:
        contactos.append({"nome": nome, "telefone": tel, "email": email})
        atualizar_tabela()
        save_contactos()
        input_nome.clear()
        input_telefone.clear()
        input_email.clear()

def edit_contacto():
    line = tabela.currentRow()
    if line >= 0 and line < len(contactos):
        contactos[line] = {
            "nome": input_nome.text().strip(),
            "telefone": input_telefone.text().strip(),
            "email": input_email.text().strip()
        }
        atualizar_tabela()
        save_contactos()
        input_nome.clear()
        input_telefone.clear()
        input_email.clear()

def remove_contact():
    line = tabela.currentRow()
    if line >= 0 and line < len(contactos):
        del contactos[line]
        atualizar_tabela()
        save_contactos()
        input_nome.clear()
        input_telefone.clear()
        input_email.clear()

def fill_input():
    line = tabela.currentRow()
    if line >= 0 and line < len(contactos):
        c = contactos[line]
        input_nome.setText(str(c.get("nome", "")))
        input_telefone.setText(str(c.get("telefone", "")))
        input_email.setText(str(c.get("email", "")))

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Contact Manager")
window.setGeometry(300, 300, 600, 400)

central = QWidget()
layout = QVBoxLayout()

tabela = QTableWidget()
tabela.setColumnCount(3)
tabela.setHorizontalHeaderLabels(["Nome", "Telefone", "Email"])
tabela.cellClicked.connect(lambda row, col: fill_input())
layout.addWidget(tabela)

input_nome = QLineEdit()
input_telefone = QLineEdit()
input_email = QLineEdit()
inputs_layout = QHBoxLayout()
inputs_layout.addWidget(input_nome)
inputs_layout.addWidget(input_telefone)
inputs_layout.addWidget(input_email)

layout.addLayout(inputs_layout)

btn_add = QPushButton("Adicionar")
btn_edit = QPushButton("Editar")
btn_rm = QPushButton("Remover")
btn_add.clicked.connect(add_contact)
btn_edit.clicked.connect(edit_contacto)
btn_rm.clicked.connect(remove_contact)

btn_layout = QHBoxLayout()
btn_layout.addWidget(btn_add)
btn_layout.addWidget(btn_edit)
btn_layout.addWidget(btn_rm)

layout.addLayout(btn_layout)

central.setLayout(layout)
window.setCentralWidget(central)

carregar_contactos()
atualizar_tabela()

window.show()
sys.exit(app.exec_())



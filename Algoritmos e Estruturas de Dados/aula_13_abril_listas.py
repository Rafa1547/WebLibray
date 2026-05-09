turma = ["Ana", "Bruno", "Carla", "Diego"]

print("Turma inicial:", turma)
print("Quantidade de alunos:", len(turma))

turma.append("Eduarda")
print("Depois de adicionar Eduarda:", turma)

# Remove um aluno pelo nome
turma.remove("Bruno")
print("Depois de remover Bruno:", turma)

# Mostra cada aluno com sua posição
print("\nLista final da turma:")
for posicao, aluno in enumerate(turma, start=1):
    print(f"{posicao}º aluno: {aluno}")

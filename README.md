# Projeto Final: Treino de IA - Evolução de Criaturas (v3.0)

Este projeto demonstra a integração de **NumPy**, **Pygame** e **Matplotlib** para simular a evolução de criaturas usando um algoritmo genético e redes neuronais. As criaturas usam sensores de distância (raycasting) para detetar obstáculos — estáticos ou móveis — e progridem por checkpoints e níveis de dificuldade crescente.

## Novidades na Versão 3.0
- **Sensores reais (raycasting):** cada agente lança 8 raios à sua volta que medem a distância ao obstáculo ou parede mais próxima. A rede neuronal recebe estas leituras como input, permitindo que aprenda a desviar-se *antes* de bater, em vez de detetar a colisão só ao tocar.
- **Checkpoints intermédios:** em vez de um único alvo distante, os agentes atravessam pontos de passagem que dão fitness parcial — acelera a aprendizagem ao dar sinal de progresso.
- **Níveis progressivos:** três níveis de dificuldade crescente. A população avança automaticamente de nível quando atinge uma taxa de sucesso mínima na geração atual.
- **Obstáculos móveis:** o nível 3 introduz obstáculos que oscilam, obrigando a rede a reagir em tempo real em vez de memorizar um mapa estático.
- **Guardar/carregar o melhor cérebro:** os pesos do agente com melhor fitness podem ser guardados em disco (`best_brain.npz`) e recarregados mais tarde para continuar o treino ou demonstrar um "campeão" já treinado.
- **Hall da Fama:** o cérebro do melhor agente que já chegou ao alvo (em toda a execução, não só na geração atual) é sempre preservado e garantido na geração seguinte. Mesmo que uma geração tenha azar e nenhum elite vença, a população nunca "esquece" o melhor comportamento já alcançado. Agentes que chegam ao alvo ganham também uma auréola dourada visível no ecrã.

## Descrição dos Módulos
- **NumPy:** motor matemático para a rede neuronal (forward propagation) e manipulação genética dos pesos (crossover, mutação).
- **Pygame:** motor gráfico interativo — colisões, raycasting (`Rect.clipline`), obstáculos móveis e interface de utilizador.
- **Matplotlib:** geração automática do gráfico de desempenho (`evolution_stats.png`), incluindo marcação visual das transições de nível.

## Como Executar

### Pré-requisitos
```bash
pip install pygame numpy matplotlib
```

### Comandos
1. Executa o ficheiro principal:
   ```bash
   python main.py
   ```
2. **Controlos durante a simulação:**
   | Tecla | Ação |
   |---|---|
   | `P` | Pausar / Retomar |
   | `R` | Reiniciar a evolução no nível atual |
   | `N` | Avançar manualmente para o próximo nível |
   | `V` | Mostrar/ocultar os raios de sensores do melhor agente vivo |
   | `S` | Guardar o cérebro do melhor agente da geração atual |
   | `L` | Carregar o cérebro guardado e injetá-lo na população |
   | Fechar janela | Encerra e guarda o gráfico final |

## Estrutura do Projeto
```
evolution_project/
├── main.py            # Configurações, loop principal e algoritmo genético
└── src/
    ├── engine.py       # Ambiente, Agentes, Obstáculos, raycasting e checkpoints
    ├── ia.py            # Rede Neuronal, Algoritmo Genético e save/load
    ├── levels.py        # Configuração dos níveis (obstáculos, checkpoints, alvo)
    └── stats.py          # Monitorização e gráficos
```

## Como Funcionam os Sensores
Cada agente lança 8 raios em direções espaçadas uniformemente (a cada 45°) até um alcance máximo de 180 píxeis. Para cada raio, a distância até ao primeiro obstáculo (ou parede) é normalizada entre 0 (a tocar) e 1 (caminho livre). Estes 8 valores juntam-se à posição, velocidade e direção ao alvo, totalizando **14 inputs** para a rede neuronal (em vez dos 6 da versão anterior).

## Sistema de Níveis e Checkpoints
Cada nível (definido em `src/levels.py`) tem o seu próprio alvo, lista de checkpoints e obstáculos. Quando a percentagem de agentes que atinge o alvo numa geração ultrapassa o `success_threshold` definido no nível, a simulação avança automaticamente para o nível seguinte, mantendo os melhores cérebros já evoluídos. O último nível tem `success_threshold = 1.1`, o que garante que nunca avança sozinho (é o desafio final).

## Hall da Fama
Sempre que um agente chega ao ponto azul (alvo final), o seu cérebro é comparado com o melhor vencedor registado até ao momento (`Simulation.hall_of_fame_brain`). Se for melhor, torna-se o novo recorde. Este cérebro campeão é **sempre** incluído, sem mutação, na geração seguinte — mesmo que os elites dessa geração específica não tenham vencido por azar (por exemplo, num nível com obstáculos móveis). Isto garante que a população nunca regride abaixo do melhor comportamento já descoberto. O recorde atual é mostrado no painel de informações ("Recorde (Hall da Fama)") e os agentes vencedores ganham uma auréola dourada no ecrã.

## Configurações (em main.py)
- `POPULATION_SIZE`: número de agentes por geração.
- `MUTATION_RATE`: probabilidade de mutação genética (ex.: 0.05 para 5%).
- `ELITISM_PERCENT`: percentagem dos melhores agentes que passam intactos para a próxima geração.

## Configurações (em src/levels.py)
- `obstacles`: lista de obstáculos por nível; adiciona `"moving": True, "axis": "x"|"y", "speed": float, "range": float` para criar obstáculos móveis.
- `checkpoints`: lista ordenada de pontos de passagem.
- `success_threshold`: taxa de sucesso (0 a 1) necessária para avançar de nível.

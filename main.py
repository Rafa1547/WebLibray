import os
import random
import sys

import numpy as np
import pygame

from src.engine import Agent, Simulation, WIDTH, HEIGHT, INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE
from src.ia import GeneticAlgorithm, NeuralNetwork
from src.levels import LEVELS
from src.stats import StatsTracker

# PARÂMETROS CONFIGURÁVEIS PELO UTILIZADOR
POPULATION_SIZE = 60
MUTATION_RATE = 0.05
ELITISM_PERCENT = 0.1
FPS = 60
BRAIN_SAVE_PATH = "best_brain.npz"


def evolve_population(simulation):
    """Avalia o fitness de todos os agentes e gera a lista de cérebros
    (elites + Hall da Fama + descendentes por crossover/mutação) para a
    próxima geração. Devolve também se houve um novo recorde de sempre."""
    fitness_list = []
    success_count = 0
    for agent in simulation.agents:
        agent.calculate_fitness(simulation.target)
        fitness_list.append(agent.fitness)
        if agent.reached_target:
            success_count += 1

    new_record = simulation.update_hall_of_fame(simulation.agents)

    sorted_agents = sorted(simulation.agents, key=lambda a: a.fitness, reverse=True)
    num_elites = max(1, int(POPULATION_SIZE * ELITISM_PERCENT))
    best_agents = sorted_agents[:num_elites]

    new_brains = [elite.brain for elite in best_agents]

    # O campeão de sempre (Hall da Fama) é sempre garantido na próxima
    # geração, mesmo que os elites desta geração tenham tido azar.
    champion = simulation.hall_of_fame_brain
    if champion is not None and all(champion is not b for b in new_brains):
        new_brains.append(champion)

    while len(new_brains) < POPULATION_SIZE:
        p1 = random.choice(best_agents)
        p2 = random.choice(best_agents)
        child_weights = GeneticAlgorithm.crossover(p1.brain.get_weights(), p2.brain.get_weights())
        mutated_weights = GeneticAlgorithm.mutate(child_weights, mutation_rate=MUTATION_RATE)
        child_brain = NeuralNetwork(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
        child_brain.set_weights(mutated_weights)
        new_brains.append(child_brain)

    return new_brains, fitness_list, success_count, new_record


def save_best_brain(simulation):
    alive_or_not = simulation.agents
    if not alive_or_not:
        return
    best = max(alive_or_not, key=lambda a: a.fitness)
    best.brain.save(BRAIN_SAVE_PATH)
    print(f"Cérebro guardado em '{BRAIN_SAVE_PATH}' (fitness={best.fitness:.4f})")


def load_brain_into_population(simulation):
    if not os.path.exists(BRAIN_SAVE_PATH):
        print("Nenhum cérebro guardado encontrado. Usa [S] primeiro para guardar um.")
        return
    loaded_brain = NeuralNetwork.load(BRAIN_SAVE_PATH)
    new_brains = [loaded_brain]
    while len(new_brains) < simulation.pop_size:
        mutated = GeneticAlgorithm.mutate(loaded_brain.get_weights(), mutation_rate=MUTATION_RATE)
        brain = NeuralNetwork(loaded_brain.input_size, loaded_brain.hidden_size, loaded_brain.output_size)
        brain.set_weights(mutated)
        new_brains.append(brain)
    simulation.reset_agents(brains=new_brains)
    print(f"Cérebro carregado de '{BRAIN_SAVE_PATH}' e injetado na população (1 clone + mutações).")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evolução IA: Sensores, Checkpoints e Níveis")
    clock = pygame.time.Clock()

    simulation = Simulation(POPULATION_SIZE, level_index=0)
    stats = StatsTracker()
    running = True
    paused = False

    font = pygame.font.SysFont("Segoe UI", 20, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 16)

    print("Iniciando Simulação...")
    print(f"População: {POPULATION_SIZE} | Mutação: {MUTATION_RATE * 100:.0f}% | Nível: {simulation.level_name}")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    simulation = Simulation(POPULATION_SIZE, level_index=simulation.level_index)
                    stats = StatsTracker()
                elif event.key == pygame.K_v:
                    simulation.show_rays = not simulation.show_rays
                elif event.key == pygame.K_n:
                    next_level = min(simulation.level_index + 1, len(LEVELS) - 1)
                    simulation.load_level(next_level)
                    simulation.reset_agents()
                    stats.add_level_change(simulation.generation, simulation.level_name)
                elif event.key == pygame.K_s:
                    save_best_brain(simulation)
                elif event.key == pygame.K_l:
                    load_brain_into_population(simulation)

        if not paused:
            simulation.update()

            screen.fill((20, 20, 25))
            simulation.draw(screen)

            overlay = pygame.Surface((260, 190), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (10, 10))

            gen_text = font.render(f"Geração: {simulation.generation}", True, (255, 215, 0))
            screen.blit(gen_text, (20, 20))

            level_text = small_font.render(simulation.level_name, True, (150, 220, 255))
            screen.blit(level_text, (20, 50))

            pop_text = small_font.render(f"População: {POPULATION_SIZE}", True, (255, 255, 255))
            screen.blit(pop_text, (20, 75))

            wins_text = small_font.render(f"Vitórias agora: {simulation.win_count()}", True, (255, 215, 0))
            screen.blit(wins_text, (20, 97))

            if simulation.hall_of_fame_brain is not None:
                record_text = small_font.render(
                    f"Recorde (Hall da Fama): {simulation.hall_of_fame_fitness:.2f}", True, (180, 255, 180)
                )
            else:
                record_text = small_font.render("Recorde (Hall da Fama): --", True, (180, 180, 180))
            screen.blit(record_text, (20, 119))

            instr1 = small_font.render("[P]ausa [R]eset [N]ível [V] Sensores", True, (200, 200, 200))
            screen.blit(instr1, (20, 144))
            instr2 = small_font.render("[S] Guardar cérebro  [L] Carregar", True, (200, 200, 200))
            screen.blit(instr2, (20, 166))

            pygame.display.flip()
            clock.tick(FPS)

            if simulation.all_dead():
                new_brains, fitness_list, success_count, new_record = evolve_population(simulation)

                avg_f = np.mean(fitness_list)
                max_f = np.max(fitness_list)
                success_rate = success_count / POPULATION_SIZE
                stats.add_data(simulation.generation, avg_f, max_f)
                print(
                    f"Gen {simulation.generation} | {simulation.level_name} | "
                    f"Max Fitness: {max_f:.4f} | Sucessos: {success_count}/{POPULATION_SIZE} "
                    f"({success_rate * 100:.0f}%)"
                )
                if new_record:
                    print(f">> NOVO RECORDE! Hall da Fama atualizado (fitness={simulation.hall_of_fame_fitness:.4f})")

                level = LEVELS[simulation.level_index]
                is_last_level = simulation.level_index == len(LEVELS) - 1
                simulation.generation += 1

                if not is_last_level and success_rate >= level["success_threshold"]:
                    print(f">> Critério atingido! A avançar para o nível seguinte...")
                    simulation.load_level(simulation.level_index + 1)
                    stats.add_level_change(simulation.generation, simulation.level_name)

                simulation.reset_agents(brains=new_brains)

                if simulation.generation % 5 == 0:
                    stats.plot_stats()

    pygame.quit()
    stats.plot_stats()
    sys.exit()


if __name__ == "__main__":
    main()

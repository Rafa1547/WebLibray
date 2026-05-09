#include <GL/glut.h>
#include <iostream>
#include <vector>

/**
 * UC: Computação Homem-Máquina 2025/26
 * TRABALHO PRÁTICO 1 (TP1)
 * O Posto de Triagem Robótico: Simulador de Automação de Processos
 */

// --- VARIÁVEIS DE ESTADO DO BRAÇO ROBÓTICO ---
float ombro = 0.0f;
float cotovelo = 0.0f;
float mao_rot = 0.0f;
float base_rot = 0.0f;

// --- VARIÁVEIS DE ESTADO DO PACOTE ---
bool pacoteAtivo = false;
bool pacoteAgarrado = false;
int tipoPacote = 0; // 1: Inválido, 2: Ligeiro, 3: Pesado

// --- POSIÇÃO DO PACOTE ---
float pacoteX = 2.0f, pacoteY = 0.0f, pacoteZ = 0.0f;

// --- REQUISITO: MANUAL DO OPERADOR (PAINEL DE BORDO) ---
void imprimirManual() {
    std::cout << "=====================================================" << std::endl;
    std::cout << "       MANUAL DO OPERADOR - POSTO DE TRIAGEM         " << std::endl;
    std::cout << "=====================================================" << std::endl;
    std::cout << " [CONTROLOS DO BRAÇO]" << std::endl;
    std::cout << "  - A / D : Rodar Base" << std::endl;
    std::cout << "  - W / S : Mover Ombro" << std::endl;
    std::cout << "  - Q / E : Mover Cotovelo" << std::endl;
    std::cout << "  - R / F : Rodar Mão" << std::endl;
    std::cout << std::endl;
    std::cout << " [AÇÕES]" << std::endl;
    std::cout << "  - ESPAÇO : Agarrar / Largar Pacote" << std::endl;
    std::cout << std::endl;
    std::cout << " [TESTE: GERAR PACOTES]" << std::endl;
    std::cout << "  - 1 : Gerar Pacote INVÁLIDO (Wireframe -> Vermelha)" << std::endl;
    std::cout << "  - 2 : Gerar Pacote LIGEIRO  (Sólido Pequeno -> Azul)" << std::endl;
    std::cout << "  - 3 : Gerar Pacote PESADO   (Sólido Grande -> Verde)" << std::endl;
    std::cout << "=====================================================" << std::endl;
}

// --- DESENHO DAS CAIXAS DE DESTINO ---
void desenhaCaixas() {
    // Caixa Vermelha (Rejeitados)
    glPushMatrix();
    glTranslatef(-3.0f, -1.0f, 2.0f);
    glColor3f(1.0f, 0.0f, 0.0f);
    glutWireCube(1.5f);
    glPopMatrix();

    // Caixa Azul (Ligeiros)
    glPushMatrix();
    glTranslatef(0.0f, -1.0f, 2.0f);
    glColor3f(0.0f, 0.0f, 1.0f);
    glutWireCube(1.5f);
    glPopMatrix();

    // Caixa Verde (Pesados)
    glPushMatrix();
    glTranslatef(3.0f, -1.0f, 2.0f);
    glColor3f(0.0f, 1.0f, 0.0f);
    glutWireCube(1.5f);
    glPopMatrix();
}

// --- REQUISITO: SIGNIFIERS VISUAIS DO PACOTE ---
void desenhaPacote() {
    if (!pacoteAtivo) return;

    glPushMatrix();
    // Se estiver agarrado, a posição é gerida pela hierarquia do braço
    if (!pacoteAgarrado) {
        glTranslatef(pacoteX, pacoteY, pacoteZ);
    }

    // Lógica de Signifiers baseada no tipo
    if (tipoPacote == 1) {
        // Registo Inválido: Wireframe (Holograma)
        glColor3f(1.0f, 0.5f, 0.5f);
        glutWireCube(0.5f);
    } else if (tipoPacote == 2) {
        // Peso Ligeiro: Sólido e Pequeno
        glColor3f(0.5f, 0.5f, 1.0f);
        glScalef(0.6f, 0.6f, 0.6f);
        glutSolidCube(0.5f);
    } else if (tipoPacote == 3) {
        // Peso Pesado: Sólido e Massivo
        glColor3f(0.5f, 1.0f, 0.5f);
        glScalef(1.5f, 1.5f, 1.5f);
        glutSolidCube(0.5f);
    }
    glPopMatrix();
}

// --- DESENHO DO BRAÇO ROBÓTICO (HIERARQUIA) ---
void desenhaBraço() {
    // Base
    glPushMatrix();
    glRotatef(base_rot, 0, 1, 0);
    glColor3f(0.3f, 0.3f, 0.3f);
    glScalef(1.0f, 0.2f, 1.0f);
    glutSolidCube(1.0f);
    glPopMatrix();

    // Ombro
    glPushMatrix();
    glRotatef(base_rot, 0, 1, 0);
    glTranslatef(0.0f, 0.1f, 0.0f);
    glRotatef(ombro, 0, 0, 1);
    glTranslatef(0.0f, 0.5f, 0.0f);
    glColor3f(0.5f, 0.5f, 0.5f);
    glPushMatrix();
    glScalef(0.2f, 1.0f, 0.2f);
    glutSolidCube(1.0f);
    glPopMatrix();

    // Cotovelo
    glTranslatef(0.0f, 0.5f, 0.0f);
    glRotatef(cotovelo, 0, 0, 1);
    glTranslatef(0.0f, 0.4f, 0.0f);
    glColor3f(0.7f, 0.7f, 0.7f);
    glPushMatrix();
    glScalef(0.15f, 0.8f, 0.15f);
    glutSolidCube(1.0f);
    glPopMatrix();

    // Mão
    glTranslatef(0.0f, 0.4f, 0.0f);
    glRotatef(mao_rot, 0, 1, 0);
    glColor3f(0.2f, 0.2f, 0.2f);
    glPushMatrix();
    glScalef(0.3f, 0.1f, 0.3f);
    glutSolidCube(1.0f);
    glPopMatrix();

    // REQUISITO: HIERARQUIA MATEMÁTICA (PACOTE FILHO DA MÃO)
    if (pacoteAgarrado) {
        glTranslatef(0.0f, 0.15f, 0.0f); // Posiciona o pacote na "palma"
        desenhaPacote();
    }

    glPopMatrix();
}

void display() {
    // REQUISITO: ILUSÃO DO MUNDO REAL (Z-BUFFER)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    // REQUISITO: EIXO Z (PROFUNDIDADE) - AFASTAR A CÂMARA
    glTranslatef(0.0f, 0.0f, -10.0f);
    glRotatef(20, 1, 0, 0); // Inclinação para melhor vista

    desenhaCaixas();
    
    // Se não estiver agarrado, desenha no tapete
    if (!pacoteAgarrado) {
        desenhaPacote();
    }

    desenhaBraço();

    glutSwapBuffers();
}

void reshape(int w, int h) {
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    // REQUISITO: PERSPEKTIVA CÓNICA
    gluPerspective(45.0, (float)w / (float)h, 1.0, 100.0);
    glMatrixMode(GL_MODELVIEW);
}

void keyboard(unsigned char key, int x, int y) {
    switch (key) {
        // Controlos do Braço
        case 'a': base_rot += 5.0f; break;
        case 'd': base_rot -= 5.0f; break;
        case 'w': ombro += 5.0f; break;
        case 's': ombro -= 5.0f; break;
        case 'q': cotovelo += 5.0f; break;
        case 'e': cotovelo -= 5.0f; break;
        case 'r': mao_rot += 5.0f; break;
        case 'f': mao_rot -= 5.0f; break;

        // REQUISITO: TECLAS DE TESTE (1, 2, 3)
        case '1': tipoPacote = 1; pacoteAtivo = true; pacoteAgarrado = false; break;
        case '2': tipoPacote = 2; pacoteAtivo = true; pacoteAgarrado = false; break;
        case '3': tipoPacote = 3; pacoteAtivo = true; pacoteAgarrado = false; break;

        // REQUISITO: AGARRAR / LARGAR (ESPAÇO)
        case ' ':
            if (pacoteAtivo) {
                if (!pacoteAgarrado) {
                    pacoteAgarrado = true;
                } else {
                    // REQUISITO: GESTÃO DE ESTADO (FIM DO CICLO)
                    // O pacote desaparece ao ser largado (simulando queda na caixa)
                    pacoteAgarrado = false;
                    pacoteAtivo = false;
                }
            }
            break;
        
        case 27: // ESC
            exit(0);
            break;
    }
    glutPostRedisplay();
}

void init() {
    // REQUISITO: LIGAR Z-BUFFER
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    imprimirManual();
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("Simulador de Triagem Robotica - TP1");

    init();

    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keyboard);

    glutMainLoop();
    return 0;
}
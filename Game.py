#arquivo do jogo
import pygame
import sys
import random
# Inicializando o Pygame
pygame.init()

# Configurando a tela
largura_tela = 800
altura_tela = 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption('Flappy Bird')

# Relógio 
relogio = pygame.time.Clock()

# Carregando imagens e fundo
personagem = pygame.image.load('personagem.png')
# aumentar o personagem 3x
pw, ph = personagem.get_size()
personagem = pygame.transform.scale(personagem, (pw * 3, ph * 3))

obstaculo_img = pygame.image.load('obstaculo.png')
# diminui o obstaculo pela metade
obstaculo_img = pygame.transform.scale(obstaculo_img, (60, int(altura_tela * 0.75)))

# vi que era melhor usar try. deixa assim klein; Carrega a imagem de fundo
try:
    fundo = pygame.image.load('fundo.png')
    fundo = pygame.transform.scale(fundo, (largura_tela, altura_tela))
except Exception:
    fundo = pygame.Surface((largura_tela, altura_tela))
    fundo.fill((0, 150, 255))  # cor azul 

# Posição e velocidade 
personagem_rect = personagem.get_rect(center=(largura_tela // 4, altura_tela // 2))
velocidade_y = 0
gravidade = 0.5
pulo = -10

# Obstaculos
lista_obstaculos = []
SPAWNOBSTACLE = pygame.USEREVENT
pygame.time.set_timer(SPAWNOBSTACLE, 1200)
velocidade_obstaculo = 5

def criar_obstaculo():
    global next_obstaculo_id
    # posição aleatoria
    altura_aleatoria = random.randint(int(altura_tela * 0.45), int(altura_tela * 0.85))
    gap = int(altura_tela * 0.33)
    obstaculo_baixo = obstaculo_img.get_rect(midtop=(largura_tela + 100, altura_aleatoria))
    obstaculo_cima = obstaculo_img.get_rect(midbottom=(largura_tela + 100, altura_aleatoria - gap))
    # retornamos tuplas (rect, id_unico)
    id_baixo = next_obstaculo_id
    id_cima = next_obstaculo_id + 1
    next_obstaculo_id += 2
    return (obstaculo_baixo, id_baixo), (obstaculo_cima, id_cima)

def mover_obstaculos(obstaculos):
    for rect, oid in obstaculos:
        rect.centerx -= velocidade_obstaculo
    # remove quando completamente fora da tela
    return [(rect, oid) for (rect, oid) in obstaculos if rect.right > -rect.width]

def desenhar_obstaculos(obstaculos):
    for rect, oid in obstaculos:
        if rect.bottom >= altura_tela:
            tela.blit(obstaculo_img, rect)
        else:
            flip_obstaculo = pygame.transform.flip(obstaculo_img, False, True)
            tela.blit(flip_obstaculo, rect)

def checar_colisao(obstaculos):
    for rect, oid in obstaculos:
        if personagem_rect.colliderect(rect):
            return False
    if personagem_rect.top <= -100 or personagem_rect.bottom >= altura_tela:
        return False
    return True

def desenhar_pontuacao(estado_jogo):
    if estado_jogo == 'jogando':
        texto_pontuacao = fonte.render(f'Pontos: {int(pontuacao)}', True, (255, 255, 255))
        pontuacao_rect = texto_pontuacao.get_rect(center=(largura_tela // 2, 50))
        tela.blit(texto_pontuacao, pontuacao_rect)
        # Desenha vidas no canto superior esquerdo
        try:
            texto_vidas = fonte_pequena.render(f'VIDAS: {vidas}', True, (255, 255, 255))
            vidas_rect = texto_vidas.get_rect(topleft=(10, 10))
            tela.blit(texto_vidas, vidas_rect)
        except Exception:
            pass
    elif estado_jogo == 'fim_de_jogo':
        texto_pontuacao = fonte.render(f'Pontos: {int(pontuacao)}', True, (255, 255, 255))
        pontuacao_rect = texto_pontuacao.get_rect(center=(largura_tela // 2, 50))
        tela.blit(texto_pontuacao, pontuacao_rect)

# Variáveis de estado do jogo
jogo_ativo = True
pontuacao = 0
vidas = 3
fonte = pygame.font.Font(None, 50)
fonte_pequena = pygame.font.Font(None, 35)
# removido o uso de obstaculo_index (não confiável). Usamos um set para marcar obstáculos já pontuados.
scored_obstaculos = set()
next_obstaculo_id = 0  # contador único para cada rect criado
nome_jogador = ''
caixa_entrada_ativa = False
caixa_entrada = pygame.Rect(largura_tela // 2 - 100, altura_tela // 2, 200, 50)
cor_ativa = pygame.Color('dodgerblue2')
cor_inativa = pygame.Color('lightskyblue3')
cor = cor_inativa

def tela_placar():
    tela.blit(fundo, (0, 0))
    try:
        with open('placar.txt', 'r') as f:
            placar = [linha.strip().split(':') for linha in f]
            placar = sorted(placar, key=lambda x: int(x[1]), reverse=True)
    except (FileNotFoundError, IndexError):
        placar = []

    texto_titulo = fonte.render('Placar', True, (255, 255, 255))
    titulo_rect = texto_titulo.get_rect(center=(largura_tela // 2, 50))
    tela.blit(texto_titulo, titulo_rect)

    for i, (nome, pontos) in enumerate(placar[:10]):
        texto_placar = fonte_pequena.render(f'{i+1}. {nome}: {pontos}', True, (255, 255, 255))
        placar_rect = texto_placar.get_rect(center=(largura_tela // 2, 100 + i * 40))
        tela.blit(texto_placar, placar_rect)

    texto_instrucao = fonte_pequena.render('Pressione Espaço para iniciar', True, (255, 255, 255))
    instrucao_rect = texto_instrucao.get_rect(center=(largura_tela // 2, altura_tela - 50))
    tela.blit(texto_instrucao, instrucao_rect)
    pygame.display.flip()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                esperando = False

def tela_fim_de_jogo():
    global nome_jogador, caixa_entrada_ativa, cor
    desenhar_pontuacao('fim_de_jogo')
    texto_instrucao = fonte_pequena.render('Digite seu nome e pressione Enter', True, (255, 255, 255))
    instrucao_rect = texto_instrucao.get_rect(center=(largura_tela // 2, altura_tela // 2 - 50))
    tela.blit(texto_instrucao, instrucao_rect)

    # Desenha a caixa de entrada
    pygame.draw.rect(tela, cor, caixa_entrada, 2)
    texto_entrada = fonte.render(nome_jogador, True, (255, 255, 255))
    tela.blit(texto_entrada, (caixa_entrada.x + 5, caixa_entrada.y + 5))
    caixa_entrada.w = max(200, texto_entrada.get_width() + 10)


# Loop principal do jogo
tela_placar()
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not jogo_ativo:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if caixa_entrada.collidepoint(evento.pos):
                    caixa_entrada_ativa = not caixa_entrada_ativa
                else:
                    caixa_entrada_ativa = False
                cor = cor_ativa if caixa_entrada_ativa else cor_inativa
            if evento.type == pygame.KEYDOWN:
                if caixa_entrada_ativa:
                    if evento.key == pygame.K_RETURN:
                        with open('placar.txt', 'a') as f:
                            f.write(f'{nome_jogador}:{int(pontuacao)}\n')
                        nome_jogador = ''
                        jogo_ativo = False # Para ir para a tela de placar
                        tela_placar()
                        # Resetar o estado do jogo para a próxima rodada
                        lista_obstaculos.clear()
                        scored_obstaculos.clear()
                        next_obstaculo_id = 0
                        personagem_rect.center = (largura_tela // 4, altura_tela // 2)
                        velocidade_y = 0
                        pontuacao = 0
                        jogo_ativo = True # Começa o jogo novamente
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    else:
                        nome_jogador += evento.unicode
        else:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    velocidade_y = pulo
            if evento.type == SPAWNOBSTACLE:
                lista_obstaculos.extend(criar_obstaculo())

    # Desenha o fundo
    tela.blit(fundo, (0, 0))

    if jogo_ativo:
        # Lógica do jogador
        velocidade_y += gravidade
        personagem_rect.y += int(velocidade_y)

        # Checa colisão manualmente para implementar sistema de vidas
        colidiu = False
        for rect, oid in lista_obstaculos:
            if personagem_rect.colliderect(rect):
                colidiu = True
                break
        if personagem_rect.top <= -100 or personagem_rect.bottom >= altura_tela:
            colidiu = True

        if colidiu:
            vidas -= 1
            # Se ainda tiver vidas, reseta a posição e obstáculos mas mantém a pontuação
            if vidas > 0:
                personagem_rect.center = (largura_tela // 4, altura_tela // 2)
                velocidade_y = 0
                lista_obstaculos.clear()
                scored_obstaculos.clear()
                next_obstaculo_id = 0
                # dá um pequeno delay para o jogador se preparar (opcional)
                pygame.time.delay(300)
            else:
                # sem vidas -> fim de jogo
                jogo_ativo = False

        # Lógica dos obstáculos
        lista_obstaculos = mover_obstaculos(lista_obstaculos)
        desenhar_obstaculos(lista_obstaculos)

        # Lógica da pontuação: conta apenas o obstáculo "inferior" (bottom >= altura_tela)
        for rect, oid in lista_obstaculos:
            if rect.bottom >= altura_tela and rect.centerx < personagem_rect.left:
                if oid not in scored_obstaculos:
                    pontuacao += 1
                    scored_obstaculos.add(oid)

        desenhar_pontuacao('jogando')
    else:
        tela_fim_de_jogo()

    # Desenha o personagem
    if jogo_ativo:
        tela.blit(personagem, personagem_rect)

    # Atualiza a tela
    pygame.display.flip()

    # Controla a taxa de quadros
    relogio.tick(60)
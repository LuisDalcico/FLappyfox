#arquivo do jogo
import pygame
import sys
import random
# Inicializando o Pygame
pygame.init()
pygame.mixer.init()

# Carregando sons
som_pulo = pygame.mixer.Sound('pulo.mp3')
som_colisao = pygame.mixer.Sound('tronco.mp3')
try:
    som_coracao = pygame.mixer.Sound('somcoracao.mp3')
except Exception:
    som_coracao = None
musica_fundo = 'musica fundo.mp3'
pygame.mixer.music.load(musica_fundo)
pygame.mixer.music.play(-1)


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

# imagens para o menu e instruções
fundo_menu = pygame.image.load('fundo2.jpg')
fundo_menu = pygame.transform.scale(fundo_menu, (largura_tela, altura_tela))
titulo = pygame.image.load('titulo.png')
titulo = pygame.transform.scale(titulo, (int(titulo.get_width() * 7.5), int(titulo.get_height() * 7.5)))
botao_jogar = pygame.image.load('botaoplay-removebg-preview.png')
botao_jogar = pygame.transform.scale(botao_jogar, (int(botao_jogar.get_width() * 0.9), int(botao_jogar.get_height() * 0.9)))
botao_instrucoes = pygame.image.load('botaoinstrucoes-removebg-preview.png')
botao_instrucoes = pygame.transform.scale(botao_instrucoes, (int(botao_instrucoes.get_width() * 0.9), int(botao_instrucoes.get_height() * 0.9)))
# Coração (power-up de vida)
coracao = pygame.image.load('coracao.png')
# ajustar o tamanho do coração para ficar um pouco menor que o personagem
pw2, ph2 = personagem.get_size()
coracao = pygame.transform.scale(coracao, (int(pw2 * 0.8), int(ph2 * 0.8)))
tela_instrucoes_img = pygame.image.load('Telainstrucao.png')
tela_instrucoes_img = pygame.transform.scale(tela_instrucoes_img, (largura_tela, altura_tela))

# Posição e velocidade 
personagem_rect = personagem.get_rect(center=(largura_tela // 4, altura_tela // 2))
velocidade_y = 0
gravidade = 0.5
pulo = -10

# Obstaculos
lista_obstaculos = []
SPAWNOBSTACLE = pygame.USEREVENT
SPAWNHEART = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNOBSTACLE, 1200)
# tenta spawnear um coração a cada 10s (checa condição interna)
pygame.time.set_timer(SPAWNHEART, 10000)
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
            som_colisao.play()
            return False
    if personagem_rect.top <= -100 or personagem_rect.bottom >= altura_tela:
        som_colisao.play()
        return False
    return True

def desenhar_pontuacao(estado_jogo):
    if estado_jogo == 'jogando':
        texto_pontuacao = fonte.render(f'Pontos: {int(pontuacao)}', True, (255, 255, 255))
        pontuacao_rect = texto_pontuacao.get_rect(center=(largura_tela // 2, 50))
        tela.blit(texto_pontuacao, pontuacao_rect)
    elif estado_jogo == 'fim_de_jogo':
        texto_pontuacao = fonte.render(f'Pontos: {int(pontuacao)}', True, (255, 255, 255))
        pontuacao_rect = texto_pontuacao.get_rect(center=(largura_tela // 2, 50))
        tela.blit(texto_pontuacao, pontuacao_rect)

def desenhar_vidas():
    texto_vidas = fonte_pequena.render(f'VIDAS: {vidas}', True, (255, 0, 0))
    tela.blit(texto_vidas, (10, 10))

def desenhar_pausa():
    texto_pausa = fonte.render('Pressione Espaço para continuar', True, (255, 255, 255))
    pausa_rect = texto_pausa.get_rect(center=(largura_tela // 2, altura_tela // 2 + 100))
    tela.blit(texto_pausa, pausa_rect)

# Variáveis de estado do jogo
jogo_ativo = True
pontuacao = 0
vidas = 3
pausa = False
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
# Estado do coração (power-up)
heart_active = False
heart_rect = None

def desenhar_placar():
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

    texto_instrucao = fonte_pequena.render('Pressione Espaço para voltar ao menu', True, (255, 255, 255))
    instrucao_rect = texto_instrucao.get_rect(center=(largura_tela // 2, altura_tela - 50))
    tela.blit(texto_instrucao, instrucao_rect)

def desenhar_fim_de_jogo():
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

def desenhar_menu():
    tela.blit(fundo_menu, (0, 0))
    titulo_rect = titulo.get_rect(center=(largura_tela // 2, altura_tela // 4))
    tela.blit(titulo, titulo_rect)
    botao_jogar_rect = botao_jogar.get_rect(center=(largura_tela // 2, altura_tela * 0.58))
    botao_instrucoes_rect = botao_instrucoes.get_rect(center=(largura_tela // 2, altura_tela * 0.85))
    tela.blit(botao_jogar, botao_jogar_rect)
    tela.blit(botao_instrucoes, botao_instrucoes_rect)
    return botao_jogar_rect, botao_instrucoes_rect

def desenhar_instrucoes():
    tela.blit(tela_instrucoes_img, (0, 0))
    # Botão de voltar
    texto_voltar = fonte_pequena.render('Pressione ESC para voltar', True, (255, 255, 255))
    voltar_rect = texto_voltar.get_rect(center=(largura_tela // 2, altura_tela - 50))
    pygame.draw.rect(tela, (0, 0, 0), (voltar_rect.x - 10, voltar_rect.y - 10, voltar_rect.width + 20, voltar_rect.height + 20))
    tela.blit(texto_voltar, voltar_rect)

# Game state setup
game_state = 'menu'
botao_jogar_rect, botao_instrucoes_rect = None, None

# Loop principal do jogo
while True:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Manipulação de eventos por estado
        if game_state == 'menu':
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar_rect and botao_jogar_rect.collidepoint(evento.pos):
                    lista_obstaculos.clear()
                    scored_obstaculos.clear()
                    next_obstaculo_id = 0
                    personagem_rect.center = (largura_tela // 4, altura_tela // 2)
                    velocidade_y = 0
                    pontuacao = 0
                    vidas = 3
                    pausa = True
                    game_state = 'jogando'
                elif botao_instrucoes_rect and botao_instrucoes_rect.collidepoint(evento.pos):
                    game_state = 'instrucoes'
        
        elif game_state == 'instrucoes':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                game_state = 'menu'

        elif game_state == 'jogando':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                if not pausa:
                    velocidade_y = pulo
                    som_pulo.play()
                else:
                    pausa = False
            if evento.type == SPAWNOBSTACLE:
                lista_obstaculos.extend(criar_obstaculo())
            # só spawna coração se tiver 2 ou menos vidas e não houver coração ativo
            if evento.type == SPAWNHEART and not heart_active and vidas <= 2:
                # spawn do coração na frente (direita) do personagem, vindo da borda direita
                hx = largura_tela + 100
                hy = random.randint(80, altura_tela - 80)
                heart_rect = coracao.get_rect(midleft=(hx, hy))
                heart_active = True

        elif game_state == 'fim_de_jogo':
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
                        game_state = 'placar'
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    else:
                        nome_jogador += evento.unicode

        elif game_state == 'placar':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                game_state = 'menu'

    # Lógica e renderização por estado
    if game_state == 'menu':
        botao_jogar_rect, botao_instrucoes_rect = desenhar_menu()

    elif game_state == 'instrucoes':
        desenhar_instrucoes()

    elif game_state == 'jogando':
        tela.blit(fundo, (0, 0))
        
        if not pausa:
            velocidade_y += gravidade
            personagem_rect.y += int(velocidade_y)
            
            if not checar_colisao(lista_obstaculos):
                vidas -= 1
                if vidas > 0:
                    # Volta ao início mas mantém a pontuação
                    lista_obstaculos.clear()
                    scored_obstaculos.clear()
                    next_obstaculo_id = 0
                    personagem_rect.center = (largura_tela // 4, altura_tela // 2)
                    velocidade_y = 0
                    pausa = True
                else:
                    # Jogo termina
                    game_state = 'fim_de_jogo'
                    caixa_entrada_ativa = False
                    cor = cor_inativa
            
            lista_obstaculos = mover_obstaculos(lista_obstaculos)
            # Move heart junto com os obstáculos quando ativo
            if heart_active and heart_rect is not None:
                heart_rect.centerx -= int(velocidade_obstaculo)
                # remove se saiu da tela
                if heart_rect.right < 0:
                    heart_active = False
                    heart_rect = None
        
        desenhar_obstaculos(lista_obstaculos)

        # Desenha power-up de vida (coração) e checa colisão
        if heart_active and heart_rect is not None:
            tela.blit(coracao, heart_rect)
            if not pausa and personagem_rect.colliderect(heart_rect):
                # aumenta vida mas limita a 3
                vidas = min(vidas + 1, 3)
                # toca som de coleta se disponível
                if som_coracao:
                    try:
                        som_coracao.play()
                    except Exception:
                        pass
                heart_active = False
                heart_rect = None

        if not pausa:
            for rect, oid in lista_obstaculos:
                if rect.bottom >= altura_tela and rect.centerx < personagem_rect.left:
                    if oid not in scored_obstaculos:
                        pontuacao += 1
                        scored_obstaculos.add(oid)
                        # Aumenta velocidade a cada 15 pontos
                        if int(pontuacao) % 15 == 0:
                            velocidade_obstaculo += 1

        desenhar_pontuacao('jogando')
        desenhar_vidas()
        tela.blit(personagem, personagem_rect)
        
        if pausa:
            desenhar_pausa()

    elif game_state == 'fim_de_jogo':
        tela.blit(fundo, (0, 0))
        desenhar_obstaculos(lista_obstaculos)
        tela.blit(personagem, personagem_rect)
        desenhar_fim_de_jogo()

    elif game_state == 'placar':
        desenhar_placar()

    # Atualiza a tela
    pygame.display.flip()
    relogio.tick(60)
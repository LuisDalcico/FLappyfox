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

# Relógio do jogo
relogio = pygame.time.Clock()

# Carregando imagens e fundo
personagem = pygame.image.load('personagem.jpg')
# aumentar o personagem 3x
pw, ph = personagem.get_size()
personagem = pygame.transform.scale(personagem, (pw * 3, ph * 3))

obstaculo_img = pygame.image.load('obstaculo.jpg')
# diminui o obstaculo pela metade
obstaculo_img = pygame.transform.scale(obstaculo_img, (60, int(altura_tela * 0.75)))

# vi que era melhor usar try. deixa assim klein; Carrega a imagem de fundo
try:
    fundo = pygame.image.load('fundo.jpg')
    fundo = pygame.transform.scale(fundo, (largura_tela, altura_tela))
except Exception:
    fundo = pygame.Surface((largura_tela, altura_tela))
    fundo.fill((0, 150, 255))  # cor azul 

# Posição e velocidade do personagem
personagem_rect = personagem.get_rect(center=(largura_tela // 4, altura_tela // 2))
velocidade_y = 0
gravidade = 0.5
pulo = -10

# Obstáculos
lista_obstaculos = []
SPAWNOBSTACLE = pygame.USEREVENT
pygame.time.set_timer(SPAWNOBSTACLE, 1200)
velocidade_obstaculo = 5
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

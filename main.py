import pygame
import random
import sys

# ============================================================
#   CONFIGURACOES DO JOGO  (mude aqui para personalizar!)
# ============================================================
LARGURA = 400
ALTURA = 600
FPS = 60

# --- Dificuldade ---
GRAVIDADE = 0.5           # o quanto o passaro cai a cada quadro
FORCA_PULO = -8           # impulso para cima ao apertar ESPACO (negativo = sobe)
VELOCIDADE_CANO = 3       # velocidade com que os canos andam para a esquerda
ABERTURA_CANO = 170       # tamanho do "buraco" entre o cano de cima e o de baixo
INTERVALO_CANO = 90       # a cada quantos quadros nasce um novo cano (90 = ~1,5s)
PONTOS_PARA_VENCER = 10   # quantos canos passar para ganhar o jogo

# --- Cores (R, G, B) ---
COR_CEU = (112, 197, 206)
COR_CANO = (76, 187, 23)
COR_CANO_BORDA = (45, 120, 15)
COR_CHAO = (222, 184, 135)
COR_PASSARO = (255, 221, 0)
COR_TEXTO = (255, 255, 255)
COR_TEXTO_ESCURO = (40, 40, 40)

LARGURA_CANO = 60
ALTURA_CHAO = 80
CHAO_Y = ALTURA - ALTURA_CHAO     # altura onde o chao comeca
RAIO_PASSARO = 18

# ============================================================
#   INICIALIZACAO DO PYGAME
# ============================================================
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Flappy Bird - Demo LPA")
relogio = pygame.time.Clock()

fonte_grande = pygame.font.SysFont(None, 60)
fonte_media = pygame.font.SysFont(None, 40)
fonte_pequena = pygame.font.SysFont(None, 26)


# ============================================================
#   FUNCOES AUXILIARES DE DESENHO
# ============================================================
def desenhar_texto(texto, fonte, cor, centro_x, centro_y):
    """Desenha um texto centralizado na posicao (centro_x, centro_y)."""
    superficie = fonte.render(texto, True, cor)
    retangulo = superficie.get_rect(center=(centro_x, centro_y))
    tela.blit(superficie, retangulo)


def desenhar_passaro(x, y):
    """Desenha o passaro: corpo (circulo), olho e bico."""
    pygame.draw.circle(tela, COR_PASSARO, (int(x), int(y)), RAIO_PASSARO)
    pygame.draw.circle(tela, (40, 40, 40), (int(x) + 6, int(y) - 5), 4)   # olho
    pygame.draw.polygon(tela, (255, 140, 0), [                            # bico
        (int(x) + 14, int(y)),
        (int(x) + 28, int(y) - 4),
        (int(x) + 28, int(y) + 4),
    ])


def desenhar_chao():
    pygame.draw.rect(tela, COR_CHAO, (0, CHAO_Y, LARGURA, ALTURA_CHAO))


def novo_cano():
    """Cria um par de canos (cima + baixo) com um buraco em posicao aleatoria."""
    margem = 60
    centro_buraco = random.randint(margem + ABERTURA_CANO // 2,
                                   CHAO_Y - margem - ABERTURA_CANO // 2)
    return {
        "x": LARGURA,                              # comeca fora da tela, na direita
        "topo": centro_buraco - ABERTURA_CANO // 2,  # onde TERMINA o cano de cima
        "base": centro_buraco + ABERTURA_CANO // 2,  # onde COMECA o cano de baixo
        "pontuado": False,                          # se ja contou ponto ao passar
    }


def desenhar_cano(cano):
    # cano de cima
    pygame.draw.rect(tela, COR_CANO, (cano["x"], 0, LARGURA_CANO, cano["topo"]))
    pygame.draw.rect(tela, COR_CANO_BORDA, (cano["x"], 0, LARGURA_CANO, cano["topo"]), 3)
    # cano de baixo
    altura_baixo = CHAO_Y - cano["base"]
    pygame.draw.rect(tela, COR_CANO, (cano["x"], cano["base"], LARGURA_CANO, altura_baixo))
    pygame.draw.rect(tela, COR_CANO_BORDA, (cano["x"], cano["base"], LARGURA_CANO, altura_baixo), 3)


# ============================================================
#   TELA DE MENU  (mostra os comandos - exigencia do trabalho!)
# ============================================================
def tela_inicial():
    """Mostra o menu. Retorna 'jogar' ou 'sair'."""
    while True:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "jogar"
                if evento.key == pygame.K_ESCAPE:
                    return "sair"

        tela.fill(COR_CEU)
        desenhar_chao()
        desenhar_passaro(LARGURA // 2, 120)
        desenhar_texto("FLAPPY BIRD", fonte_grande, COR_TEXTO_ESCURO, LARGURA // 2, 185)
        desenhar_texto("Demo - LPA", fonte_pequena, COR_TEXTO_ESCURO, LARGURA // 2, 222)

        # ----- COMANDOS DE CONTROLE (precisam aparecer no menu) -----
        desenhar_texto("ESPACO  -  Voar", fonte_media, COR_TEXTO, LARGURA // 2, 320)
        desenhar_texto("ENTER  -  Comecar", fonte_media, COR_TEXTO, LARGURA // 2, 362)
        desenhar_texto("ESC  -  Sair", fonte_media, COR_TEXTO, LARGURA // 2, 404)

        desenhar_texto("Passe por " + str(PONTOS_PARA_VENCER) + " canos para vencer!",
                       fonte_pequena, COR_TEXTO_ESCURO, LARGURA // 2, 470)
        pygame.display.flip()


# ============================================================
#   PARTIDA  (o jogo em si)
# ============================================================
def jogar():
    """Roda uma partida. Retorna (resultado, pontos).
    resultado pode ser: 'vitoria', 'derrota', 'menu' ou 'sair'."""
    passaro_y = ALTURA // 2
    passaro_x = 80
    velocidade_y = 0
    canos = []
    contador = 0
    pontos = 0

    while True:
        relogio.tick(FPS)

        # ---------- EVENTOS / CONTROLE ----------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair", 0
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    velocidade_y = FORCA_PULO          # PULO / voar
                if evento.key == pygame.K_ESCAPE:
                    return "menu", 0

        # ---------- FISICA DO PASSARO ----------
        velocidade_y += GRAVIDADE
        passaro_y += velocidade_y
        if passaro_y < RAIO_PASSARO:                   # trava no teto
            passaro_y = RAIO_PASSARO
            velocidade_y = 0

        # ---------- CRIAR / MOVER CANOS ----------
        contador += 1
        if contador >= INTERVALO_CANO:
            contador = 0
            canos.append(novo_cano())

        for cano in canos:
            cano["x"] -= VELOCIDADE_CANO
        canos = [c for c in canos if c["x"] > -LARGURA_CANO]   # remove os que sairam

        # ---------- COLISAO E PONTUACAO ----------
        passaro_rect = pygame.Rect(passaro_x - 14, passaro_y - 14, 28, 28)

        for cano in canos:
            rect_cima = pygame.Rect(cano["x"], 0, LARGURA_CANO, cano["topo"])
            rect_baixo = pygame.Rect(cano["x"], cano["base"], LARGURA_CANO, CHAO_Y - cano["base"])

            # bateu num cano -> DERROTA
            if passaro_rect.colliderect(rect_cima) or passaro_rect.colliderect(rect_baixo):
                return "derrota", pontos

            # passou pelo cano -> +1 ponto
            if not cano["pontuado"] and cano["x"] + LARGURA_CANO < passaro_x:
                cano["pontuado"] = True
                pontos += 1
                if pontos >= PONTOS_PARA_VENCER:        # atingiu a meta -> VITORIA
                    return "vitoria", pontos

        # bateu no chao -> DERROTA
        if passaro_y + RAIO_PASSARO >= CHAO_Y:
            return "derrota", pontos

        # ---------- DESENHO ----------
        tela.fill(COR_CEU)
        for cano in canos:
            desenhar_cano(cano)
        desenhar_chao()
        desenhar_passaro(passaro_x, passaro_y)
        desenhar_texto(str(pontos), fonte_grande, COR_TEXTO, LARGURA // 2, 60)
        pygame.display.flip()


# ============================================================
#   TELA DE FIM  (vitoria ou derrota)
# ============================================================
def tela_fim(venceu, pontos):
    """Mostra o resultado. Retorna 'jogar', 'menu' ou 'sair'."""
    while True:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "jogar"
                if evento.key == pygame.K_ESCAPE:
                    return "menu"

        tela.fill(COR_CEU)
        desenhar_chao()
        if venceu:
            desenhar_texto("VOCE VENCEU!", fonte_grande, (255, 215, 0), LARGURA // 2, 200)
        else:
            desenhar_texto("GAME OVER", fonte_grande, (200, 40, 40), LARGURA // 2, 200)
        desenhar_texto("Pontos: " + str(pontos), fonte_media, COR_TEXTO_ESCURO, LARGURA // 2, 270)
        desenhar_texto("ENTER  -  Jogar de novo", fonte_pequena, COR_TEXTO_ESCURO, LARGURA // 2, 360)
        desenhar_texto("ESC  -  Menu", fonte_pequena, COR_TEXTO_ESCURO, LARGURA // 2, 395)
        pygame.display.flip()


# ============================================================
#   CONTROLE PRINCIPAL (liga menu -> jogo -> fim)
# ============================================================
def main():
    estado = "menu"
    venceu = False
    pontos = 0

    while True:
        if estado == "menu":
            if tela_inicial() == "sair":
                break
            estado = "jogando"

        elif estado == "jogando":
            resultado, pontos = jogar()
            if resultado == "sair":
                break
            elif resultado == "menu":
                estado = "menu"
            else:
                venceu = (resultado == "vitoria")
                estado = "fim"

        elif estado == "fim":
            escolha = tela_fim(venceu, pontos)
            if escolha == "sair":
                break
            elif escolha == "menu":
                estado = "menu"
            else:
                estado = "jogando"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

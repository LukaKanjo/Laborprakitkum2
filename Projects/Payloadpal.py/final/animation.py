import pygame
import sys
# SCHEIße, ich mach selber noch!!!!!
def animate_flight(flight_data, max_height):
    pygame.init()

    width, height = 400, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Rocket Flight")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)

    # Farbcodes
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    BLACK = (0, 0, 0)

    # Hauptloop
    running = True
    i = 0

    while running:
        clock.tick(30)  # FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        screen.fill(BLACK)

        # Aktueller Datenpunkt
        if i < len(flight_data):
            data = flight_data[i]
            h = data["h"]
            v = data["v"]
            t = data["t"]

            # Höhe auf Bildschirmhöhe skalieren (umdrehen wegen y↓)
            rocket_y = height - int((h / max_height) * (height - 100))
            pygame.draw.rect(screen, WHITE, (width // 2 - 10, rocket_y, 20, 60))

            # Flamme bei Schub
            if data["a"] > 0:
                pygame.draw.polygon(screen, RED, [(width // 2, rocket_y + 60), (width // 2 - 10, rocket_y + 80), (width // 2 + 10, rocket_y + 80)])

            # Textanzeige
            info = f"t = {t:.1f}s, h = {h:.0f} m, v = {v:.0f} m/s"
            text = font.render(info, True, WHITE)
            screen.blit(text, (10, 10))

            i += 1
        else:
            text = font.render("Simulation complete", True, WHITE)
            screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()
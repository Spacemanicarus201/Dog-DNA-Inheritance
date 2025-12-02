import pygame
from screens.main_menu import MainMenu

class App:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 800
        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Dog DNA Inheritance")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = MainMenu(self)
        self.time_delta = 0  # <- initialize

    def run(self):
        while self.running:
            # Calculate frame time delta
            self.time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Update new window size
                    self.WIDTH, self.HEIGHT = event.w, event.h
                    self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                    self.current_screen.resize(self.WIDTH, self.HEIGHT)
                else:
                    self.current_screen.handle_event(event)

            self.current_screen.draw(self.SCREEN)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    app = App()
    app.run()

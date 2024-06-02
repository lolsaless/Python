import pygame
import random

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 300
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')

# 색상 정의
black = (0, 0, 0)
white = (255, 255, 255)
colors = [
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0)
]

# 테트리스 블록 모양 정의
shapes = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 0], [1, 1, 1]]
]

class Tetris:
    def __init__(self, screen):
        self.screen = screen
        self.board = [[0] * 10 for _ in range(20)]
        self.current_piece = self.new_piece()
        self.piece_x = 3
        self.piece_y = 0
        self.game_over = False

    def new_piece(self):
        return random.choice(shapes), random.choice(colors)

    def rotate(self):
        shape, color = self.current_piece
        new_shape = [list(row) for row in zip(*shape[::-1])]
        if self.can_move(new_shape, 0, 0):
            self.current_piece = new_shape, color

    def can_move(self, shape, dx, dy):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.piece_x + x + dx
                    new_y = self.piece_y + y + dy
                    if new_x < 0 or new_x >= 10 or new_y >= 20 or (new_y >= 0 and self.board[new_y][new_x]):
                        return False
        return True

    def freeze(self):
        shape, color = self.current_piece
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.piece_y + y][self.piece_x + x] = color
        self.clear_lines()
        self.current_piece = self.new_piece()
        self.piece_x = 3
        self.piece_y = 0
        if not self.can_move(self.current_piece[0], 0, 0):
            self.game_over = True

    def clear_lines(self):
        self.board = [row for row in self.board if any(cell == 0 for cell in row)]
        while len(self.board) < 20:
            self.board.insert(0, [0] * 10)

    def move(self, dx, dy):
        shape, color = self.current_piece
        if self.can_move(shape, dx, dy):
            self.piece_x += dx
            self.piece_y += dy
        elif dy:
            self.freeze()

    def draw(self):
        self.screen.fill(black)
        shape, color = self.current_piece
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, color, pygame.Rect((self.piece_x + x) * 30, (self.piece_y + y) * 30, 30, 30))
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell, pygame.Rect(x * 30, y * 30, 30, 30))
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Tetris(screen)
    running = True
    drop_counter = 0
    drop_speed = 30  # 속도를 느리게 하여 블록이 떨어지는 속도를 조절합니다.
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move(0, 1)
                elif event.key == pygame.K_UP:
                    game.rotate()
        drop_counter += 1
        if drop_counter >= drop_speed:
            game.move(0, 1)
            drop_counter = 0
        if not game.game_over:
            game.draw()
        clock.tick(30)  # 게임의 프레임 속도 조절

    pygame.quit()

if __name__ == '__main__':
    main()

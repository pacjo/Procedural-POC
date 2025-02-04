from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QSizePolicy, QPushButton, QVBoxLayout
from random import choice
import sys

CELL_SIZE = 35


class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.visited = False
        self.is_wall = True
        self.is_start = False
        self.is_end = False


class MazeGenerator(QWidget):
    def __init__(self, rows: int, cols: int):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.grid = []
        self.cell_widgets = {}
        self.start_pos = None
        self.end_pos = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.maze_layout = QGridLayout()
        self.maze_layout.setSpacing(0)
        main_layout.addLayout(self.maze_layout)

        generate_button = QPushButton("Generuj nowy labirynt")
        generate_button.clicked.connect(self.generate_maze)
        main_layout.addWidget(generate_button)

        self.initialize_grid()

        self.setWindowTitle('Generator Labiryntów')
        self.show()

        self.generate_maze()

    def initialize_grid(self):
        self.grid = [[Cell(row, col) for col in range(self.cols)] for row in range(self.rows)]

        for row in range(self.rows):
            for col in range(self.cols):
                label = QLabel()
                label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")
                label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                label.setFixedSize(QSize(CELL_SIZE, CELL_SIZE))
                self.maze_layout.addWidget(label, row, col)
                self.cell_widgets[(row, col)] = label

    def find_valid_start_end_positions(self):
        # Lista wszystkich dostępnych pozycji (nie-ścian)
        available_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.grid[row][col].is_wall:
                    available_positions.append((row, col))

        # Wybierz losową pozycję startową i końcową
        self.start_pos = choice(available_positions)
        # Usuń pozycję startową z dostępnych pozycji
        available_positions.remove(self.start_pos)
        # Wybierz pozycję końcową z pozostałych pozycji
        self.end_pos = choice(available_positions)

        # Ustaw flagi w komórkach
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos
        self.grid[start_row][start_col].is_start = True
        self.grid[end_row][end_col].is_end = True

    def generate_maze(self):
        # Reset gridu
        for row in self.grid:
            for cell in row:
                cell.visited = False
                cell.is_wall = True
                cell.is_start = False
                cell.is_end = False

        # Reset kolorów
        for label in self.cell_widgets.values():
            label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")

        # Rozpocznij od środka
        start_row = self.rows // 2
        start_col = self.cols // 2
        self.grid[start_row][start_col].is_wall = False
        self.dfs(start_row, start_col)

        # Znajdź i ustaw punkty startowy i końcowy
        self.find_valid_start_end_positions()

        # Aktualizuj widok
        self.update_maze_view()

    def dfs(self, row: int, col: int):
        self.grid[row][col].visited = True
        self.grid[row][col].is_wall = False

        # Lista możliwych kierunków (góra, prawo, dół, lewo)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while directions:
            dx, dy = choice(directions)
            directions.remove((dx, dy))

            new_row = row + (dx * 2)
            new_col = col + (dy * 2)

            if (0 <= new_row < self.rows and
                    0 <= new_col < self.cols and
                    not self.grid[new_row][new_col].visited):
                self.grid[row + dx][col + dy].is_wall = False
                self.dfs(new_row, new_col)

    def update_maze_view(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                label = self.cell_widgets[(row, col)]

                if cell.is_start:
                    label.setStyleSheet("background-color: #2ecc71; border: 1px solid #34495e;")  # Zielony
                elif cell.is_end:
                    label.setStyleSheet("background-color: #e74c3c; border: 1px solid #34495e;")  # Czerwony
                elif cell.is_wall:
                    label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")  # Ciemnoniebieski
                else:
                    label.setStyleSheet("background-color: white; border: 1px solid #34495e;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MazeGenerator(21, 31)
    sys.exit(app.exec())
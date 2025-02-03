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
        self.is_wall = True  # Domyślnie każda komórka jest ścianą


class MazeGenerator(QWidget):
    def __init__(self, rows: int, cols: int):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.grid = []
        self.cell_widgets = {}  # Słownik do przechowywania widgetów
        self.initUI()

    def initUI(self):
        # Główny layout pionowy
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Grid dla labiryntu
        self.maze_layout = QGridLayout()
        self.maze_layout.setSpacing(0)
        main_layout.addLayout(self.maze_layout)

        # Przycisk do generowania nowego labiryntu
        generate_button = QPushButton("Generuj nowy labirynt")
        generate_button.clicked.connect(self.generate_maze)
        main_layout.addWidget(generate_button)

        # Inicjalizacja gridu
        self.initialize_grid()

        # Konfiguracja okna
        self.setWindowTitle('Generator Labiryntów')
        self.show()

        # Generuj pierwszy labirynt
        self.generate_maze()

    def initialize_grid(self):
        # Tworzenie komórek
        self.grid = [[Cell(row, col) for col in range(self.cols)] for row in range(self.rows)]

        # Tworzenie widgetów dla komórek
        for row in range(self.rows):
            for col in range(self.cols):
                label = QLabel()
                label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")
                label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                label.setFixedSize(QSize(CELL_SIZE, CELL_SIZE))
                self.maze_layout.addWidget(label, row, col)
                self.cell_widgets[(row, col)] = label

    def generate_maze(self):
        # Reset gridu
        for row in self.grid:
            for cell in row:
                cell.visited = False
                cell.is_wall = True

        # Reset kolorów
        for label in self.cell_widgets.values():
            label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")

        # Rozpocznij od środka
        start_row = self.rows // 2
        start_col = self.cols // 2
        self.grid[start_row][start_col].is_wall = False
        self.dfs(start_row, start_col)

        # Aktualizuj widok
        self.update_maze_view()

    def dfs(self, row: int, col: int):
        self.grid[row][col].visited = True
        self.grid[row][col].is_wall = False

        # Lista możliwych kierunków (góra, prawo, dół, lewo)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # Losowo wybierz kolejność kierunków
        while directions:
            dx, dy = choice(directions)
            directions.remove((dx, dy))

            # Sprawdź sąsiada dwa kroki dalej (żeby zostawić miejsce na ścianę)
            new_row = row + (dx * 2)
            new_col = col + (dy * 2)

            if (0 <= new_row < self.rows and
                    0 <= new_col < self.cols and
                    not self.grid[new_row][new_col].visited):
                # Usuń ścianę między aktualną komórką a nową
                self.grid[row + dx][col + dy].is_wall = False
                self.dfs(new_row, new_col)

    def update_maze_view(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                label = self.cell_widgets[(row, col)]

                if cell.is_wall:
                    label.setStyleSheet("background-color: #2c3e50; border: 1px solid #34495e;")
                else:
                    label.setStyleSheet("background-color: white; border: 1px solid #34495e;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Użyj parzystych wymiarów dla lepszego efektu
    ex = MazeGenerator(21, 31)
    sys.exit(app.exec())
from copy import deepcopy

from sty import bg


class Sudoku:
    def __init__(
            self,
            sudoku_matrix: str,
            possible_values: list,
            subsquare_width: int,
            subsquare_height: int = None,
    ):
        self.simplifier_representation = False
        self.grid = []
        self.subsquare_width = subsquare_width
        self.subsquare_height = subsquare_height if subsquare_height else subsquare_width
        self.possible_values = possible_values
        self.square_size = self.subsquare_height * self.subsquare_width
        if len(possible_values) != self.subsquare_width * self.subsquare_height:
            raise IndexError(
                f"Possible values {possible_values} length {len(possible_values)} should equal {self.square_size=}"
            )
        for row in sudoku_matrix.split("\n"):
            self.grid.append(
                [
                    symbol if symbol and symbol != " " else possible_values.copy()
                    for symbol in row
                ]
            )
        column_len_difference = len(self.grid) - len(possible_values)
        if column_len_difference > 0:
            self.grid = self.grid[: len(possible_values)]
        for row_counter, row in enumerate(self.grid):
            row_len_difference = len(row) - len(possible_values)
            if row_len_difference > 0:
                self.grid[row_counter] = self.grid[row_counter][: len(possible_values)]
            if row_len_difference < 0:
                for counter in range(-row_len_difference):
                    row.append(possible_values.copy())
        if column_len_difference < 0:
            for counter in range(-column_len_difference):
                self.grid.append(
                    list([possible_values.copy() for i in range(len(possible_values))])
                )

    def simplify_representation(self)->None:
        self.simplifier_representation = True

    def create_possible_branches(self)->list["Sudoku"]:
        minimal_cell_row = -1
        minimal_cell_column = -1
        minimal_length = 10
        for row_counter, row in enumerate(self.grid):
            for column_counter, cell in enumerate(row):
                if isinstance(cell, list):
                    if len(cell) < minimal_length:
                        minimal_cell_column = column_counter
                        minimal_cell_row = row_counter
                        minimal_length = len(cell)
        result = []
        cell_value = self.grid[minimal_cell_row][minimal_cell_column]
        for counter in range(minimal_length):
            proposed_decision = deepcopy(self)
            proposed_decision.grid[minimal_cell_row][minimal_cell_column] = cell_value[
                counter
            ]
            result.append(proposed_decision)
        return result

    def remove_value_from_cell(self, value, row:int, column:int)->None:
        if isinstance(value, str):
            if value in self.grid[row][column]:
                self.grid[row][column].remove(value)

    def filter_column(self, row_number:int, column:int)->None:
        for row in self.grid:
            value = row[column]
            self.remove_value_from_cell(value, row_number, column)

    def filter_row(self, row:int, column:int)->None:
        for value in self.grid[row]:
            self.remove_value_from_cell(value, row, column)

    def filter_subsquare(self, row:int, column:int):
        # subsquare_size = int(len(self.possible_values) / self.number_of_subsquares)
        start_row_number = self.subsquare_height* (row // self.subsquare_height)
        start_column_number = self.subsquare_width* (column // self.subsquare_width)
        for row_counter in range(start_row_number, start_row_number + self.subsquare_height):
            for column_counter in range(
                    start_column_number, start_column_number + self.subsquare_width
            ):
                value = self.grid[row_counter][column_counter]
                self.remove_value_from_cell(value, row, column)

    def calculate_all_possible_values(self)->None:
        for row in range(len(self.possible_values)):
            for column in range(len(self.possible_values)):
                cell_value = self.grid[row][column]
                if isinstance(cell_value, list):
                    self.filter_column(row, column)
                    self.filter_row(row, column)
                    self.filter_subsquare(row, column)

    def replace_options_by_values(self)->int:
        number_of_replaced_items = 0
        for row_counter, row in enumerate(self.grid):
            for cell_counter, cell in enumerate(row):
                if not cell:
                    raise ValueError(
                        f"Invalid value in grid {cell} in {row_counter}, {cell_counter}"
                    )
                if isinstance(cell, list) and len(cell) == 1:
                    self.grid[row_counter][cell_counter] = cell[0]
                    number_of_replaced_items += 1
        return number_of_replaced_items

    @staticmethod
    def get_str_symbols(value:str|list, symbols_qty:int)->str:
        if isinstance(value, str):
            return str(value * symbols_qty + " ")
        if isinstance(value, list):
            result:str = ""
            for counter in range(symbols_qty):
                if counter < len(value):
                    result += value[counter]
                else:
                    result += " "
            return str(result + " ")

    def __str__(self)->str:
        if self.check_solved() or self.simplifier_representation:
            return "\n".join(
                [
                    "".join([value if isinstance(value, str) else " " for value in row])
                    for row in self.grid
                ]
            )
        result = ""
        max_symbols_qty = 0
        for row in self.grid:
            for cell in row:
                cell_size = len(cell)   if isinstance(cell,list) else 1
                if max_symbols_qty < cell_size:
                    max_symbols_qty = cell_size

        for y_counter in range(self.square_size):
            if y_counter and y_counter % self.subsquare_height == 0:
                result += "\n"
            for x_counter in range(self.square_size):
                cell_value = self.grid[y_counter][x_counter]
                if x_counter and x_counter % self.subsquare_width == 0:
                    result += "  "
                result += self.get_str_symbols(
                    value=cell_value,
                    symbols_qty=     max_symbols_qty
                )
            result += "\n"
        return result

    def check_valid(self):
        for row in self.grid:
            if len(set(row)) != len(self.possible_values):
                raise ValueError(f"Invalid row {row}")
        for column_number in range(len(self.possible_values)):
            if len(set([row[column_number] for row in self.grid])) != len(self.possible_values):
                raise ValueError(f"Invalid row {row}")

    def check_solved(self)->bool:
        for row in self.grid:
            for cell in row:
                if isinstance(cell, list):
                    return False
        self.check_valid()
        return True

    def simplify_as_possible(self):
        while True:
            self.calculate_all_possible_values()
            if not self.replace_options_by_values():
                break

    def solve(self):
        self.simplify_as_possible()
        if self.check_solved():
            return self
        possible_branches = self.create_possible_branches()
        for branch in possible_branches:
            try:
                solved_branch = branch.solve()
                return solved_branch
            except ValueError:
                print("Branch failed - no problem")

    def all_possible_solutions(self)->list:
        self.simplify_as_possible()
        if self.check_solved():
            return [deepcopy(self)]
        possible_branches = self.create_possible_branches()
        possible_solutions = []
        for branch in possible_branches:
            try:
                solved_branches = branch.all_possible_solutions()
                possible_solutions.extend(solved_branches)
            except ValueError:
                pass
        return possible_solutions

    def merge_solutions(self, solutions: list):
        self.grid = []
        for counter in range(len(self.possible_values)):
            self.grid.append(list([[] for i in range(len(self.possible_values))]))
        for solution in solutions:
            for row_counter in range(len(self.possible_values)):
                for column_counter in range(len(self.possible_values)):
                    self.grid[row_counter][column_counter].append(
                        solution.grid[row_counter][column_counter]
                    )
        for row_counter in range(len(self.possible_values)):
            for column_counter in range(len(self.possible_values)):
                self.grid[row_counter][column_counter] = list(
                    set(self.grid[row_counter][column_counter])
                )
        self.replace_options_by_values()

    def get_worst_cell(self):
        max_options = 1
        r = -1
        c = -1
        for row_counter, row in enumerate(self.grid):
            for column_counter, cell in enumerate(row):
                if isinstance(cell, list) and len(cell) > max_options:
                    r = row_counter
                    c = column_counter
                    max_options = len(cell)
        return r + 1, c + 1, max_options

    def print_diff(self, answer):
        for symbol_solution, symbol_original in zip(str(answer), str(self)):
            if symbol_original == symbol_solution and symbol_solution != "\n":
                print(bg.yellow + symbol_solution + bg.rs, end="")
            else:
                print(symbol_solution, end="")

#23
# original_task = Sudoku(
#     sudoku_matrix="""123456
# 456123
# 6 5  4
# 31
# 56
# """,
#     possible_values=["1", "2", "3", "4", "5", "6"],
#     subsquare_width=2, subsquare_height=3,
# )


# 43
original_task = Sudoku(
    sudoku_matrix="""A  C    9  7
    4BA3
  5  6C  4
1    53    9
 8  C  A  4
 329    A8B
 43B    761
 2  7  6  C
7    15    A
  6  72  9
    5369
2  A    3  6""",
    possible_values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C"],
    subsquare_width=4, subsquare_height=3,
)

# 43
# original_task = Sudoku(
#     sudoku_matrix="""A64C12859B37
# 81974BA3C562
# 3B5  6C  4
# 1    53    9
#  8  C  A  4
#  329    A8B
#  43B    761
#  2  7  6  C
# 7    15    A
#   6  72  9
#     5369
# 2  A    3  6""",
#     possible_values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C"],
#     subsquare_width=4, subsquare_height=3,
# )


# 33
# original_task = Sudoku(
#     sudoku_matrix="""    89
#       47
# 6
#  2 3
#  4      9
#        68
# 8 9 5
#    7  2
# 5""",
#     possible_values=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
#     subsquare_width=3,
# )

#44
# original_task = Sudoku(
#     sudoku_matrix="""3E C 9      5  8
# F  6E  B  72 1A
# G 9AC 82F  5 7BD
#    7  D 8  9CF3
# 1 A 47 D6G 8 59F
# 6 ED     A54
#  7F  AG 3 1CD 6
# 82 G 69 B  F3 4C
# D9  7E3 5F G C1
#  3 8  A5  674DF
# A C  2B  483   9
# 4G E  1 A B 6
#  6 FB5    9  3 1
#     G 43D5C    2
# 5   FD 9 B 1AEC
#   G92   43 A""",
#     possible_values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"],
#     subsquare_width=4,
# )

solution = deepcopy(original_task)
original_task.simplify_representation()
solutions = solution.all_possible_solutions()
if not solutions:
    raise IndexError("No solution found")
if len(solutions) > 1:
    print(f"Found {len(solutions)} solutions. Merging...")
    solution.merge_solutions(solutions)
    print("Solutions merged. Result:")
    print(solution)
    worst_cell = solution.get_worst_cell()
    print(
        f"Worst cell {worst_cell[0]}, {worst_cell[1]} contains {worst_cell[2]} options"
    )
else:
    print("Difference is:")
    original_task.print_diff(solutions[0])

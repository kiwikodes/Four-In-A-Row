"""
This program plays a modified version of connect 4 where you accumulate as many 4 in a rows as possible.
It creates a GUI that has many additions add for the player's comfort. For example, it has:
zooming, player selection, move highlighting, connection highlighting, move visualising, a menu with game controls and points, and an AI

Name: Miles Scherer
ID: 174855369
UPI: msch213
"""


import sys, time, tkinter as tk
from tkinter import messagebox
from idlelib.tooltip import Hovertip


class FourInARow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Four In A Row! - msch213')
        self.window.resizable(False, False)

        self.preferences = Preferences(self)
        self.board = HiddenBoard(self, 0)
        self.canvas = VisualBoard(self, 0)
        self.menu = Menu(self)
        self.ai = AI(self)

        self.players = 0
        self.can_move = False

        self.create_menubar()
        self.window.mainloop()


    def create_menubar(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label='New Game', accelerator='Ctrl+N', command=self.menu.new_game)
        file_menu.add_command(label='Restart Game', accelerator='Ctrl+R', command=self.menu.restart_game)
        file_menu.add_command(label='Exit', accelerator='Ctrl+Q', command=self.menu.quit_game)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label='Zoom In', accelerator='Ctrl+=', command=lambda: self.preferences.zoom(0.1))
        view_menu.add_command(label='Zoom Out', accelerator='Ctrl+-', command=lambda: self.preferences.zoom(-0.1))
        view_menu.add_command(label='Reset Zoom', accelerator='Ctrl+0', command=lambda: self.preferences.zoom(0))

        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='View', menu=view_menu)

        self.window.bind('<Control-n>', self.menu.new_game)
        self.window.bind('<Control-r>', self.menu.restart_game)
        self.window.bind('<Control-q>', self.menu.quit_game)
        self.window.bind('<Control-equal>', lambda event: self.preferences.zoom(0.1))
        self.window.bind('<Control-minus>', lambda event: self.preferences.zoom(-0.1))
        self.window.bind('<Control-0>', lambda event: self.preferences.zoom(0))
        self.window.protocol('WM_DELETE_WINDOW', self.menu.quit_game)


    def set_players(self, players):
        self.players = players

        # Replace player selection menu with size selection menu
        self.menu.players_menu.grid_remove()
        self.menu.size_menu.grid(columnspan=2, row=5, sticky='ew')
        self.menu.prompt.config(text='What size board\nwould you like?')


    def set_size(self, size):
        self.board.__init__(self, size)
        self.canvas.size = size
        self.canvas.cells = self.canvas.draw()

        self.menu.points[0].config(text='* P1 - 0')
        self.menu.points[1].config(text=['BOT', 'P2'][self.players > 1] + ' - 0')
        self.menu.prompt.config(text='Good luck!')

        self.canvas.canvas.bind('<ButtonRelease-1>', self.on_click)
        self.canvas.canvas.bind('<Motion>', self.canvas.show_move)
        self.can_move = True

        # Replace size selection menu with game menu
        self.menu.size_menu.grid_remove()
        self.menu.game_menu.grid(columnspan=2, row=5, sticky='ew')


    def on_click(self, event):
        cell_size = self.preferences.gui['cell'].get()
        outline_size = self.preferences.gui['outline'].get()
        spacing_size = self.preferences.gui['spacing'].get()

        # Find column cursor is in
        col = max(min((self.window.winfo_pointerx() - self.window.winfo_rootx() - \
        outline_size - spacing_size // 2) // (cell_size + spacing_size), self.board.size - 1), 0)

        if not (col in self.board.get_valid_moves() and self.can_move):
            return

        # Disable moves (to prevent moves sending before the other ones are received)
        self.can_move = False
        self.board.make_move(col)

        # If playing against bot, queue bot's move
        if self.players == 1 and not self.board.is_gameover():
            self.board.make_move(self.ai.get_move())

        # Display winning message
        if self.board.is_gameover():
            self.canvas.canvas.unbind('<ButtonRelease-1>')
            self.canvas.canvas.unbind('<Motion>')
            self.canvas.canvas.delete('highlight')

            # Remove the asterisk as there's no active player
            self.menu.points[0].config(text=f'P1 - {self.board.points[0]}')
            self.menu.points[1].config(text=f"{['BOT', 'P2'][self.players > 1]} - {self.board.points[1]}")

            if self.board.points[0] == self.board.points[1]:
                self.menu.prompt.config(text="It's a draw!")
            elif self.players == 1:
                self.menu.prompt.config(text=('Congratulations!\nYou win!', 'Unfortunate!\nYou lose!')[self.board.points[0] < self.board.points[1]])
            else:
                self.menu.prompt.config(text=f'Player {(self.board.points[0] < self.board.points[1]) + 1} wins!')
            return

        self.can_move = True


class Preferences:
    def __init__(self, game):
        self.game = game
        self.scale = 1

        self.gui = {
            'cell': tk.IntVar(value=50), 'spacing': tk.IntVar(value=10),
            'outline': tk.IntVar(value=4), 'text': tk.IntVar(value=12),
            'default': {'cell': 50, 'spacing': 10, 'outline': 4, 'text': 12}
        }


    def zoom(self, factor):
        if self.scale < 0.85 and factor == -0.1:
            return
        elif factor == 0:
            self.scale = 1

        # Set gui values to scaled values
        self.scale += factor
        for key in self.gui['default'].keys():
            self.gui[key].set(self.gui['default'][key] * self.scale)

        self.game.menu.redraw()
        self.game.canvas.redraw()


class Menu:
    def __init__(self, game):
        self.game = game
        self.create()


    def create(self):
        self.menu = tk.Frame(self.game.window, bg='#36454F'); self.menu.pack(fill=tk.Y, expand=True, side=tk.LEFT)
        self.menu.rowconfigure((3, 4), weight=1)
        
        # Titles
        tk.Label(self.menu, text='Four In', bg='#36454F', fg='#EEC643', font=('Helvetica', 36, 'bold'), padx=36
        ).grid(columnspan=2, row=0, pady=(18, 0))
        tk.Label(self.menu, text='A Row', bg='#36454F', fg='#EE5622', font=('Helvetica', 36, 'bold')
        ).grid(columnspan=2, row=1)
        tk.Label(self.menu, text='By Miles Scherer', bg='#36454F', fg='#CFD7DE', font=('Helvetica', 9)
        ).grid(columnspan=2, row=2, pady=(5, 0))

        # Point boxes
        self.points = (tk.Label(self.menu, text='P1 - 0', bg='#536878', fg='#EEC643', font=('Courier New', 12, 'bold'), 
                                highlightbackground='#44535F', highlightthickness=4, padx=12, pady=6
        ), tk.Label(self.menu, text='P2 - 0', bg='#536878', fg='#EE5622', font=('Courier New', 12, 'bold'), 
                    highlightbackground='#44535F', highlightthickness=4, padx=12, pady=6
        )); self.points[0].grid(column=0, row=3); self.points[1].grid(column=1, row=3)

        # Prompt box
        self.prompt = tk.Label(self.menu, text='Welcome to\nFour In A Row!', bg='#536878', fg='#CFD7DE', 
                               font=('Courier New', 12, 'bold'), highlightbackground='#44535F', highlightthickness=4, padx=12, pady=6
        ); self.prompt.grid(columnspan=2, row=4)

        # Game menu
        self.game_menu = tk.Frame(self.menu); self.game_menu.columnconfigure((0, 1), weight=1); self.game_menu.grid(columnspan=2, row=5, sticky='ew')
        tk.Button(self.game_menu, text='New Game', height=3, command=self.new_game, font=('Helvetica', 12), 
                  bg='#536878', fg='#CFD7DE', activebackground='#36454F').grid(columnspan=2, row=0, sticky='ew')
        tk.Button(self.game_menu, text='Restart', height=2, width=1, command=self.restart_game, font=('Helvetica', 12),
                  bg='#536878', fg='#CFD7DE', activebackground='#36454F').grid(column=0, row=1, sticky='ew')
        tk.Button(self.game_menu, text='Quit', height=2, width=1, command=self.quit_game, font=('Helvetica', 12),
                  bg='#536878', fg='#CFD7DE', activebackground='#36454F').grid(column=1, row=1, sticky='ew')

        # Players menu
        self.players_menu = tk.Frame(self.menu); self.players_menu.columnconfigure((0, 1), weight=1)
        for i in range(2):
            size_button = tk.Button(self.players_menu, text=f'{i + 1}', command=lambda i=i + 1: self.game.set_players(i), height=4, width=1,
                                    font=('Helvetica', 12), bg='#536878', fg='#CFD7DE', activebackground='#36454F')
            size_button.grid(column=i, row=0, sticky='ew')
            Hovertip(size_button, ('Play against the bot', 'Play against another human')[i], hover_delay=500)

        # Size menu
        self.size_menu = tk.Frame(self.menu); self.size_menu.columnconfigure((0, 1, 2, 3, 4), weight=1)
        for i in range(10):
            tk.Button(self.size_menu, text=f'{i + 1}', command=lambda i=i: self.game.set_size(i + 1), height=2, width=1, 
                      font=('Helvetica', 12), bg='#536878', fg='#CFD7DE', activebackground='#36454F').grid(column=i % 5, row=i // 5, sticky='ew')


    def redraw(self):
        outline_size = self.game.preferences.gui['outline'].get()
        text_size = self.game.preferences.gui['text'].get()

        title_elements = self.menu.winfo_children()
        title_elements[0].config(font=('Helvetica', text_size * 3, 'bold'), padx=text_size * 3)
        title_elements[1].config(font=('Helvetica', text_size * 3, 'bold'))
        title_elements[2].config(font=('Helvetica', int(text_size * 0.8)))

        for item in (self.points[0], self.points[1], self.prompt):
            item.config(font=('Courier New', text_size, 'bold'), highlightthickness=outline_size, padx=text_size, pady=int(text_size * 0.5))
        for button in self.game_menu.winfo_children():
            button.config(font=('Helvetica', text_size))
        for button in self.players_menu.winfo_children():
            button.config(font=('Helvetica', text_size))
        for button in self.size_menu.winfo_children():
            button.config(font=('Helvetica', text_size))


    def new_game(self, event=None):
        if self.game.board.is_ongoing() and not messagebox.askyesno('Four In A Row! - New Game',
        'Are you sure you would like to start a new game?'):
            return

        self.game_menu.grid_remove()
        self.players_menu.grid(columnspan=2, row=5, sticky='ew')
        self.prompt.config(text='How many players\nwould you like?')


    def restart_game(self, event=None):
        if self.game.players == 0 or not messagebox.askyesno('Four In A Row! - Restart Game',
        'Are you sure you would like to restart the current game?'):
            return

        self.game.set_size(self.game.canvas.size)


    def quit_game(self, event=None):
        if messagebox.askyesno('Four In A Row! - Quit Game', 'Are you sure you would like to quit?'):
            self.game.window.destroy()


class HiddenBoard:
    def __init__(self, game, size):
        self.game = game
        self.size = size

        self.cells = [[0] * size for _ in range(size)]
        self.entries = [0] * size
        self.points = [0, 0]
        self.player = 1


    def get_valid_moves(self):
        return [col for col in range(self.size) if self.entries[col] != self.size]


    def make_move(self, col, check=False):
        connections = ([], [], [], [])
        points = 0

        # Update board
        self.cells[col][self.entries[col]] = self.player
        self.entries[col] += 1

        # Calculate points
        row = self.entries[col] - 1
        # Horizontal
        for i in range(max(-3, -col), min(1, self.size - col - 3)):
            is_connection = [self.cells[col + i + c][row] for c in range(4)] == [self.player] * 4
            points += is_connection
            if is_connection:
                connections[0].append(i)
        # Vertical
        for i in range(max(-3, -row), min(1, self.size - row - 3)):
            is_connection = [self.cells[col][row + i + c] for c in range(4)] == [self.player] * 4
            points += is_connection
            if is_connection:
                connections[1].append(i)
        # Positive diagonal
        for i in range(max(-3, -col, -row), min(1, self.size - col - 3, self.size - row - 3)):
            is_connection = [self.cells[col + i + c][row + i + c] for c in range(4)] == [self.player] * 4
            points += is_connection
            if is_connection:
                connections[2].append(i)
    	# Negative diagonal
        for i in range(max(-3, -col, row - self.size + 1), min(1, self.size - col - 3, row - 2)):
            is_connection = [self.cells[col + i + c][row - i - c] for c in range(4)] == [self.player] * 4
            points += is_connection
            if is_connection:
                connections[3].append(i)

        # Undo move and return point count
        if check:
            self.cells[col][self.entries[col] - 1] = 0
            self.entries[col] -= 1
            return points
        
        else:
            # Update points and change turn
            self.points[self.player - 1] += points
            self.player = 3 - self.player

            # Update canvas
            self.game.canvas.make_move(col, row)
            self.game.canvas.show_connections(col, row, connections)

            # Update point boxes
            self.game.menu.points[0].config(text=f"{'* ' * (2 - self.player)}P1 - {self.points[0]}")
            self.game.menu.points[1].config(text=f"{'* ' * (self.player - 1)}{['BOT', 'P2'][self.game.players > 1]} - {self.points[1]}")


    def is_gameover(self):
        return sum(self.entries) == self.size ** 2


    def is_ongoing(self):
        return sum(self.entries) > 0 and not self.is_gameover()


class VisualBoard:
    def __init__(self, game, size):
        self.game = game
        self.size = size

        self.canvas = tk.Canvas(self.game.window, bg='#36454F', highlightthickness=0)
        self.canvas.pack(fill=tk.Y, side=tk.LEFT)
        self.cells = self.draw()

    
    def draw(self):
        cell_size = self.game.preferences.gui['cell'].get()
        spacing_size = self.game.preferences.gui['spacing'].get()
        outline_size = self.game.preferences.gui['outline'].get()

        self.canvas.delete('all')

        # Drawing board
        self.canvas.create_rectangle(
            outline_size // 2, outline_size // 2 + spacing_size + cell_size,
            self.size * (spacing_size + cell_size) + spacing_size + outline_size * 1.5, 
            (self.size + 1) * (spacing_size + cell_size) + spacing_size + outline_size * 1.5,
            fill='#536878', outline='#44535F', width=outline_size, tag='board')

        # Creating board cells
        cells = []
        for row in range(self.size):
            for col in range(self.size):
                cells.append(self.canvas.create_oval(
                    col * (spacing_size + cell_size) + outline_size + spacing_size,
                    (row + 1) * (spacing_size + cell_size) + outline_size + spacing_size, 
                    (col + 1) * (spacing_size + cell_size) + outline_size - 1,
                    (row + 2) * (spacing_size + cell_size) + outline_size - 1,
                    fill='#36454F', outline='#44535F', width=outline_size // 2))
    	
        # Setting canvas size to fit board
        self.canvas.config(height=min((self.size + 2) * (spacing_size + cell_size) + outline_size * 2 - cell_size, sys.float_info.max * self.size),
                           width=min(self.size * (spacing_size + cell_size) + spacing_size + outline_size * 2, sys.float_info.max * self.size))

        return cells


    def redraw(self):
        cell_size = self.game.preferences.gui['cell'].get()
        spacing_size = self.game.preferences.gui['spacing'].get()
        outline_size = self.game.preferences.gui['outline'].get()

        # Redraw board
        self.canvas.coords(
            'board', outline_size // 2, outline_size // 2 + spacing_size + cell_size,
            self.size * (spacing_size + cell_size) + spacing_size + outline_size * 1.5, 
            (self.size + 1) * (spacing_size + cell_size) + spacing_size + outline_size * 1.5)
        self.canvas.itemconfig('board', width=outline_size)

        # Redraw cells and connection outlines
        for row in range(1, self.size + 1):
            for col in range(self.size):
                self.canvas.coords(
                    self.cells[(row - 1) * self.size + col], 
                    col * (spacing_size + cell_size) + outline_size + spacing_size,
                    row * (spacing_size + cell_size) + outline_size + spacing_size, 
                    (col + 1) * (spacing_size + cell_size) + outline_size - 1,
                    (row + 1) * (spacing_size + cell_size) + outline_size - 1)
                self.canvas.itemconfig(self.cells[(row - 1) * self.size + col], width=outline_size // 2)
        self.canvas.itemconfig('connected', width=outline_size)

        # Changing canvas size to fit board
        self.canvas.config(height=min((self.size + 2) * (spacing_size + cell_size) + outline_size * 2 - cell_size, sys.float_info.max),
                           width=min(self.size * (spacing_size + cell_size) + spacing_size + outline_size * 2, sys.float_info.max))

        # Redraw move highlight
        self.show_move()


    def show_move(self, event=None):
        self.canvas.delete('highlight')

        if self.game.players == 0 or self.game.board.player > self.game.players:
            return

        cell_size = self.game.preferences.gui['cell'].get()
        spacing_size = self.game.preferences.gui['spacing'].get()
        outline_size = self.game.preferences.gui['outline'].get()

        # Find board column cursor is in
        col = max(min((self.game.window.winfo_pointerx() - self.game.window.winfo_rootx() - \
        outline_size - spacing_size // 2) // (cell_size + spacing_size), self.size - 1), 0)

        # Drawing highlight counter
        self.canvas.create_oval(
            col * (spacing_size + cell_size) + outline_size + spacing_size, spacing_size // 2, 
            (col + 1) * (spacing_size + cell_size) + outline_size - 1, spacing_size // 2 + cell_size - 1,
            fill=('#BFA546', '#BF512D')[self.game.board.player - 1], tags='highlight', width=0)


    def make_move(self, col, row):
        self.show_move()

        # If player quits game mid animation, don't throw error
        try:
            colour = ('#EEC643', '#EE5622')[2 - self.game.board.player]
            for cell in range(self.size - row):
                if cell > 0:
                    self.canvas.itemconfig(self.cells[(cell - 1) * self.size + col], fill='#36454F')

                # If player restarts game, cancel animation
                if self.game.can_move:
                    return

                self.canvas.itemconfig(self.cells[cell * self.size + col], fill=colour)
                time.sleep(0.06)
                self.canvas.update()
        except:
            return


    def show_connections(self, col, row, connections):
        colour = ('#B29432', '#B24019')[2 - self.game.board.player]
        outline_size = self.game.preferences.gui['outline'].get()

        # Horizontal
        for counter in connections[0]:
            for i in range(counter, counter + 4):
                self.canvas.itemconfig(self.cells[(self.size - row - 1) * self.size + col + i], width=outline_size, outline=colour, tag='connected')

        # Vertical
        for counter in connections[1]:
            for i in range(counter, counter + 4):
                self.canvas.itemconfig(self.cells[(self.size - row - 1 - i) * self.size + col], width=outline_size, outline=colour, tag='connected')

        # Positive diagonal
        for counter in connections[2]:
            for i in range(counter, counter + 4):
                self.canvas.itemconfig(self.cells[(self.size - row - 1 - i) * self.size + col + i], width=outline_size, outline=colour, tag='connected')

        # Negative diagonal
        for counter in connections[3]:
            for i in range(counter, counter + 4):
                self.canvas.itemconfig(self.cells[(self.size - row - 1 + i) * self.size + col + i], width=outline_size, outline=colour, tag='connected')


class AI:
    def __init__(self, game):
        self.game = game

    
    def get_move(self):
        ordered_cols = ()
        points = ()

        # Organise columns into centered order
        for i in range(self.game.board.size - 1, -1, -1):
            if i % 2 == 0:
                ordered_cols += (self.game.board.size - 1 - i // 2,)
            else:
                ordered_cols += (i // 2,)

        # Remove ordered columns that aren't valid moves, but retain order
        moves = [col for col in ordered_cols if col in self.game.board.get_valid_moves()]

        # Check for points each move would generate
        for move in moves:
            points += (self.game.board.make_move(move, True),)

        # If there are no points for the AI, try block the player
        if max(points) < 1:
            points = ()
            self.game.board.player = 1
            for move in moves:
                points += (self.game.board.make_move(move, True),)
            self.game.board.player = 2

        return moves[points.index(max(points))]


game = FourInARow()


"""
class AlphaBetaAI:
    def __init__(self, game):
        self.game = game

    def get_best_move(self, depth, alpha, beta):
        if depth == 0:
            return evaluation
        
        moves = self.generate_moves()

        # If end of the game is reached
        if len(moves) == 0:
            return evaluation

        for move in moves:
            self.game.board.make_move(move)
            evaluation = -self.get_best_move(depth - 1, -beta, -alpha)
            self.game.board.unmake_move(move)
            if evaluation >= beta:
                return beta
            alpha = max(alpha, evaluation)

        return alpha


    # Board function for AlphaBeta AI to work on

    def evaluation(self):
        evaluation = 0

        # Horizontals
        for i in range(self.size - 3):
            for j in range(self.size):
                evaluation += [self.cells[i + c][j] for c in range(4)] == [1] * 4
                evaluation -= [self.cells[i + c][j] for c in range(4)] == [2] * 4

        # Verticals
        for i in range(self.size):
            for j in range(self.size - 3):
                evaluation += [self.cells[i][j + c] for c in range(4)] == [1] * 4
                evaluation -= [self.cells[i][j + c] for c in range(4)] == [2] * 4            

        # Positive diagonals
        for i in range(self.size - 3):
            for j in range(self.size - 3):
                evaluation += [self.cells[i + c][j + c] for c in range(4)] == [1] * 4
                evaluation -= [self.cells[i + c][j + c] for c in range(4)] == [2] * 4            

        # Negative diagonals
        for i in range(self.size - 3):
            for j in range(3, self.size):
                evaluation += [self.cells[i + c][j - c] for c in range(4)] == [1] * 4
                evaluation -= [self.cells[i + c][j - c] for c in range(4)] == [2] * 4

        return evaluation
"""
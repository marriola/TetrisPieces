###########################################################################
## GLOBAL IMPORTS
###########################################################################

from __future__ import print_function
from copy import copy
import pygtk
import gtk
import gtk.glade
from random import randint, shuffle

pygtk.require("2.0")


###########################################################################
## GLOBAL DEFINITIONS
###########################################################################

MATRIX_WIDTH = 50
MATRIX_HEIGHT = 50

BLOCK_SIZE = 13
GAP_SIZE = 2

MATRIX_BACKGROUND = gtk.gdk.Color("#111111")

COLOR_MAP = { 0: MATRIX_BACKGROUND,
			  1: gtk.gdk.Color("#cc0000"),
			  2: gtk.gdk.Color("#cc00cc"),
			  3: gtk.gdk.Color("#008800"),
			  4: gtk.gdk.Color("#0000cc"),
			  5: gtk.gdk.Color("#cc6600"),
			  6: gtk.gdk.Color("#00cc88") }

PIECE_I =\
	[[1],
	 [1],
	 [1],
	 [1]]

PIECE_Z =\
	[[2, 2, 0],
	 [0, 2, 2]]

PIECE_S =\
	[[0, 3, 3],
	 [3, 3, 0]]

PIECE_T =\
	[[0, 4, 0],
	 [4, 4, 4]]

PIECE_L =\
	[[5, 0],
	 [5, 0],
	 [5, 5]]

PIECE_J =\
	[[0, 6],
	 [0, 6],
	 [6, 6]]

PIECES = [PIECE_I, PIECE_Z, PIECE_S, PIECE_T, PIECE_L, PIECE_J]

ROTATE_0 = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

ORIENTATIONS = [ROTATE_0, ROTATE_90, ROTATE_180, ROTATE_270]


###########################################################################
## TETRIS MATRIX FUNCTIONS
###########################################################################

def new_matrix():
	matrix = []
	for n in range(MATRIX_HEIGHT):
		matrix.append([0] * MATRIX_WIDTH)
	return matrix

###########################################################################

def rotate_piece(piece, orientation):
	height = len(piece)
	width = len(piece[0])

	if orientation == ROTATE_0:
		return piece

	elif orientation == ROTATE_90:
		new_piece = []
		for col in range(0, width):
			new_row = []
			for row in reversed(range(0, height)):
				new_row.append(piece[row][col])
			new_piece.append(new_row)
		return new_piece

	elif orientation == ROTATE_180:
		new_piece = []
		for row in reversed(piece):
			new_piece.append(list(reversed(row)))
		return new_piece

	elif orientation == ROTATE_270:
		new_piece = []
		for col in reversed(range(0, width)):
			new_row = []
			for row in range(0, height):
				new_row.append(piece[row][col])
			new_piece.append(new_row)
		return new_piece

	return None


###########################################################################

def place_piece(matrix, place_x, place_y, piece, orientation):
	"""Attempts to place a piece on a matrix. If the piece would overlap
	any other pieces, the function returns the tuple (False, matrix).
	Otherwise, it returns (True, new_matrix)."""
	rotated_piece = rotate_piece(piece, orientation)

	if (place_x + len(rotated_piece[0]) >= len(matrix[0]) or
	   place_y + len(rotated_piece) >= len(matrix)):
	   return (False, matrix)

	new_matrix = []
	for row in matrix:
		new_matrix.append([])
		for block in row:
			new_matrix[len(new_matrix) - 1].append(block)

	for block_y, row in enumerate(rotated_piece):
		for block_x, block in enumerate(row):
			if block != 0:
				if matrix[block_y + place_y][block_x + place_x] != 0:
					return (False, matrix)
				new_matrix[block_y + place_y][block_x + place_x] = block

	return (True, new_matrix)


###########################################################################

def attachment_points(matrix, piece, place_x, place_y):
	"""Returns a list of empty cells around a piece in the matrix."""
	height = len(piece)
	width = len(piece[0])

	points = []
	for y in range(place_y - 1, place_y + height + 1):
		for x in range(place_x - 1, place_x + width + 1):
			if (x >= 0 and y >= 0 and
				x < MATRIX_WIDTH and y < MATRIX_HEIGHT and
				matrix[y][x] == 0):
				points.append((x, y))

	return points


###########################################################################

def fill_matrix(matrix, place_x=0, place_y=0):
	def has_gaps(matrix):
		"""Returns true if there are any empty cells in the matrix."""
		for row in matrix:
			for block in row:
				if block == 0:
					return True
		return False

	def make_pairs():
		"""Generates all possible combinations of tetriminoes and orientations."""
		pairs = []
		for piece in PIECES:
			for orientation in ORIENTATIONS:
				pairs.append((piece, orientation))
		shuffle(pairs)
		return pairs

	matrices = [(0, make_pairs(), matrix)]

	# keep trying tetrimino-orientation pairs until the matrix is full
	while has_gaps(matrices[0][1]):
		iteration, pairs, this_matrix = matrices[0]
		print("iteration", iteration, "\t", len(pairs), "pairs")
		if len(pairs) == 0:
			# no piece-orientation pairs to try -- back up
			matrices = matrices[1:]
			continue

		piece, orientation = pairs[0]
		pairs = pairs[1:]
		result, new_matrix = place_piece(this_matrix, place_x, place_y, piece, orientation)
		if result:
			for i in range(0, iteration):
				print("\t", end=None)
			print("placed at", place_x, "x", place_y)
			attach = attachment_points(new_matrix, piece, place_x, place_y)
			new_place_x = attach[0][0]
			new_place_y = attach[0][1]
			place_x = new_place_x
			place_y = new_place_y
			for i in range(0, iteration):
				print("\t", end=None)
			print("next iteration from", new_place_x, "x", new_place_y)
			matrices.insert(0, (iteration + 1, pairs, new_matrix))
			#count += 1
			#print count
		else:
			# piece doesn't fit, drop this piece-orientation pair and try the next
			matrices[0] = (iteration, pairs[1:], this_matrix)

	return matrices[0][2]


###########################################################################

class TetrisWindow:
	def __init__(self):
		self.pixmap = None

		self.matrix = new_matrix()

		self.gladefile = "TetrisPieces.glade"
		self.glade = gtk.Builder()
		self.glade.add_from_file(self.gladefile)
		self.glade.connect_signals(self)

		self.window1 = self.glade.get_object("window1")
		self.drawing = self.glade.get_object("drawingarea1")

		self.window1.show_all()


	###########################################################################
	## GUI callback methods
	###########################################################################

	def on_btn_generate_clicked(self, widget):
		self.matrix = new_matrix()
		self.matrix = fill_matrix(self.matrix)
		self.drawing.queue_draw()


	###########################################################################

	def on_btn_exit_clicked(self, widget):
		gtk.main_quit()


	###########################################################################

	def on_window1_delete_event(self, widget, event, data=None):
		gtk.main_quit()


	###########################################################################

	def on_window1_destroy_event(self, widget, data=None):
		gtk.main_quit()


	###########################################################################

	def copy_pixmap_to_window(self, widget, x, y, width, height):
		drawable_gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
		widget.window.draw_drawable(drawable_gc, self.pixmap, x, y, x, y, width, height)


	###########################################################################

	def on_drawingarea1_configure_event(self, widget, event):
		x, y, width, height = widget.get_allocation()
		self.pixmap = gtk.gdk.Pixmap(widget.window, width, height)
		return True


	###########################################################################

	def on_drawingarea1_expose_event(self, widget, event):
		if self.matrix is None:
			return

		x, y, width, height = event.area
		gc = self.pixmap.new_gc()
		gc.set_rgb_fg_color(MATRIX_BACKGROUND)
		self.pixmap.draw_rectangle(gc, gtk.TRUE, 0, 0, width, height)

		for block_y in range(0, len(self.matrix)):
			for block_x in range(0, len(self.matrix[0])):
				gc.set_rgb_fg_color(COLOR_MAP[self.matrix[block_y][block_x]])
				self.pixmap.draw_rectangle(gc, gtk.TRUE,
										   block_x * BLOCK_SIZE + GAP_SIZE,
										   block_y * BLOCK_SIZE + GAP_SIZE,
										   BLOCK_SIZE - GAP_SIZE,
										   BLOCK_SIZE - GAP_SIZE)

		self.copy_pixmap_to_window(widget, x, y, width, height)


###############################################################################

if __name__ == "__main__":
	win = TetrisWindow()
	gtk.main()
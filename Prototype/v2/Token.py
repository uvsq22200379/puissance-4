from shapes import *
from global_variables import *
from tools import *

class Token:

	def __init__(self, column, color):
		self.pos = Vector(GRID_RECT.pos.x + column * (GRID_RECT.size.x / GRID_DIMS.x), GRID_RECT.pos.y - (GRID_RECT.size.y / GRID_DIMS.y))
		self.color = color
		self.speed = Vector(0, 0)
		self.visual = create_oval(Rectangle(self.pos, Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y)))
		canvas.itemconfig(self.visual, fill = color)
		self.GRAVITY = 1

	def move(self):
		self.speed.y += self.GRAVITY

		self.pos += self.speed
		set_pos(self.visual, self.pos)


	def get_rect(self):
		return Rectangle(self.pos, Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y))
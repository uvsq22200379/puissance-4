from shapes import *
from global_variables import *
from tools import *

class Token:

	def __init__(self, column, color):
		self.pos = Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y)/8 + Vector(GRID_RECT.pos.x + column * (GRID_RECT.size.x / GRID_DIMS.x), GRID_RECT.pos.y - (GRID_RECT.size.y / GRID_DIMS.y))
		self.color = color
		self.speed = Vector(0, 0)
		self.visual = create_oval(Rectangle(self.pos + Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y)/8, Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y) * 6/8))
		canvas.itemconfig(self.visual, fill = color)
		self.falling = True
		self.GRAVITY = 2

	def move(self):
		if self.falling:
			self.speed.y += self.GRAVITY

			self.pos += self.speed
			set_pos(self.visual, self.pos)
		else:
			self.speed.x = 0
			self.speed.y = 0

	def set_pos(self, v: Vector):
		self.pos = v
		set_pos(self.visual, self.pos)

	def get_rect(self):
		size = Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y)
		return Rectangle(self.pos + Vector(size.x/8, 0), size - Vector(size.x * 6/8, 0))
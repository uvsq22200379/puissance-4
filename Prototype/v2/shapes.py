from global_variables import *
from tools import *

def create_rectangle(box: Rectangle):
	return canvas.create_rectangle(box.pos.x, box.pos.y, box.pos.x + box.size.x, box.pos.y + box.size.y)

def create_oval(box: Rectangle):
	return canvas.create_oval(box.pos.x, box.pos.y, box.pos.x + box.size.x, box.pos.y + box.size.y, outline = "")

def get_pos(shape):
	return Vector(canvas.coords(shape)[0], canvas.coords(shape)[1])

def get_size(shape):
	return Vector(canvas.coords(shape)[2] - canvas.coords(shape)[0], canvas.coords(shape)[3] - canvas.coords(shape)[1])

def set_pos(shape, pos: Vector):
	cS = get_size(shape)

	canvas.coords(shape, pos.x, pos.y, pos.x + cS.x, pos.y + cS.y)

def set_size(shape, size: Vector):
	cP = get_pos(shape)

	canvas.coords(shape, cP.x, cP.y, cP.x + size.x, cP.y + size.y)
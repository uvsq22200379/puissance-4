from math import *
import tkinter as tk

class Vector:

	def __init__(self, x, y):
		self.x = x;
		self.y = y;

	def get_squared_lenght(self):
		return self.x ** 2 + self.y ** 2
	def get_lenght(self):
		return sqrt(get_squared_lenght)

	def __add__(self, v):
		return Vector(self.x + v.x, self.y + v.y)
	def __mul__(self, r):
		return Vector(self.x * r, self.y * r)
	def __sub__(self, v):
		return self + (v * -1)
	def __truediv__(self, r):
		return self * (1/r)

class Rectangle:

	def __init__(self, pos: Vector, size: Vector):
		self.pos = pos
		self.size = size

	def has_in(self, point: Vector):
		return point.x > self.pos.x and point.x < self.pos.x + self.size.x and point.y > self.pos.y and point.y < self.pos.y + self.size.y

	def intersects(self, rect):
		return not (self.pos.x > rect.pos.x + rect.size.x
				 or self.pos.x + self.size.x < rect.pos.x
				 or self.pos.y > rect.pos.y + rect.size.y
				 or self.pos.y + self.size.y < rect.pos.y)
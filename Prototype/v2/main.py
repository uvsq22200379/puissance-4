from Token import *
from global_variables import *
from shapes import *
from tools import *
from math import *

def main():

	grid_visual = []
	tokens = []
	team = [True]

	for x in range(GRID_DIMS.x):
		for y in range(GRID_DIMS.y):
			grid_visual.append(create_oval(Rectangle(Vector(GRID_RECT.pos.x + x * GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.pos.y + y * GRID_RECT.size.y / GRID_DIMS.y),
													 Vector(GRID_RECT.size.x / GRID_DIMS.x, GRID_RECT.size.y / GRID_DIMS.y))))
	def canvas_clicked(event):

		color = "red"
		if team[0]:
			color = "yellow"

		tokens.append(Token( int((event.x - GRID_RECT.pos.x)/(GRID_RECT.size.x / GRID_DIMS.x)) , color))

		team[0] = not team[0]

	canvas.bind("<Button-1>", canvas_clicked)

	def game_loop():

		for i in range(len(tokens)):
			if tokens[i].falling == False:
				continue
			for j in range(len(tokens)):
				
				futur = tokens[i].get_rect()
				futur.pos += tokens[i].speed

				if i != j and futur.intersects(tokens[j].get_rect()) or futur.pos.y + futur.size.y >= GRID_RECT.pos.y + GRID_RECT.size.y:
					tokens[i].speed.y = -3/4 * tokens[i].speed.y
					if (abs(tokens[i].speed.y) < tokens[i].GRAVITY/2) and tokens[i].pos.y > GRID_RECT.pos.y:
						tokens[i].falling = False
						slot = GRID_RECT.size.y / GRID_DIMS.y
						rel = tokens[i].pos.y - GRID_RECT.pos.y

						tokens[i].set_pos(Vector(tokens[i].pos.x, GRID_RECT.pos.y + int((rel + slot/4) / slot) * slot))
				
			tokens[i].move()

		if game_running:
			window.after(int(1000/60), game_loop)

	game_loop()

	window.mainloop()

if __name__ == "__main__":
	main()
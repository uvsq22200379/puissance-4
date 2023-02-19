from Token import *
from global_variables import *
from shapes import *
from tools import *



def main():

	test = Token(3, "red")

	def game_loop():

		test.move()

		if game_running:
			window.after(int(1000/60), game_loop)

	game_loop()

	window.mainloop()

if __name__ == "__main__":
	main()
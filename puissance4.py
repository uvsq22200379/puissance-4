'''
	Puissance 4

	JOURDAIN Anaïs
	CAICEDO LEMOS Vanessa
	GHARIB ALI BARURA Sama

	Programme réalisé dans le cadre du projet d'IN200
'''

import tkinter as tk
import numpy as np
from math import *
import time
from PIL import Image, ImageTk
import random


#Options

COLOR_PALETTE          = {
	"Red" : "#f63f34",
	"Yellow" : "#efbd20",
	"Cyan" : "#65abaf",
	"Grey" : "#9cafb7",
	"Turquoise" : "#59e38c"	

}
WINDOW_SIZE            = np.array([700, 600])
BACKGROUND             = COLOR_PALETTE["Cyan"]
GRID_POS               = WINDOW_SIZE / 4
GRID_SIZE              = WINDOW_SIZE / 2
GRID_DIMS              = np.array([7, 6])
SLOT_SIZE              = GRID_SIZE / GRID_DIMS
TOKEN_BOX              = SLOT_SIZE * 4/5
TOKEN_COLLISION_RADIUS = SLOT_SIZE[1] / 2
GRAVITY                = 2


#Variables globales

root = tk.Tk()
root.geometry(str(WINDOW_SIZE[0])+'x'+str(WINDOW_SIZE[1]) + "+0+0")
root.title("Puissance 4")
root.resizable(False, False)

canvas = tk.Canvas(root, width = WINDOW_SIZE[0], height = WINDOW_SIZE[1], bg = BACKGROUND)

canvas.grid()

widgets = [] #Toutes les widget crées doivent être dans cette liste afin de pouvoir les supprime à chaque changement d'écran
tokens_pos = [] #position des jetons dans le monde physique
tokens_speed = [] #vitesse des jetons
tokens_visu = [] #Representation graphique des jetons
is_static = [] #Définit si un jeton est un objet physique ou non

click_time = 0 # Permet d'empêcher le joueur de spammer les cliques

slot_image = Image.open("slot.png") # Image des cases
slot_image = slot_image.resize(np.array(SLOT_SIZE + (1, 1), dtype = int))
slot_imagetk = ImageTk.PhotoImage(slot_image)

logo_image = Image.open("puiss4nce.jpg") # Logo de l'écran de démarrage
logo_image = logo_image.resize(np.array(WINDOW_SIZE, dtype=int))
logo_imagetk = ImageTk.PhotoImage(logo_image)

image_play=Image.open("background.jpg") # Fond d'écran du menu principal
image_play_tk = ImageTk.PhotoImage(image_play)

fade_delay = 1500
fade_duration = 500

player1 = ""
player2 = ""

color_player1 = ""
color_player2 = ""

#Outils

# Fonctions permettant d'utiliser des tableaux numpy 1x2 (Vecteurs) pour créer des formes
def rectangle(pos, size):
	'''
		Retourne l'id tkinter d'un rectangle dont le côté supérieur gauche est à "pos" et qui mesure "size".
	'''
	return canvas.create_rectangle(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def oval(pos, size):
	'''
		Retourne l'id tkinter de l'oval inscrit dans le rectangle dont le point supérieur gauche est à "pos" et qui mesure "size"
	'''
	oval = canvas.create_oval(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1], width = 0)
	canvas.lower(oval) # On dessine les ovales derrière les images
	return oval
def create_slot(pos):
	'''
		Crée une case de puissance quatre à pos
	'''
	pos += SLOT_SIZE/2
	slot = canvas.create_image(pos[0], pos[1], image = slot_imagetk)
	canvas.tkraise(slot) # On dessine les images devant les ovales
	return slot
def set_pos(obj, pos, size):
	'''
		Change la position et la taille d'un item du canvas
	'''
	canvas.coords(obj, pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])

def delete_widgets():
	'''
		Supprime tous les widgets
	'''
	
	canvas.delete("all")

	for i in range(len(widgets)):
		widgets[i].place_forget()
	widgets.clear()

def raycast(o_start, stride):
	'''
		Lance un "rayon" de "o_start" jusqu'à 4*"stride" avec un pas de "stride" s'intérompant
		lorsqu'il tombe sur un jeton d'une couleur différente et renvoie le nombre de jetons 
		d'une même couleur touchés. 
	'''

	start = o_start.copy() # On copie o_start pour éviter de le modifier globalement

	count = 1
	other_token = False
	ray = start
	verifying = ""

	for i in range(4):

		current_color = ""
		found = False
		for i_ in range(len(tokens_pos)):
			pos = tokens_pos[i_]
			if ray[0] >= pos[0] and ray[0] <= pos[0] + SLOT_SIZE[0] \
		   and ray[1] >= pos[1] and ray[1] <= pos[1] + SLOT_SIZE[1]: # <=> Si le rayon touche un jeton
				current_color = canvas.itemcget(tokens_visu[i_], "fill")
				found = True
				break
		if not found:
			break
		if i==0:
			verifying = current_color # La couleur que l'on vérifie est la couleur du premier jeton touché par le rayon
		elif current_color == verifying:
			count += 1
		else:
			break

		ray += stride

	return count

# Chargement / Sauvegarde

def save(path):

	out = open(path, "w")

	for i in range(len(tokens_pos)):

		out.write(str(tokens_pos[i][0]) + ";" + str(tokens_pos[i][1]) + ";" 
			    + str(tokens_speed[i][0]) + ";" + str(tokens_speed[i][1]) + ";" + str(int(is_static[i])) + ";" + canvas.itemcget(tokens_visu[i], "fill")  + ";" + "\n")

	out.close()

def load(path):

	inn = open(path, "r")

	reading = True
	while reading:
		
		line = inn.readline()

		if line:
			
			buffer = ""
			phase = 0

			for c in line:

				if c == ";":
					if phase == 0:
						tokens_pos.append(np.array([float(buffer), 0]))
					elif phase == 1:
						tokens_pos[-1][1] = float(buffer)
					elif phase == 2:
						tokens_speed.append(np.array([float(buffer), 0]))
					elif phase == 3:
						tokens_speed[-1][1] = float(buffer)
					elif phase == 4:
						is_static.append(bool(buffer))
					elif phase == 5:
						visu = oval(tokens_pos[-1], SLOT_SIZE)
						canvas.itemconfig(visu, fill = buffer)
						tokens_visu.append(visu)

					phase += 1
					buffer = ""
					continue

				buffer += c
		else:
			reading = False

		print()

	inn.close()

def launch_load(path):
	global player1
	global player2

	player1 = widgets[0].get()
	player2 = widgets[1].get()

	delete_widgets()

	root.after(10, load(path))
	root.after(1, game)

#Jeu

playing = True
turn = False #False : Jeton jaune / True : Jeton rouge

def game_keys(event):
	'''
		Gère les entrées clavier lorsque le jeu tourne
	'''

	global playing

	if event.keysym == "Escape":
		retourner()
	if event.keysym == "BackSpace":
		annul_jeton()
	if event.keysym == "s":
		save("saved_games/test.game")
	if event.keysym == "l":
		load("saved_games/test.game")

matrice_base = np.zeros([GRID_DIMS[1],GRID_DIMS[0]]) #crée une matrice représentant la grille

def game_clicks(event):
	'''
		Gère les cliques lorsque le jeu tourne
	'''

	global turn
	global click_time
	global player1
	global player2
	global matrice_base


	if event.x <= GRID_POS[0] or event.x >= GRID_POS[0] + GRID_SIZE[0]:
		return # Si le clique est en dehors de la grille, on ne crée pas de jeton
	
	pos = np.array((GRID_POS[0] + SLOT_SIZE[0] * int((event.x - GRID_POS[0])/SLOT_SIZE[0]), GRID_POS[1] - SLOT_SIZE[1])) # On met le jeton dans la bonne colonne
	
	for t in tokens_pos:
		if pos[0] + SLOT_SIZE[0] <= t[0]\
		or pos[0] >= t[0] + SLOT_SIZE[0]\
		or pos[1] + SLOT_SIZE[1] * 2 <= t[1]\
		or pos[1] >= t[1] + SLOT_SIZE[1]:
			pass # Il n'y a pas de jeton qui obstrue le point d'appartition du nouveau jeton
		else:
			return # Un jeton obstrue le point d'apparition

	turn = not turn

	# Création d'un nouveau jeton

	visu = oval(pos, SLOT_SIZE)

	if turn:
		canvas.itemconfig(visu, fill = "firebrick")
		widgets[0]["text"] = "Au tour de " + player2
	else:
		canvas.itemconfig(visu, fill = "gold")
		widgets[0]["text"] = "Au tour de " + player1

	tokens_pos.append(pos)
	tokens_speed.append(np.array((0, 0)))
	tokens_visu.append(visu)
	is_static.append(False)
	
	click_time = time.time()

def annul_jeton():
	'''
		Annule le dernier jeton.
	'''
	global turn

	if len(tokens_pos) == 0: # Si il n'y a plus de jeton, nous interrompons la fonction
		return

	canvas.delete(tokens_visu[-1])
	tokens_pos.pop()
	tokens_speed.pop()
	tokens_visu.pop()
	is_static.pop()
	turn = not turn

def game_physics():
	'''
		Comportement physique des jetons (gravité, rebonds et collisions)
	'''

	global playing

	for i in range(len(tokens_pos)):

		if is_static[i]:
			continue # Nous n'appliquons pas le comportement physique à un jeton statique

		collides_another = False

		for j in range(len(tokens_pos)):
			if i==j or tokens_pos[j][1] < tokens_pos[i][1]:
				continue # On évite de tester si le jeton se collisione lui même ou avec un jeton plus haut


			if tokens_pos[i][0] > tokens_pos[j][0] + SLOT_SIZE[0]-1 or tokens_pos[i][0] + SLOT_SIZE[0]-1 < tokens_pos[j][0]:
				pass
			elif tokens_pos[i][1] + SLOT_SIZE[1] + tokens_speed[i][1] > tokens_pos[j][1] + tokens_speed[j][1]:
				collides_another = True
				break
			

		if not collides_another and tokens_pos[i][1] + tokens_speed[i][1] + SLOT_SIZE[1] <= GRID_POS[1] + GRID_SIZE[1]:
			tokens_pos[i] += tokens_speed[i]
		else:
			tokens_speed[i][1] = -1/2 * tokens_speed[i][1]
			if abs(tokens_speed[i][1]) < 1:
				tokens_pos[i] = GRID_POS + SLOT_SIZE * np.array( (tokens_pos[i] - GRID_POS) / SLOT_SIZE, dtype = int)
				is_static[i] = True

				horiz = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], 0)) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], 0)) - 1
				verti = raycast(tokens_pos[i] + TOKEN_BOX/2, (0, SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (0, -SLOT_SIZE[1])) - 1
				diag1 = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], -SLOT_SIZE[1])) - 1
				diag2 = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], -SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], SLOT_SIZE[1])) - 1

				if horiz >= 4 or verti >= 4 or diag1 >= 4 or diag2 >= 4:
					print("Victoire !!!")
					widgets.append(tk.Label(canvas, text = "Victoire"))
					widgets[-1].place(x=10,y=10)

		tokens_speed[i][1] += GRAVITY
		set_pos(tokens_visu[i], tokens_pos[i], SLOT_SIZE)

	if playing:
		root.after(int(1000/60), game_physics)



def game_visu():
	'''
		Crée les widgets et la grille du jeu
	'''

	for y in range(GRID_DIMS[1]):
		for x in range(GRID_DIMS[0]):
			#oval((x, y) * SLOT_SIZE + GRID_POS, SLOT_SIZE)
			create_slot((x, y) * SLOT_SIZE + GRID_POS)

	turn_info = tk.Label(canvas, text = "Au tour de Joueur " + str(1 + int(turn)), font = ("Comic Sans MS", WINDOW_SIZE[1]//16), bg = BACKGROUND)
	turn_info.place(x = 10, y = 10)

	widgets.append(turn_info)
	widgets.append(tk.Button(text = "Annuler le dernier jeton", font = ("Comic Sans MS", 12), command = annul_jeton))
	widgets[-1].place(x = int(7 * WINDOW_SIZE[0]/10), y = 10)

#

def game():
	'''
		Initialisation du jeu
	'''
	canvas.delete("all")
	delete_widgets()

	global playing
	global turn

	playing = True
	turn=random.randint(0,1)
	canvas.bind("<Button-1>", game_clicks)
	root.bind("<Key>", game_keys)
	game_visu()
	root.after(1, game_physics)


#Menu principal

def main_menu_clicks():
	'''
		Gère les cliques du menu principal
	'''
	global player1
	global player2

	player1 = widgets[0].get()
	player2 = widgets[1].get()

	delete_widgets()

	root.after(1, game)

def main_menu_visu():
	'''
		Crée les widgets du menu principal
	'''

	canvas.delete("all")

	canvas.create_image(0,200, image = image_play_tk)

	#instruction pour les joueurs, boutons du menu principal 

	font_size = int(WINDOW_SIZE[1]/23)
	
	canvas.create_text(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2+50, text= "Veuillez entrer le nom des joueurs", fill="black", font=("Calibri", 15))
	canvas.pack()

	canvas.create_text(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2+80, text= "avant de commencer", fill="black", font=("Calibri", 15))
	canvas.pack()

	canvas.create_text(WINDOW_SIZE[0]/2, 100, text="PUISSANCE 4", fill="red", font=("Calibri bold", 50))
	canvas.pack()

	charger_jeu=tk.Button(canvas,text="Charger", fg="black",font = ("Calibri bold", 15), command = lambda: launch_load("saved_games/test.game"))
	charger_jeu.place(x=300, y=200,anchor="nw")

	#fonction qui explique les instructions dans une nouvelle fenêtre

	def instructions():
		'''
			Montre les instructions de jeu
		'''
		canvas.delete("all")
		charger_jeu.place_forget()
		quitter_jeu.place_forget()
		jouer.place_forget()
		saisie1.place_forget()
		saisie2.place_forget()
		instructions_jeu.place_forget()
		canvas.create_text(WINDOW_SIZE[0]/2, 100, text= "Instructions:", fill="black", font=("Calibri", font_size))
		canvas.create_text(WINDOW_SIZE[0]/2, 200, text= "-Pour mettre un jeton cliquez sur la colonne souhaitée", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 250, text= "-Pour annuler un jeton cliquez sur le bouton droit de votre souris", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 300, text= "-Le but du jeu est de positionner 4 jetons de la même couleur consécutivement", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 350, text= "(horizontalement, verticalement ou diagonalement)", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 400, text= "A vous de jouer!", fill="black", font=("Calibri", 15))
		canvas.pack()

	#nouveaux boutons au menu principal 

	instructions_jeu = tk.Button(canvas, text="Instructions", font=("Calibri bold", 15), command = instructions)
	instructions_jeu.place(x=300, y=250, anchor="nw")

	couleurs = tk.Button(canvas, text = "Modif couleurs jetons", command = changer_couleurs)
	couleurs.place(x=300, y=300,anchor="nw") 
	widgets.append(couleurs)


	quitter_jeu=tk.Button(canvas,text="QUITTER",fg="red",font = ("Calibri bold", 15), command = quitter)
	quitter_jeu.place(x=WINDOW_SIZE[0]-100, y=WINDOW_SIZE[1]-100)

	retour = tk.Button(canvas, text="RETOURNER AU MENU PRINCIPAL", font = ("Calibri bold", 15), command = retourner)
	retour.place(x=25, y=WINDOW_SIZE[1]-100)

	jouer = tk.Button(canvas, text = "Jouer", font = ("Calibri bold", 15), command = game)
	jouer.place(x=300, y=150,anchor="nw") 


	#zone de saisie pour que les joueurs rentrent leurs noms 
	saisie1 = tk.Entry(canvas)
	saisie1.insert(0, "Joueur 1")
	saisie1.place(x=WINDOW_SIZE[0]/2-290, y=WINDOW_SIZE[1]/2+130)

	saisie2 = tk.Entry(canvas)
	saisie2.insert(0, "Joueur 2")
	saisie2.place(x=WINDOW_SIZE[0]/2 +90, y=WINDOW_SIZE[1]/2+130)

	widgets.append(saisie1)
	widgets.append(saisie2)
	widgets.append(jouer)
	#widgets.append(retour)
	#widgets.append(quitter_jeu)
	widgets.append(instructions_jeu)
	widgets.append(charger_jeu)

	

def main_menu():
	'''
		fonctions préliminaires au menu principal
	'''

	main_menu_visu()

#Ecran de lancement

logo = canvas.create_image(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, image = logo_imagetk)
fade = rectangle((0, 0), WINDOW_SIZE)
canvas.itemconfig(fade, fill = "")

def process_fade():
	'''
		Gère le dégradé du menu de lancement.
	'''

	global fade
	
	root.after(0, lambda : canvas.itemconfig(fade, fill = "black", stipple = "gray12"))

	root.after(1 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray25"))

	root.after(2 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray50"))

	root.after(3 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = "gray75"))

	root.after(4 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = ""))

	root.after(fade_duration, main_menu)

root.after(fade_delay, process_fade)

#main_menu()

def quitter():
	'''
		Inutile...
	'''
	root.destroy()

def retourner():
	'''
		Retourne au menu principal
	'''
	global playing
	global turn

	#canvas.delete("all")
	playing = False
	turn = False
	tokens_pos.clear()
	tokens_speed.clear()
	tokens_visu.clear()
	is_static.clear()
	delete_widgets()
	root.after(1, main_menu)

def changer_couleurs(): 

	delete_widgets()
	canvas.delete("all")

	vert = tk.Button(canvas, bg = "green", height= 2, width=4)
	vert.place(x=300, y=150,anchor="nw") 
	widgets.append(vert)

	rouge = tk.Button(canvas, bg = "red", height= 2, width=4)
	rouge.place(x=350, y=150,anchor="nw") 
	widgets.append(rouge)

	jaune = tk.Button(canvas, bg = "yellow", height= 2, width=4)
	jaune.place(x=400, y=150,anchor="nw") 
	widgets.append(jaune)

	rose = tk.Button(canvas, bg = "pink", height= 2, width=4)
	rose.place(x=450, y=150,anchor="nw") 
	widgets.append(rose)

	bleu = tk.Button(canvas, bg = "blue", height= 2, width=4)
	bleu.place(x=500, y=150,anchor="nw") 
	widgets.append(bleu)







root.mainloop()
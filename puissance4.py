'''
	Puissance 4

	JOURDAIN Anaïs
	CAICEDO LEMOS Vanessa
	GHARIB ALI BARURA Sama

	Programme réalisé dans le cadre du projet d'IN200
'''

import tkinter as tk
from tkinter import filedialog
import numpy as np
from math import *
import time
from PIL import Image, ImageTk
import random


# Variables globales


# Options
COLOR_PALETTE          = {
	"Red" : "#f63f34",
	"Yellow" : "#efbd20",
	"Cyan" : "#65abaf",
	"Grey" : "#9cafb7",
	"Turquoise" : "#59e38c",
	"Violet" : "#89375F"

}
WINDOW_SIZE            = np.array([700, 600])
BACKGROUND             = "#000650"
GRID_DIMS              = np.array([7, 6])
GRID_POS               = WINDOW_SIZE / 8
GRID_SIZE              = 6*WINDOW_SIZE / 8
SLOT_SIZE              = GRID_SIZE / GRID_DIMS
TOKEN_BOX              = SLOT_SIZE * 4/5
TOKEN_COLLISION_RADIUS = SLOT_SIZE[1] / 2
GRAVITY                = 2
WINNING_STREAK         = 4
NAME_PLAYER_1          = "Turing"
NAME_PLAYER_2          = "Conway"
COLOR_PLAYER_1         = COLOR_PALETTE["Red"]
COLOR_PLAYER_2         = COLOR_PALETTE["Yellow"]
SCORE_PLAYER_1         = 0 
SCORE_PLAYER_2         = 0
N_SET                  = 0

#Visual
root = tk.Tk()
root.geometry(str(WINDOW_SIZE[0]) + 'x' + str(WINDOW_SIZE[1]) + "+0+0")
root.title("Puissance 4")
root.resizable(False, False)

canvas = tk.Canvas(root, width = WINDOW_SIZE[0], height = WINDOW_SIZE[1], bg = BACKGROUND)

canvas.grid()

widgets = [] #Toutes les widget crées doivent être dans cette liste afin de pouvoir les supprimer à chaque changement d'écran

# Listes liées à la création d'un jeton (chaque jeton existant sur le jeu a ces 4 propriétés)
tokens_pos = [] #Position des jetons dans le monde physique
tokens_speed = [] #Vitesse des jetons
tokens_visu = [] #Representation graphique des jetons
is_static = [] #Définit si un jeton est un objet physique ou non

click_time = 0 # Permet d'empêcher le joueur de spammer les cliques

slot_image = Image.open("slot.png") # Image des cases
slot_image = slot_image.resize(np.array(SLOT_SIZE + (1, 1), dtype = int))
slot_imagetk = ImageTk.PhotoImage(slot_image)

logo_image = Image.open("puiss4nce.jpg") # Logo de l'écran de démarrage
logo_image = logo_image.resize(np.array(WINDOW_SIZE, dtype=int))
logo_imagetk = ImageTk.PhotoImage(logo_image)

image_play = Image.open("background.jpeg") # Fond d'écran du menu principal
image_play_tk = ImageTk.PhotoImage(image_play)

image_invaders = Image.open("invader_background.png")   #fond d'écran lorsque le jeu est lancé 
image_invaders = image_invaders.resize(WINDOW_SIZE)
image_invaders_tk = ImageTk.PhotoImage(image_invaders) 
invaders_background = None

image_bouton_pressed = Image.open("boutons/pressed.png")   #image des boutons bleus 
image_bouton_released = Image.open("boutons/rest.png")
image_bouton_hovered = Image.open("boutons/hovered.png")

# Propriétés du fondu sur l'écran de lancement
fade_delay = 1500
fade_duration = 500

#Outils

# Bouton

bouton_model = {
	"position" : np.array((0, 0)),
	"taille" : np.array((100, 30)),
	"texte" : None,
	"image_pressed" : None,
	"image_released" : None,
	"image_hovered" : None,
	"visual" : None,
	"fonction" : None
}
boutons = []


def clicked(bouton):
	'''
		Est appelée lorsque que "bouton" est cliqué.
	'''
	canvas.itemconfig(bouton["visual"], image = bouton["image_pressed"])
	canvas.coords(bouton["texte"], bouton["position"][0],\
	       int(bouton["position"][1]+ bouton["taille"][1]/8))
	root.after(100, lambda: canvas.coords(bouton["texte"], \
				       bouton["position"][0], bouton["position"][1]))
	root.after(100, lambda arg0 = bouton["visual"], \
	    arg1 = bouton["image_released"]: canvas.itemconfig(arg0, image = arg1))
	root.after(200, bouton["fonction"])


def creer_bouton(pos, taille, text = "Appuyez", command = lambda: 
		 print("Button clicked !")):
	'''
		Crée un bouton sur le canvas.
	'''
	nouveau_bouton = bouton_model.copy()
	nouveau_bouton["position"] = pos
	nouveau_bouton["taille"] = taille
	nouveau_bouton["fonction"] = command
	nouveau_bouton["image_pressed"] = ImageTk.PhotoImage \
	(image_bouton_pressed.resize(taille))
	nouveau_bouton["image_released"] = ImageTk.PhotoImage \
	(image_bouton_released.resize(taille))
	nouveau_bouton["image_hovered"] = ImageTk.PhotoImage \
	(image_bouton_hovered.resize(taille))
	nouveau_bouton["visual"] = canvas.create_image(pos[0], pos[1], \
						image = nouveau_bouton["image_released"], anchor = "center")
	nouveau_bouton["texte"] = canvas.create_text(pos[0], pos[1], text = text, \
					      anchor = "center", font = ("Small Fonts", int(taille[1]/3)), \
						  fill = COLOR_PALETTE["Yellow"])

	boutons.append(nouveau_bouton)


def hover_boutons(event):
	'''
		Change l'image du boutons qui est en dessous du curseur de la souris.
	'''

	for b in boutons:
		if event.x > b["position"][0] - b["taille"][0]/2 and\
		   event.x < b["position"][0] + b["taille"][0]/2 and\
		   event.y > b["position"][1] - b["taille"][1]/2 and\
		   event.y < b["position"][1] + b["taille"][1]/2:

		   canvas.itemconfig(b["visual"], image = b["image_hovered"])
		else:
		   canvas.itemconfig(b["visual"], image = b["image_released"])


def click_boutons(event):
	'''
		Vérifie si un est sur un bouton.
	'''

	for b in boutons:
		if event.x > b["position"][0] - b["taille"][0]/2 and\
		   event.x < b["position"][0] + b["taille"][0]/2 and\
		   event.y > b["position"][1] - b["taille"][1]/2 and\
		   event.y < b["position"][1] + b["taille"][1]/2:

		   clicked(b)
		   return True
		

# Fonctions permettant d'utiliser des tableaux numpy 1x2 (Vecteurs) pour créer des formes
def rectangle(pos, size):
	'''
		Retourne l'id tkinter d'un rectangle dont le côté supérieur gauche est à "pos" et qui mesure "size".
	'''
	return canvas.create_rectangle(pos[0], pos[1], pos[0] + size[0], 
				pos[1] + size[1])


def oval(pos, size):
	'''
		Retourne l'id tkinter de l'oval inscrit dans le rectangle dont le point supérieur gauche est à "pos" et qui mesure "size"
	'''
	oval = canvas.create_oval(pos[0], pos[1], pos[0] + size[0], \
			   pos[1] + size[1], width = 0, fill = "red")
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

	boutons.clear()
	for i in range(len(widgets)):
		widgets[i].place_forget()
	widgets.clear()


def raycast(o_start, stride, nbr = WINNING_STREAK):
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

	for i in range(nbr):

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
	'''
		Sauvegarde une partie de puissance 4 dans le fichier situé à "path" sur le
		disque dur de l'utilisateur.
	'''

	try:
		out = open(path, "w")

		out.write(str(GRID_DIMS[0]) + ";" + str(GRID_DIMS[1]) + ";\n") # On commence par écrire le nombre de colonnes et le nombre de lignes

		# On sauvegarde les propriétés de chaque jeton

		for i in range(len(tokens_pos)):

			out.write(str(tokens_pos[i][0]) + ";" + str(tokens_pos[i][1]) + ";" + \
	     str(tokens_speed[i][0]) + ";" + str(tokens_speed[i][1]) + ";" + \
		 str(int(is_static[i])) + ";" + \
		 canvas.itemcget(tokens_visu[i], "fill")  + ";" + "\n")

		out.close()

		return True
	
	except: # Si le "path" n'est pas valide.
		return False


def load(path):
	'''
		Charge une partie à partir du fichier situé à "path" sur le disque dur de l'utilisateur
	'''

	global COLOR_PLAYER_1
	global COLOR_PLAYER_2
	global SLOT_SIZE
	global GRID_DIMS
	global slot_image
	global slot_imagetk

	try:
		inn = open(path, "r")

		def_color = 0

		header = True # Header devient false lorsque les paramètres de la partie ont étés chargés
		reading = True
		while reading:
			
			line = inn.readline()

			if line and header: # On charge les paramètres de la partie (Pour l'instant il ne s'agit que des dimensions de la grille)
				buffer = ""
				step = 0

				for c in line:
					if c == ";":
						GRID_DIMS[step] = int(buffer)
						buffer = ""
						step += 1
					else:
						buffer += c

				header = False

				SLOT_SIZE = GRID_SIZE / GRID_DIMS

				slot_image = slot_image.resize((int(SLOT_SIZE[0]), int(SLOT_SIZE[1])))
				slot_imagetk = ImageTk.PhotoImage(slot_image)

			elif line: # On charge un jeton
				
				buffer = ""
				phase = 0

				for c in line:

					if c == ";":
						if phase == 0:
							tokens_pos.append(np.array([float(buffer), 0])) # La première donnée rencontrée est la position x
						elif phase == 1:
							tokens_pos[-1][1] = float(buffer) # Puis il s'agit de la position y
						elif phase == 2:
							tokens_speed.append(np.array([float(buffer), 0])) # Ensuite la vitesse x
						elif phase == 3:
							tokens_speed[-1][1] = float(buffer) # Suite à quoi on trouve la vitesse y
						elif phase == 4:
							is_static.append(bool(buffer)) # Suivie par le bit décidant si le jeton est fixé ou non
						elif phase == 5: # Pour enfin charger la couleur du jeton
							oval((0, 0), (100, 100))
							visu = oval(tokens_pos[-1], SLOT_SIZE)
							canvas.itemconfig(visu, fill = buffer)
							tokens_visu.append(visu)

							if def_color == 0:
								COLOR_PLAYER_1 = buffer
								def_color += 1
							elif def_color == 1 and buffer != COLOR_PLAYER_1:
								COLOR_PLAYER_2 = buffer

						phase += 1
						buffer = ""
						continue

					buffer += c
			else:
				reading = False

		inn.close()

		return True # La lecture du fichier s'est bien passée
	except:
		return False # Le fichier n'a pas pu être lu.


def launch_load(): #fonction qui permet de charger une partie
	'''
		Charge une partie puis la lance.
	'''

	delete_widgets()

	path = filedialog.askopenfilename()
	if load(path):
		root.after(1, game)
		root.after(100, lambda: canvas.lower(invaders_background))
	else:
		widgets.append(tk.Label(canvas, text = "Erreur : Le fichier \"" + \
			  str(path) + "\" n'a pas pu être chargé !", fg = "red"))
		widgets.append(tk.Button(canvas, text = "OK", command = retourner))
		widgets[-2].place(x = 10, y = 10)
		widgets[-1].place(x = 10, y = 50)


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


def game_clicks(event):
	'''
		Gère les cliques lorsque le jeu tourne
	'''

	global turn
	global click_time
	global NAME_PLAYER_1
	global NAME_PLAYER_2
	global GRID_SIZE
	global invaders_background

	if click_boutons(event):
		return

	if event.x <= GRID_POS[0] or event.x >= GRID_POS[0] + GRID_SIZE[0]:
		return # Si le clique est en dehors de la grille, on ne crée pas de jeton
	
	pos = np.array((GRID_POS[0] + SLOT_SIZE[0] * 
		 int((event.x - GRID_POS[0])/SLOT_SIZE[0]),GRID_POS[1] - SLOT_SIZE[1])) # On met le jeton dans la bonne colonne

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

	canvas.lower(invaders_background)

	if turn:
		canvas.itemconfig(visu, fill = COLOR_PLAYER_1)
		widgets[0]["text"] = "Au tour de : " + NAME_PLAYER_2
	else:
		canvas.itemconfig(visu, fill = COLOR_PLAYER_2)
		widgets[0]["text"] = "Au tour de : " + NAME_PLAYER_1

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

	# On supprime le dernier élément de chaque liste liée à la création d"un jeton
	canvas.delete(tokens_visu[-1])
	tokens_pos.pop()
	tokens_speed.pop()
	tokens_visu.pop()
	is_static.pop()
	turn = not turn


def nouvelle_manche():
	'''
		Lance une nouvelle manche.
	'''
	for i in range (len(tokens_visu)):
		canvas.delete(tokens_visu[i])
	tokens_pos.clear()
	tokens_speed.clear()
	tokens_visu.clear()
	is_static.clear()


def jeu_set_match(N_SET):
	'''
		Montre quel joueur remporte le set.
	'''
	if SCORE_PLAYER_1 > (N_SET/2):
		widgets.append(tk.Label(canvas, text = str(NAME_PLAYER_1) + \
			   " emporte le set!", font = ("Small Fonts", 15), bg = "white"))
		widgets[-1].place(relx = 0.5, y = 90, anchor='center')
	elif SCORE_PLAYER_2 > (N_SET/2):
		widgets.append(tk.Label(canvas, text = str(NAME_PLAYER_2) + \
			   " emporte le set!", font = ("Small Fonts", 15), bg = "white"))
		widgets[-1].place(relx = 0.5, y = 90, anchor='center')


def game_physics():
	'''
		Comportement physique des jetons (gravité, rebonds et collisions)
	'''

	global playing
	global WINNING_STREAK
	global SCORE_PLAYER_1
	global SCORE_PLAYER_2
	global N_SET

	try:
		if turn:
			widgets[0]["text"] = "Au tour de : " + NAME_PLAYER_2
		else:
			widgets[0]["text"] = "Au tour de : " + NAME_PLAYER_1
	except:
		pass

	for i in range(len(tokens_pos)):

		if is_static[i]:
			continue # Nous n'appliquons pas le comportement physique à un jeton statique

		collides_another = False

		for j in range(len(tokens_pos)):
			if i==j or tokens_pos[j][1] < tokens_pos[i][1]:
				continue # On évite de tester si le jeton se collisione lui même ou avec un jeton plus haut


			if tokens_pos[i][0] > tokens_pos[j][0] + SLOT_SIZE[0]-1 or \
			tokens_pos[i][0] + SLOT_SIZE[0]-1 < tokens_pos[j][0]:
				pass
			elif tokens_pos[i][1] + SLOT_SIZE[1] + \
			tokens_speed[i][1] > tokens_pos[j][1] + tokens_speed[j][1]:
				collides_another = True
				break
			

		# Si le jeton ne collisionne ni un autre jeton, ni le bas de la grille
		if not collides_another and tokens_pos[i][1] + tokens_speed[i][1] \
		+ SLOT_SIZE[1] <= GRID_POS[1] + GRID_SIZE[1]:
			tokens_pos[i] += tokens_speed[i]
		else: # Sinon
			tokens_speed[i][1] = -1/3 * tokens_speed[i][1]
			if abs(tokens_speed[i][1]) < 1: # Si la vitesse absolue du jeton est trop faible, on met sa position à la case la plus proche (évite qu'un jeton ne soit entre deux cases)
				tokens_pos[i][1] = GRID_POS[1] + SLOT_SIZE[1] * \
				int( (tokens_pos[i][1] - GRID_POS[1]) /SLOT_SIZE[1])


				is_static[i] = True # On fixe le jeton

				# On lance les différents rayons pour compter le nombre de jetons autour


				horiz = raycast(tokens_pos[i] + SLOT_SIZE/2, (SLOT_SIZE[0], 0))\
				+ raycast(tokens_pos[i] + SLOT_SIZE/2, (-SLOT_SIZE[0], 0)) - 1
				verti = raycast(tokens_pos[i] + SLOT_SIZE/2, (0, SLOT_SIZE[1]))\
				+ raycast(tokens_pos[i] + SLOT_SIZE/2, (0, -SLOT_SIZE[1])) - 1
				diag1 = raycast(tokens_pos[i] + SLOT_SIZE/2, (SLOT_SIZE[0], SLOT_SIZE[1]))\
				+ raycast(tokens_pos[i] + SLOT_SIZE/2, (-SLOT_SIZE[0], -SLOT_SIZE[1])) - 1
				diag2 = raycast(tokens_pos[i] + SLOT_SIZE/2, (SLOT_SIZE[0], -SLOT_SIZE[1]))\
				+ raycast(tokens_pos[i] + SLOT_SIZE/2, (-SLOT_SIZE[0], SLOT_SIZE[1])) - 1

				
				# Dans le cas où il y a assez de jetons alignés pour un puissance 4 :
				if horiz >= WINNING_STREAK or verti >= WINNING_STREAK or diag1 >= WINNING_STREAK or diag2 >= WINNING_STREAK:
					if turn == True:
						widgets.append(tk.Label(canvas, text = "Victoire pour : ", \
			      fg="red", font=("Small Fonts", 25), bg="white"))
						widgets[-1].place(x=10,y=180)

						widgets.append(tk.Label(canvas, text=NAME_PLAYER_1 + " !!", \
			      fg="red", font=("Small Fonts", 21), bg="white"))
						widgets[-1].place(x=10, y=240)
						SCORE_PLAYER_1+=1
					else: 
						widgets.append(tk.Label(canvas, text = "Victoire pour : ", \
			       fg="red", font=("Small Fonts", 25), bg="white"))
						widgets[-1].place(x=10,y=180)

						widgets.append(tk.Label(canvas, text=NAME_PLAYER_2 + " !!", \
			      fg="red", font=("Small Fonts", 21), bg="white"))
						widgets[-1].place(x=10, y=240)

						SCORE_PLAYER_2+=1					
					if N_SET!=0: # Si l'utilisateur a décidé de jouer un set (plusieurs manches)
						widgets.append(tk.Label(canvas, text = " SCORE: " + str(SCORE_PLAYER_1) + \
			       " - " +  str(SCORE_PLAYER_2) + " ", font = ("Small Fonts", 18), \
					  highlightthickness=3, highlightbackground = "white", bg = "white"))
						widgets[-1].place(relx = 0.5, y = 120, anchor='center')

						jeu_set_match(N_SET)
						if SCORE_PLAYER_1 or SCORE_PLAYER_2 < (N_SET/2): #Si personne emporte le set, on commence une nouvelle manche
							root.after(2500, nouvelle_manche)

		tokens_speed[i][1] += GRAVITY
		set_pos(tokens_visu[i], tokens_pos[i], SLOT_SIZE)
	
	if playing:
		root.after(int(1000/60), game_physics)


def game_visu():
	'''
		Crée les widgets et la grille du jeu
	'''
	global SCORE_PLAYER_1
	global SCORE_PLAYER_2
	global invaders_background

	invaders_background = canvas.create_image(0, 0, 
					   image = image_invaders_tk, anchor = "nw")


	for y in range(GRID_DIMS[1]):
		for x in range(GRID_DIMS[0]):
			#oval((x, y) * SLOT_SIZE + GRID_POS, SLOT_SIZE)
			create_slot((x, y) * SLOT_SIZE + GRID_POS)

	turn_info = tk.Label(canvas, font = ("Small Fonts", WINDOW_SIZE[1]//20),
		       bg = "white")

	if turn == 0:
		turn_info["text"] = NAME_PLAYER_1 + " commence !"
	else:
		turn_info["text"] = NAME_PLAYER_2 + " commence !"

	turn_info.place(x = 10, y = 10)

	widgets.append(turn_info)
	widgets.append(tk.Button(text = "Annuler le dernier jeton", \
			  font = ("Small Fonts", 12), command = annul_jeton))
	widgets[-1].place(x = int(WINDOW_SIZE[0] - 200), y = 10)
	widgets.append(tk.Button(text = "Sauvegarder", font = ("Small Fonts", 12), \
			   command = lambda: save(filedialog.asksaveasfilename())))
	widgets[-1].place(x = int(WINDOW_SIZE[0] / 2), y = int(WINDOW_SIZE[1] - 40))

	if N_SET != 0:
		widgets.append(tk.Label(canvas, text = "Set à " + str(N_SET) + " manches", \
			  font = ("Small Fonts", 14), bg = "white"))
		widgets[-1].place(relx = 0.5, y = 60, anchor='center')


def game():
	'''
		Initialisation du jeu
	'''
	global tokens_visu

	colors_copy = []
	for e in tokens_visu:
		colors_copy.append(canvas.itemcget(e, "fill"))

	canvas.delete("all")
	delete_widgets()
	tokens_visu.clear()
	for i in range(len(colors_copy)):
		tokens_visu.append(oval(tokens_pos[i], SLOT_SIZE))
		canvas.itemconfig(tokens_visu[-1], fill = colors_copy[i])

	global playing
	global turn

	playing = True
	turn=random.randint(0,1)
	canvas.bind("<Button-1>", game_clicks)
	root.bind("<Key>", game_keys)
	game_visu()
	root.after(1, game_physics)


# fonction qui affiche les infos supplémentaires sur le projet 
def credits():
	'''
		Montre le menu "credits"
	'''
	global widgets

	delete_widgets()
	canvas.delete("all")

	canvas.create_image(0, 0, anchor = "nw", image = image_invaders_tk)

	credits_font = ("Small Fonts", 20)
	credits_font_title = ("Small Fonts", 38, "bold")
	credits_font_subtitle = ("Small Fonts", 24, "bold")

	widgets = [
		tk.Label(root, text = "Puissance 4 S2", fg="white", font = credits_font_title),
		tk.Label(root, text = "Auteurs : ", fg="white", font = credits_font_subtitle),
		tk.Label(root, text = "JOURDAIN Anaïs\n\
CAICEDO LEMOS Vanessa\n\
GHARIB ALI BARURA Sama", fg="white",font = credits_font),
		tk.Label(root, text = "LDDBI", fg="white", font = credits_font_subtitle),
		tk.Label(root, text = "Projet réalisé dans le cadre du module IN200", \
	   fg="white", font = credits_font)
	]

	for i in range(len(widgets)):
		widgets[i]["bg"] = BACKGROUND
		widgets[i].place(x = WINDOW_SIZE[0]/2, y = 100 + i * 100,
		    anchor = "center")

#Menu principal

def main_menu_visu():
	'''
		Crée les widgets du menu principal
	'''

	canvas.delete("all")

	canvas.bind("<Button-1>", click_boutons)
	canvas.bind("<Motion>", hover_boutons)

	canvas.create_image(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2, image=image_play_tk)

	font_size = int(WINDOW_SIZE[1]/23)
	
	canvas.create_text(WINDOW_SIZE[0]/2, 100, text="PUISSANCE 4",\
		    fill="#efbd20", font=("Small Fonts", 50))
	canvas.pack()

	# Fonction qui affiche les instructions dans une nouvelle fenêtre

	def instructions():
		'''
			Montre les instructions de jeu
		'''
		delete_widgets()
		canvas.delete("all")

		global widgets

		widgets = [
			tk.Label(root, text = "Instructions:", fg="#efbd20", \
	     font=("Small Fonts", 25, "bold")),
			tk.Label(root, text = "Pour mettre un jeton cliquez sur la colonne souhaitée.", \
	    fg="white", font=("Small Fonts", 19)),
			tk.Label(root, text = \
	    "BUT: positionner 4 jetons de la même couleur consécutivement",\
	    fg="white",font=("Small Fonts", 18)), 
			tk.Label(root, text = "(horizontalement, verticalement ou diagonalement)",\
	     fg="white", font = ("Small Fonts", 19)),
		  tk.Label(root, text = "À vous de jouer !", fg="white",\
	      font = ("Small Fonts", 23, "bold"))
		]

		for i in range(len(widgets)):
			widgets[i]["bg"] = BACKGROUND
			widgets[i].place(x = WINDOW_SIZE[0]/2, y = 100 + i * 90, anchor = "center")


	# Boutons du menu principal 

	quitter_jeu=tk.Button(canvas,text="QUITTER",fg="red",
		       font = ("Small Fonts", 15), command = quitter)
	quitter_jeu.place(x=WINDOW_SIZE[0]-110, y=WINDOW_SIZE[1]-50)

	retour = tk.Button(canvas, text="RETOURNER AU MENU PRINCIPAL", 
		    font = ("Small Fonts", 12), command = retourner)
	retour.place(x=25, y=WINDOW_SIZE[1]-50)

	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/5 + 100), (150, 50),\
	       text = "Jouer", command = game)
	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/5 + 160), (150, 50),\
	      text = "Options", command = menu_perso_jeu)
	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/5 + 220), (150, 50),\
	      text = "Credits", command = credits)
	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/5 + 280), (150, 50), \
	      text = "Charger", command = launch_load)
	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/5 + 340), (150, 50),\
	      text = "Instructions", command = instructions)

def main_menu():
	'''
		Fonctions préliminaires au menu principal
	'''
	main_menu_visu()

#Ecran de lancement

logo = canvas.create_image(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, image = logo_imagetk)
fade = rectangle((0, 0), WINDOW_SIZE)
canvas.itemconfig(fade, fill = "")


def process_fade():
	'''
		Gère le dégradé de l'écran de lancement.
	'''

	global fade
	
	root.after(0, lambda : canvas.itemconfig(fade, fill = "black", \
					  stipple = "gray12"))

	root.after(1 * fade_duration // 5, lambda : canvas.itemconfig \
	    (fade, stipple = "gray25"))

	root.after(2 * fade_duration // 5, lambda : canvas.itemconfig \
	    (fade, stipple = "gray50"))

	root.after(3 * fade_duration //5, lambda : canvas.itemconfig \
	    (fade, stipple = "gray75"))

	root.after(4 * fade_duration //5, lambda : canvas.itemconfig \
	    (fade, stipple = ""))

	root.after(fade_duration, main_menu)

root.after(fade_delay, process_fade)


#Main_menu

def quitter():
	root.destroy()


def retourner():
	'''
		Retourne au menu principal
	'''
	global playing
	global turn

	playing = False
	turn = False
	tokens_pos.clear()
	tokens_speed.clear()
	tokens_visu.clear()
	is_static.clear()
	canvas.unbind("<Button-1>")
	delete_widgets()
	root.after(1, main_menu)


# Menu personnalisation 

def menu_perso_jeu():
	'''
		Menu avec pour modifier/personnaliser le jeu avant de commencer
	'''

	global widgets

	canvas.delete("all")
	delete_widgets()

	widgets = [tk.Label (canvas, text = "Options", font = ("Small Fonts", 32),fg="#efbd20", bg=BACKGROUND)]
	widgets[0].place(x = WINDOW_SIZE[0]/2, y = 100, anchor = "center")
	# tous les boutons pour modifier les paramètres 
	creer_bouton((WINDOW_SIZE[0]/2, 200), (200, 50), \
	      text = "Player names", command = player_name_menu)
	creer_bouton((WINDOW_SIZE[0]/2, 260), (200, 50), \
	      text = "Grid dimensions", command = grid_dimensions_menu)
	creer_bouton((WINDOW_SIZE[0]/2, 320), (200, 50), \
	      text = "Tokens color", command = tokens_color_menu)
	creer_bouton((WINDOW_SIZE[0]/2, 380), (200, 50), \
	      text = "Winning streak", command = winning_streak_menu)
	creer_bouton((WINDOW_SIZE[0]/2, 440), (200, 50), \
	      text = "Set/Match", command = jeu_set_match_menu)


def player_name_menu():
	'''
		Montre le menu pour changer les noms des joueurs
	'''
	
	global widgets

	canvas.delete("all")
	delete_widgets()

	def validate_names():
		global NAME_PLAYER_1
		global NAME_PLAYER_2
		global widgets

		NAME_PLAYER_1 = widgets[1].get()
		NAME_PLAYER_2 = widgets[2].get()

		root.after(1, retourner)

	#widgets pour insérer les noms des joueurs 

	widgets = [
		tk.Label (canvas, text = "Veuillez saisir vos noms", fg="#efbd20", \
	    font = ("Small Fonts", 30, "bold"), bg=BACKGROUND),
		tk.Entry(canvas, font = ("Small Fonts", 25), highlightthickness=5, \
	    highlightbackground = "white", bg = "white"),
		tk.Entry(canvas, font = ("Small Fonts", 25), highlightthickness=5, \
	   highlightbackground = "white", bg = "white") ,
	]
	widgets[0].place(x = WINDOW_SIZE[0]/2, y = WINDOW_SIZE[1]/4, anchor = "n")
	widgets[1].insert(0, NAME_PLAYER_1)
	widgets[2].insert(0, NAME_PLAYER_2)
	
	for i in range(1, 3):
		widgets[i].place(relx = 0.25, y = WINDOW_SIZE[1]/4 + i * 66)

	
	creer_bouton((WINDOW_SIZE[0]/2, WINDOW_SIZE[1] * 5/8), (150, 80), 
	      text = "Valider", command = validate_names)


def grid_dimensions_menu(): #menu pour choisisr les dimensions de la grille 
	'''
		Menu pour changer les dimensions de la grille
	'''


	global GRID_DIMS
	global SLOT_SIZE
	global widgets
	global slot_image
	global slot_imagetk

	canvas.delete("all")
	delete_widgets()
	

	def validate_dims():
		global GRID_DIMS
		global SLOT_SIZE
		global widgets
		global slot_image
		global slot_imagetk

		try:
			GRID_DIMS[0] = int(widgets[0]["text"])
			GRID_DIMS[1] = int(widgets[1]["text"])
		except:
			GRID_DIMS[0] = 7
			GRID_DIMS[1] = 6

		SLOT_SIZE = GRID_SIZE / GRID_DIMS

		slot_imagetk = ImageTk.PhotoImage(slot_image.resize((int(SLOT_SIZE[0]), \
						       int(SLOT_SIZE[1]))))

		root.after(1, retourner)


	widgets.append(tk.Label(canvas, text = str(GRID_DIMS[0]), \
			 font = ("Small Fonts", 15), highlightthickness=3, \
	    	 highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(x = 430, y = 175)

	widgets.append(tk.Label(canvas, text = str(GRID_DIMS[1]), \
			 font = ("Small Fonts", 15), highlightthickness=3, \
	    	  highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(x = 430, y = 225)

	def add_figure(index, fig):
		widgets[index]["text"] += fig
	def remove_figure(index):
		if len(widgets[index]["text"]) > 0:
			widgets[index]["text"] = widgets[index]["text"] \
			[:len(widgets[index]["text"]) - 1]

	# Clavier de saisie
	for i in range(2):
		for j in range(10):
			creer_bouton((55 + j * 50, 295 + i * 50), (50, 50), \
		 text = str(j), command = lambda arg0 = i, \
		 arg1 = j: add_figure(arg0, str(arg1)))

	widgets.append(tk.Label(canvas,\
			  text =" Choix de la longueur de la grille :", \
			  font = ("Small Fonts", 15), highlightthickness=3, \
	    	  highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(x = 120, y = 175)

	widgets.append(tk.Label(canvas, \
			  text = "  Choix de la hauteur de la grille :  ", \
			  font = ("Small Fonts", 15), highlightthickness=3, \
	    	  highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(x = 120, y = 225)

	widgets.append(tk.Label(canvas,text="Veuillez entrer les tailles",  \
			 fg="#efbd20",font = ("Small Fonts", 28), bg=BACKGROUND))
	widgets[-1].place(relx = 0.5, y=50, anchor = "center")

	widgets.append(tk.Label(canvas,text="que vous souhaitez",\
			  fg="#efbd20", font = ("Small Fonts", 28), bg=BACKGROUND))
	widgets[-1].place(relx = 0.5, y=100, anchor = "center")

	widgets.append(tk.Button(canvas, text = "Remove figure", \
			  font = ("Small Fonts", 12), command = lambda: remove_figure(0)))
	widgets[-1].place(x = 550, y = 275)

	widgets.append(tk.Button(canvas, text = "Remove figure", \
			  font = ("Small Fonts", 12), command = lambda: remove_figure(1)))
	widgets[-1].place(x = 550, y = 325)

	widgets.append(tk.Button(canvas, text = "Valider", \
			  font = ("Small Fonts", 28), command = validate_dims))
	widgets[-1].place(relx = 0.5, y = 450, anchor = "center")


def tokens_color_menu():  # menu pour choisir la couleur des jetons 
	'''
		Menu pour changer les couleurs des joueurs
	'''

	global COLOR_PLAYER_1
	global COLOR_PLAYER_2

	canvas.delete("all")
	delete_widgets()
	
	# carré pour montrer quelles couleurs ont été choisies
	widgets.append(tk.Canvas(canvas, width = 25, height = 25, \
			  bg = COLOR_PLAYER_1, relief = "flat", bd = 10))
	widgets[-1].place(x = 175, y = 200)
	widgets.append(tk.Canvas(canvas, width = 25, height = 25, \
			  bg = COLOR_PLAYER_2, relief = "flat", bd = 10))
	widgets[-1].place(x = 175, y = 350)

	def validate_colors():
		global COLOR_PLAYER_1
		global COLOR_PLAYER_2

		COLOR_PLAYER_1 = widgets[0]["bg"]
		COLOR_PLAYER_2 = widgets[1]["bg"]

		root.after(1, retourner)

	def change_color(index, color_index):
		widgets[index]["bg"] = COLOR_PALETTE[list(COLOR_PALETTE.keys())[color_index]]

	for i in range(2):
		for j in range(len(list(COLOR_PALETTE.keys()))):  #pour créer la liste des propositions de couleurs pour les joueurs 
			widgets.append(tk.Button(canvas, relief = "sunken", \
			     bd = 8, bg = COLOR_PALETTE[list(COLOR_PALETTE.keys())[j]],\
				 command = lambda arg0 = i, arg1 = j: change_color(arg0, arg1)))
			widgets[-1].place(x = 265 + j * 48, y = 200 + i * 150)

	widgets.append(tk.Label(canvas, text = "COULEURS", fg="#efbd20", \
			 font = ("Small Fonts", 45, "bold"), bg=BACKGROUND))
	widgets[-1].place(x = WINDOW_SIZE[0]/2, y = 20, anchor = "n")

	widgets.append(tk.Label(canvas, text = "Couleur pour player 1 :", \
			 font = ("Small Fonts", 24), highlightthickness=3, \
	    	 highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(relx = 0.5, y = 150, anchor = "center")

	widgets.append(tk.Label(canvas, text = "Couleur pour player 2 :", \
			 font = ("Small Fonts", 24), highlightthickness=3, \
	    	 highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(relx = 0.5, y = 300, anchor = "center")

	widgets.append(tk.Button(canvas, text = "Valider", font = ("Small Fonts", 25), \
			   command = validate_colors))
	widgets[-1].place(relx = 0.5, y = 470, anchor = "center")


def winning_streak_menu():  # menu pour le choix du nombre de jeton gagnants 
	'''
		Menu pour changer le nombre de jetons nécessaire pour faire un puissance 4.
	'''

	global WINNING_STREAK

	canvas.delete("all")  # pour suppprimer tous les autres canvas 
	delete_widgets()

	widgets.append(tk.Label(canvas, text = str(WINNING_STREAK), \
			 font = ("Small Fonts", 20), highlightthickness=3, \
	    	 highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[0].place(x = 450, y = 130)


	def validate_winning_streak():
		global WINNING_STREAK

		try:
			WINNING_STREAK = int(widgets[0]["text"])
		except:
			WINNING_STREAK = 4

		root.after(1, retourner)

	def add_figure(fig):
		widgets[0]["text"] += fig

	def remove_figure():
		if len(widgets[0]["text"]) > 0:
			widgets[0]["text"] = widgets[0]["text"][:len(widgets[0]["text"]) - 1]

	# Clavier de saisie
	for j in range(10):
		
		if j != 9:
			creer_bouton((300 + (j%3) * 50, 220 + int(j/3) * 50), (50, 50), text = str(j),
		 command = lambda arg = j: add_figure(str(arg)))
		else:
			creer_bouton((300 + 50, 220 + int(j/3) * 50), (50, 50), text = '9',
		 command = lambda: add_figure('9'))

	widgets.append(tk.Label(canvas, text = "NOMBRE DE JETONS POUR GAGNER", fg="#efbd20", \
			 font = ("Small Fonts", 25, "bold"), bg=BACKGROUND))
	widgets[-1].place(x = WINDOW_SIZE[0]/2, y = 40, anchor = "n")

	widgets.append(tk.Button(canvas, text = "Remove figure", \
			  font = ("Small Fonts", 12), command = lambda: remove_figure()))
	widgets[-1].place(x = 510, y = 250)

	widgets.append(tk.Label(text="Vous avez choisi : ", \
			 font=("Small Fonts", 20), highlightthickness=3, \
	    	 highlightbackground = "white", bg = BACKGROUND, fg = "white"))
	widgets[-1].place(x = 200, y = 130)

	widgets.append(tk.Label(text = "Veuillez choisir un nombre qui est en accord ", \
			  fg = "#efbd20", font = ("Small Fonts", 12), bg=BACKGROUND))
	widgets[-1].place(relx = 0.5, y = WINDOW_SIZE[1] - 120, anchor = "center")

	widgets.append(tk.Label(text="avec la taille de votre grille ", \
			 fg="#efbd20", font=("Small Fonts", 12), bg=BACKGROUND))
	widgets[-1].place(relx=0.5, y = WINDOW_SIZE[1] - 95, anchor = "center")


	widgets.append(tk.Button(canvas, text = "Valider", \
			  font = ("Small Fonts", 15), command = validate_winning_streak))
	widgets[-1].place(relx = 0.5, y = 440, anchor = "center")


def jeu_set_match_menu():  # menu pour le choix du nombre de set 
	'''
		Menu pour choisir le nombre de set à gagner pour gagner un match
	'''

	global N_SET
	canvas.delete("all")
	delete_widgets()

	widgets.append(tk.Label(canvas,text = "Choisissez le nombre de set: ", \
			 fg ="#efbd20", font = ("Small Fonts", 25), bg = BACKGROUND))
	widgets[-1].place(relx = 0.5, y = 250, anchor = "center")


	def set_3():   #3 set
		global N_SET
		N_SET = 3
		retourner()


	def set_5():	#5 set 
		global N_SET
		N_SET = 5
		retourner()


	def set_7():	#7 set 
		global N_SET
		N_SET = 7
		retourner()

	set3 = tk.Button(canvas, text = "3", font = ("Small Fonts", 25), \
		  command = set_3)
	widgets.append(set3)
	set3.place(x = 265, y = 300)

	set5 = tk.Button(canvas, text = "5", font = ("Small Fonts", 25), \
		  command = set_5)
	widgets.append(set5)
	set5.place(x = 325, y = 300)

	set7 = tk.Button(canvas, text = "7", font = ("Small Fonts", 25), \
		  command = set_7)
	widgets.append(set7)
	set7.place(x = 385, y = 300)
	


root.mainloop()
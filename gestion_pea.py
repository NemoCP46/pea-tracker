from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime

# Config de CustomTkinter
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")

# Création de la fenêtre principale
root = customtkinter.CTk()
root.title("Gestion PEA")
root.geometry("1000x600")

# --- Variables ---
investissements = []
dates = []
pea_values = []
current_file = None

# --- Fonctions Menu ---
def nouveau_fichier():
    global investissements, dates, pea_values, current_file
    investissements = []
    dates = []
    pea_values = []
    current_file = None
    # Effacer le tableau
    for item in tableau.get_children():
        tableau.delete(item)
    # Effacer le graphique
    ax.clear()
    canvas.draw()
    # Réinitialiser l'affichage de l'investissement total et du rendement
    label_invest_total.configure(text="Investissement total: 0.00 €")
    label_rendement.configure(text="Rendement: 0.00 € (0.00%)")
    root.title("Gestion PEA - Nouveau fichier")

def ouvrir():
    global investissements, dates, pea_values, current_file
    filename = filedialog.askopenfilename(
        title="Ouvrir un fichier",
        filetypes=[("Fichiers PEA", "*.pea"), ("Tous les fichiers", "*.*")]
    )
    if filename:
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            
            # Effacer les données actuelles
            investissements = []
            dates = []
            pea_values = []
            
            # Effacer le tableau
            for item in tableau.get_children():
                tableau.delete(item)
            
            # Charger les nouvelles données
            for item in data:
                dates.append(item['date'])
                investissements.append(item['investissement'])
                pea_values.append(item['valeur_pea'])
                tableau.insert("", "end", values=(item['date'], item['investissement'], item['valeur_pea']))
            
            current_file = filename
            update_graph()
            update_investissement_total()
            update_rendement()
            root.title(f"Gestion PEA - {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")

def enregistrer():
    if current_file:
        sauvegarder_sous(current_file)
    else:
        sauvegarder_sous()

def sauvegarder_sous(filename=None):
    global current_file
    if not filename:
        filename = filedialog.asksaveasfilename(
            title="Enregistrer le fichier",
            defaultextension=".pea",
            filetypes=[("Fichiers PEA", "*.pea"), ("Tous les fichiers", "*.*")]
        )
    
    if filename:
        try:
            data = []
            for i in range(len(dates)):
                data.append({
                    'date': dates[i],
                    'investissement': investissements[i],
                    'valeur_pea': pea_values[i]
                })
            
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
            
            current_file = filename
            root.title(f"Gestion PEA - {filename}")
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {str(e)}")

def set_theme(theme):
    if theme == "White":
        customtkinter.set_appearance_mode("light")
        tableau.configure(style="Treeview")
        root.configure(bg="white")
        # Mettre à jour le graphique pour le mode clair
        update_graph()
    else:
        customtkinter.set_appearance_mode("dark")
        tableau.configure(style="Dark.Treeview")
        root.configure(bg="#2b2b2b")
        update_table_style_dark()
        # Mettre à jour le graphique pour le mode sombre
        update_graph()

# --- Ajout Menu ---
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Nouveau", command=nouveau_fichier)
filemenu.add_command(label="Ouvrir", command=ouvrir)
filemenu.add_command(label="Enregistrer", command=enregistrer)
filemenu.add_command(label="Enregistrer sous", command=sauvegarder_sous)
menubar.add_cascade(label="Fichier", menu=filemenu)

colormenu = Menu(menubar, tearoff=0)
colormenu.add_command(label="White", command=lambda: set_theme("White"))
colormenu.add_command(label="Black", command=lambda: set_theme("Black"))
menubar.add_cascade(label="Couleur", menu=colormenu)

root.config(menu=menubar)

# --- Frame gauche pour les entrées ---
frame_gauche = customtkinter.CTkFrame(root, width=300)
frame_gauche.pack(side=LEFT, fill=Y, padx=10, pady=10)

Label(frame_gauche, text="Date").pack(pady=5)
entry_date = DateEntry(frame_gauche, width=20)
entry_date.pack(pady=5)

Label(frame_gauche, text="Investissement (€)").pack(pady=5)
entry_invest = customtkinter.CTkEntry(frame_gauche)
entry_invest.pack(pady=5)

Label(frame_gauche, text="Valeur PEA (€)").pack(pady=5)
entry_pea = customtkinter.CTkEntry(frame_gauche)
entry_pea.pack(pady=5)

# --- Frame pour tableau et boutons ---
frame_table = customtkinter.CTkFrame(frame_gauche)
frame_table.pack(pady=20)

# Boutons
def ajouter_ligne():
    try:
        date = entry_date.get()
        invest = float(entry_invest.get())
        pea = float(entry_pea.get())
        dates.append(date)
        investissements.append(invest)
        pea_values.append(pea)
        tableau.insert("", "end", values=(date, invest, pea))
        update_graph()
        update_investissement_total()
        update_rendement()
        
        # Effacer les champs après ajout
        entry_invest.delete(0, END)
        entry_pea.delete(0, END)
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")

def modifier_ligne():
    selected = tableau.selection()
    if selected:
        try:
            index = tableau.index(selected[0])
            tableau.item(selected, values=(entry_date.get(), float(entry_invest.get()), float(entry_pea.get())))
            dates[index] = entry_date.get()
            investissements[index] = float(entry_invest.get())
            pea_values[index] = float(entry_pea.get())
            update_graph()
            update_investissement_total()
            update_rendement()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")

def supprimer_ligne():
    selected = tableau.selection()
    if selected:
        index = tableau.index(selected[0])
        tableau.delete(selected)
        dates.pop(index)
        investissements.pop(index)
        pea_values.pop(index)
        update_graph()
        update_investissement_total()
        update_rendement()

customtkinter.CTkButton(frame_table, text="Ajouter", command=ajouter_ligne).pack(side=LEFT, padx=5)
customtkinter.CTkButton(frame_table, text="Modifier", command=modifier_ligne).pack(side=LEFT, padx=5)
customtkinter.CTkButton(frame_table, text="Supprimer", command=supprimer_ligne).pack(side=LEFT, padx=5)

# --- Tableau ---
style = ttk.Style()
style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
style.configure("Dark.Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b")

tableau = ttk.Treeview(frame_gauche, columns=("Date", "Investissement", "PEA"), show="headings")
tableau.heading("Date", text="Date")
tableau.heading("Investissement", text="Investissement (€)")
tableau.heading("PEA", text="Valeur PEA (€)")
tableau.column("Date", width=100)
tableau.column("Investissement", width=100)
tableau.column("PEA", width=100)
tableau.pack(pady=10, fill=BOTH, expand=True)

def update_table_style_dark():
    style.configure("Dark.Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")

# --- Frame pour l'investissement total et le rendement ---
frame_stats = customtkinter.CTkFrame(frame_gauche)
frame_stats.pack(pady=10, fill=X)

label_invest_total = customtkinter.CTkLabel(
    frame_stats, 
    text="Investissement total: 0.00 €",
    font=("Arial", 16, "bold")
)
label_invest_total.pack(pady=5)

label_rendement = customtkinter.CTkLabel(
    frame_stats, 
    text="Rendement: 0.00 € (0.00%)",
    font=("Arial", 14)
)
label_rendement.pack(pady=5)

def update_investissement_total():
    total = sum(investissements)
    label_invest_total.configure(text=f"Investissement total: {total:.2f} €")

def update_rendement():
    if not pea_values:  # Si aucune valeur PEA
        label_rendement.configure(text="Rendement: 0.00 € (0.00%)")
        return
    
    investissement_total = sum(investissements)
    valeur_pea_actuelle = pea_values[-1]  # Dernière valeur du PEA
    
    rendement_absolu = valeur_pea_actuelle - investissement_total
    
    if investissement_total > 0:
        rendement_pourcentage = (rendement_absolu / investissement_total) * 100
    else:
        rendement_pourcentage = 0
    
    # Choisir la couleur en fonction du rendement
    if rendement_absolu >= 0:
        color = "green"
    else:
        color = "red"
    
    label_rendement.configure(
        text=f"Rendement: {rendement_absolu:.2f} € ({rendement_pourcentage:.2f}%)",
        text_color=color
    )

# --- Frame droite pour graphique ---
frame_droite = customtkinter.CTkFrame(root)
frame_droite.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

# Configuration du style du graphique
plt.style.use('default')
fig, ax = plt.subplots(figsize=(8, 6))
canvas = FigureCanvasTkAgg(fig, master=frame_droite)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

def update_graph():
    ax.clear()
    
    # Déterminer les couleurs en fonction du mode
    if customtkinter.get_appearance_mode() == "Dark":
        bg_color = '#2b2b2b'
        text_color = 'white'
        grid_color = '#444444'
        invest_color = '#1f77b4'  # Bleu
        pea_color = '#ff7f0e'     # Orange
    else:
        bg_color = 'white'
        text_color = 'black'
        grid_color = '#e0e0e0'
        invest_color = '#1f77b4'  # Bleu
        pea_color = '#ff7f0e'     # Orange
    
    # Appliquer les couleurs au graphique
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    
    if dates and investissements and pea_values:
        # Convertir les dates en objets datetime pour un meilleur affichage
        date_objects = [datetime.strptime(date, '%m/%d/%y') for date in dates]
        
        # Calculer l'investissement cumulé
        investissement_cumule = []
        cumul = 0
        for invest in investissements:
            cumul += invest
            investissement_cumule.append(cumul)
        
        # Tracer les courbes
        ax.plot(date_objects, investissement_cumule, label="Investissement cumulé", color=invest_color, marker='o')
        ax.plot(date_objects, pea_values, label="Valeur PEA", color=pea_color, marker='s')
        
        # Formater l'axe des x pour afficher les dates correctement
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m/%y'))
        fig.autofmt_xdate()
    
    ax.set_xlabel("Date", color=text_color)
    ax.set_ylabel("Montant (€)", color=text_color)
    ax.tick_params(colors=text_color)
    ax.grid(True, color=grid_color, alpha=0.3)
    ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)
    
    # Ajuster les bordures du graphique
    for spine in ax.spines.values():
        spine.set_color(text_color)
    
    canvas.draw()

# Fonction pour sélectionner une ligne du tableau
def on_table_select(event):
    selected = tableau.selection()
    if selected:
        values = tableau.item(selected[0], 'values')
        entry_date.set_date(datetime.strptime(values[0], '%m/%d/%y'))
        entry_invest.delete(0, END)
        entry_invest.insert(0, values[1])
        entry_pea.delete(0, END)
        entry_pea.insert(0, values[2])

tableau.bind('<<TreeviewSelect>>', on_table_select)

root.mainloop()
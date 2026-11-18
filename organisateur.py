from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Vidéos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".pptx", ".xlsx"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Programmes": {".py", ".js", ".html", ".css"},
}


def categorie_pour(extension):
    extension = extension.lower()
    for categorie, extensions in CATEGORIES.items():
        if extension in extensions:
            return categorie
    return "Autres"


def destination_libre(destination):
    if not destination.exists():
        return destination
    numero = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{numero}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        numero += 1


class Organisateur:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Organisateur de fichiers")
        self.fenetre.geometry("900x560")
        self.dossier = None
        self.operations = []
        self.construire_interface()

    def construire_interface(self):
        cadre = ttk.Frame(self.fenetre, padding=20)
        cadre.pack(fill="both", expand=True)

        ttk.Label(
            cadre,
            text="📁 Organisateur de fichiers",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(0, 6))

        ttk.Label(
            cadre,
            text="Choisis un dossier, prévisualise le rangement, puis confirme.",
        ).pack(pady=(0, 18))

        ligne = ttk.Frame(cadre)
        ligne.pack(fill="x", pady=(0, 14))
        self.chemin = ttk.Entry(ligne, state="readonly")
        self.chemin.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(
            ligne, text="Choisir un dossier", command=self.choisir_dossier
        ).pack(side="right")

        colonnes = ("nom", "extension", "destination")
        self.tableau = ttk.Treeview(cadre, columns=colonnes, show="headings")
        self.tableau.heading("nom", text="Fichier")
        self.tableau.heading("extension", text="Extension")
        self.tableau.heading("destination", text="Destination")
        self.tableau.column("nom", width=450)
        self.tableau.column("extension", width=110, anchor="center")
        self.tableau.column("destination", width=180, anchor="center")
        self.tableau.pack(fill="both", expand=True)

        bas = ttk.Frame(cadre)
        bas.pack(fill="x", pady=(14, 0))
        self.statut = ttk.Label(bas, text="Aucun dossier sélectionné")
        self.statut.pack(side="left")
        self.bouton = ttk.Button(
            bas,
            text="Ranger les fichiers",
            command=self.ranger,
            state="disabled",
        )
        self.bouton.pack(side="right")

    def choisir_dossier(self):
        chemin = filedialog.askdirectory(title="Choisir le dossier à ranger")
        if not chemin:
            return
        self.dossier = Path(chemin)
        self.chemin.configure(state="normal")
        self.chemin.delete(0, tk.END)
        self.chemin.insert(0, str(self.dossier))
        self.chemin.configure(state="readonly")
        self.analyser()

    def analyser(self):
        self.operations.clear()
        for ligne in self.tableau.get_children():
            self.tableau.delete(ligne)

        for fichier in self.dossier.iterdir():
            if not fichier.is_file():
                continue
            categorie = categorie_pour(fichier.suffix)
            destination = self.dossier / categorie
            self.operations.append((fichier, destination))
            self.tableau.insert(
                "", "end", values=(fichier.name, fichier.suffix, categorie)
            )

        nombre = len(self.operations)
        self.statut.configure(text=f"{nombre} fichier(s) à ranger")
        self.bouton.configure(state="normal" if nombre else "disabled")

    def ranger(self):
        if not messagebox.askyesno(
            "Confirmation", f"Ranger {len(self.operations)} fichier(s) ?"
        ):
            return

        deplaces = 0
        for fichier, dossier_destination in self.operations:
            try:
                dossier_destination.mkdir(exist_ok=True)
                destination = destination_libre(dossier_destination / fichier.name)
                shutil.move(str(fichier), str(destination))
                deplaces += 1
            except OSError as erreur:
                messagebox.showerror("Erreur", f"{fichier.name}\n{erreur}")

        self.analyser()
        messagebox.showinfo("Terminé", f"{deplaces} fichier(s) rangé(s) !")


if __name__ == "__main__":
    racine = tk.Tk()
    Organisateur(racine)
    racine.mainloop()


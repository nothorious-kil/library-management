# ===== IMPORTS =====
from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

# ===== INITIALISER FLASK =====
app = Flask(__name__)

# Nom du fichier CSV pour stocker les livres
NOM_FICHIER = "livres.csv"


# ===== CLASSE LIVRE =====
class Livre:
    """Représente un livre individuel"""

    def __init__(self, titre, auteur, genre, annee):
        """
        Initialise un nouveau livre

        Args:
            titre (str): Le titre du livre
            auteur (str): L'auteur du livre
            genre (str): Le genre (Fiction, Romance, Thriller, etc.)
            annee (int): L'année de publication
        """
        self.titre = titre
        self.auteur = auteur
        self.genre = genre
        self.annee = annee
        self.statut = "Non lu"  # "Non lu", "En cours", "Lu"
        self.note = 0  # Note de 0 à 5
        self.avis = ""  # Avis personnel
        self.date_ajout = datetime.now().strftime("%d/%m/%Y")

    def marquer_en_cours(self):
        """Marquer le livre comme en cours de lecture"""
        self.statut = "En cours"

    def marquer_lu(self):
        """Marquer le livre comme lu"""
        self.statut = "Lu"

    def ajouter_note(self, note):
        """
        Ajouter une note au livre

        Args:
            note (int): Note entre 0 et 5
        """
        if 0 <= note <= 5:
            self.note = note
        else:
            raise ValueError("La note doit être entre 0 et 5")

    def ajouter_avis(self, avis):
        """
        Ajouter un avis personnel

        Args:
            avis (str): L'avis personnel sur le livre
        """
        self.avis = avis

    def afficher_info(self):
        """Retourne les informations du livre sous forme de texte"""
        return f"{self.titre} de {self.auteur} ({self.annee}) - {self.genre}"

    def to_dict(self):
        """Convertit le livre en dictionnaire (pour sauvegarder en CSV)"""
        return {
            "titre": self.titre,
            "auteur": self.auteur,
            "genre": self.genre,
            "annee": self.annee,
            "statut": self.statut,
            "note": self.note,
            "avis": self.avis,
            "date_ajout": self.date_ajout,
        }

    @staticmethod
    def from_dict(data):
        """Crée un livre à partir d'un dictionnaire (pour charger depuis CSV)"""
        livre = Livre(data["titre"], data["auteur"], data["genre"], data["annee"])
        livre.statut = data["statut"]
        livre.note = int(data["note"])
        livre.avis = data["avis"]
        livre.date_ajout = data["date_ajout"]
        return livre


# ===== CLASSE BIBLIOTHEQUE =====
class Bibliotheque:
    """Gère une collection complète de livres"""

    def __init__(self, nom_fichier=NOM_FICHIER):
        """
        Initialise la bibliothèque

        Args:
            nom_fichier (str): Nom du fichier pour sauvegarder les livres
        """
        self.nom_fichier = nom_fichier
        self.livres = []  # Liste pour stocker les livres
        self.charger_livres()  # Charger les livres sauvegardés

    def charger_livres(self):
        """Charge les livres depuis le fichier CSV"""
        # Vérifier si le fichier existe
        if os.path.exists(self.nom_fichier):
            try:
                with open(self.nom_fichier, "r", encoding="utf-8") as fichier:
                    # Utiliser DictReader pour lire le CSV avec les en-têtes
                    reader = csv.DictReader(fichier)
                    # Convertir chaque ligne en objet Livre
                    self.livres = [Livre.from_dict(row) for row in reader]
            except Exception as e:
                print(f"Erreur lors du chargement : {e}")
        else:
            # Créer un fichier vide s'il n'existe pas
            self.sauvegarder_livres()

    def sauvegarder_livres(self):
        """Sauvegarde les livres dans le fichier CSV"""
        try:
            # Définir les noms des colonnes
            colonnes = [
                "titre",
                "auteur",
                "genre",
                "annee",
                "statut",
                "note",
                "avis",
                "date_ajout",
            ]

            # Ouvrir le fichier en mode écriture
            with open(self.nom_fichier, "w", newline="", encoding="utf-8") as fichier:
                # Utiliser DictWriter pour écrire avec les en-têtes
                writer = csv.DictWriter(fichier, fieldnames=colonnes)
                # Écrire la ligne d'en-têtes
                writer.writeheader()
                # Écrire chaque livre converti en dictionnaire
                for livre in self.livres:
                    writer.writerow(livre.to_dict())
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def ajouter_livre(self, titre, auteur, genre, annee):
        """
        Ajoute un nouveau livre

        Args:
            titre (str): Le titre
            auteur (str): L'auteur
            genre (str): Le genre
            annee (int): L'année
        """
        # Vérifier que les champs ne sont pas vides
        if titre.strip() and auteur.strip() and genre.strip():
            try:
                # Créer un nouveau livre
                livre = Livre(titre, auteur, genre, int(annee))
                # L'ajouter à la liste
                self.livres.append(livre)
                # Sauvegarder immédiatement
                self.sauvegarder_livres()
                return True
            except ValueError:
                return False
        return False

    def get_livres_dict(self):
        """Retourne les livres sous forme de dictionnaires (pour l'HTML)"""
        livres_list = []
        for index, livre in enumerate(self.livres):
            livres_list.append(
                {
                    "index": index,
                    "titre": livre.titre,
                    "auteur": livre.auteur,
                    "genre": livre.genre,
                    "annee": livre.annee,
                    "statut": livre.statut,
                    "note": livre.note,
                    "avis": livre.avis,
                    "date_ajout": livre.date_ajout,
                }
            )
        return livres_list

    def supprimer_livre(self, index):
        """
        Supprime un livre

        Args:
            index (int): L'index du livre à supprimer
        """
        try:
            if 0 <= index < len(self.livres):
                del self.livres[index]
                self.sauvegarder_livres()
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            return False

    def marquer_en_cours(self, index):
        """Marquer un livre comme en cours de lecture"""
        try:
            if 0 <= index < len(self.livres):
                self.livres[index].marquer_en_cours()
                self.sauvegarder_livres()
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            return False

    def marquer_lu(self, index):
        """Marquer un livre comme lu"""
        try:
            if 0 <= index < len(self.livres):
                self.livres[index].marquer_lu()
                self.sauvegarder_livres()
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            return False

    def ajouter_note(self, index, note):
        """Ajouter une note à un livre"""
        try:
            if 0 <= index < len(self.livres):
                self.livres[index].ajouter_note(int(note))
                self.sauvegarder_livres()
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            return False

    def ajouter_avis(self, index, avis):
        """Ajouter un avis à un livre"""
        try:
            if 0 <= index < len(self.livres):
                self.livres[index].ajouter_avis(avis)
                self.sauvegarder_livres()
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            return False

    def filtrer_par_genre(self, genre):
        """
        Retourne les livres d'un genre spécifique

        Args:
            genre (str): Le genre à filtrer

        Returns:
            list: Liste des livres du genre
        """
        return [livre for livre in self.livres if livre.genre.lower() == genre.lower()]

    def filtrer_par_auteur(self, auteur):
        """
        Retourne les livres d'un auteur spécifique

        Args:
            auteur (str): L'auteur à filtrer

        Returns:
            list: Liste des livres de l'auteur
        """
        return [
            livre for livre in self.livres if livre.auteur.lower() == auteur.lower()
        ]

    def filtrer_par_statut(self, statut):
        """
        Retourne les livres avec un statut spécifique

        Args:
            statut (str): Le statut à filtrer ("Non lu", "En cours", "Lu")

        Returns:
            list: Liste des livres avec ce statut
        """
        return [livre for livre in self.livres if livre.statut == statut]

    def get_genres(self):
        """Retourne la liste de tous les genres uniques"""
        genres = set()
        for livre in self.livres:
            genres.add(livre.genre)
        return sorted(list(genres))

    def get_auteurs(self):
        """Retourne la liste de tous les auteurs uniques"""
        auteurs = set()
        for livre in self.livres:
            auteurs.add(livre.auteur)
        return sorted(list(auteurs))

    def get_statistiques(self):
        """Retourne les statistiques de la bibliothèque"""
        total = len(self.livres)
        lus = len(self.filtrer_par_statut("Lu"))
        en_cours = len(self.filtrer_par_statut("En cours"))
        non_lus = len(self.filtrer_par_statut("Non lu"))
        note_moyenne = 0

        # Calculer la note moyenne
        if total > 0:
            notes = [livre.note for livre in self.livres if livre.note > 0]
            if notes:
                note_moyenne = round(sum(notes) / len(notes), 1)

        return {
            "total": total,
            "lus": lus,
            "en_cours": en_cours,
            "non_lus": non_lus,
            "note_moyenne": note_moyenne,
        }


# ===== CRÉER L'INSTANCE GLOBALE =====
bibliotheque = Bibliotheque()


# ===== ROUTES FLASK =====


@app.route("/")
def index():
    """Route principale - affiche tous les livres"""
    livres = bibliotheque.get_livres_dict()
    stats = bibliotheque.get_statistiques()
    genres = bibliotheque.get_genres()
    auteurs = bibliotheque.get_auteurs()

    return render_template(
        "index.html", livres=livres, stats=stats, genres=genres, auteurs=auteurs
    )


@app.route("/ajouter", methods=["POST"])
def ajouter():
    """Route pour ajouter un livre"""
    titre = request.form.get("titre", "").strip()
    auteur = request.form.get("auteur", "").strip()
    genre = request.form.get("genre", "").strip()
    annee = request.form.get("annee", "").strip()

    # Ajouter le livre
    if bibliotheque.ajouter_livre(titre, auteur, genre, annee):
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@app.route("/supprimer/<int:index>", methods=["POST"])
def supprimer(index):
    """Route pour supprimer un livre"""
    bibliotheque.supprimer_livre(index)
    return redirect(url_for("index"))


@app.route("/en-cours/<int:index>", methods=["POST"])
def en_cours(index):
    """Route pour marquer un livre comme en cours"""
    bibliotheque.marquer_en_cours(index)
    return redirect(url_for("index"))


@app.route("/lu/<int:index>", methods=["POST"])
def lu(index):
    """Route pour marquer un livre comme lu"""
    bibliotheque.marquer_lu(index)
    return redirect(url_for("index"))


@app.route("/noter/<int:index>", methods=["POST"])
def noter(index):
    """Route pour ajouter une note"""
    note = request.form.get("note", "0")
    bibliotheque.ajouter_note(index, note)
    return redirect(url_for("index"))


@app.route("/avis/<int:index>", methods=["POST"])
def avis_livre(index):
    """Route pour ajouter un avis"""
    avis = request.form.get("avis", "")
    bibliotheque.ajouter_avis(index, avis)
    return redirect(url_for("index"))


@app.route("/genre/<genre>")
def par_genre(genre):
    """Route pour filtrer par genre"""
    livres_filtres = bibliotheque.filtrer_par_genre(genre)
    livres = [
        {
            "index": bibliotheque.livres.index(livre),
            "titre": livre.titre,
            "auteur": livre.auteur,
            "genre": livre.genre,
            "annee": livre.annee,
            "statut": livre.statut,
            "note": livre.note,
            "avis": livre.avis,
            "date_ajout": livre.date_ajout,
        }
        for livre in livres_filtres
    ]

    stats = bibliotheque.get_statistiques()
    genres = bibliotheque.get_genres()
    auteurs = bibliotheque.get_auteurs()

    return render_template(
        "index.html",
        livres=livres,
        stats=stats,
        genres=genres,
        auteurs=auteurs,
        filtre_genre=genre,
    )


@app.route("/auteur/<auteur>")
def par_auteur(auteur):
    """Route pour filtrer par auteur"""
    livres_filtres = bibliotheque.filtrer_par_auteur(auteur)
    livres = [
        {
            "index": bibliotheque.livres.index(livre),
            "titre": livre.titre,
            "auteur": livre.auteur,
            "genre": livre.genre,
            "annee": livre.annee,
            "statut": livre.statut,
            "note": livre.note,
            "avis": livre.avis,
            "date_ajout": livre.date_ajout,
        }
        for livre in livres_filtres
    ]

    stats = bibliotheque.get_statistiques()
    genres = bibliotheque.get_genres()
    auteurs = bibliotheque.get_auteurs()

    return render_template(
        "index.html",
        livres=livres,
        stats=stats,
        genres=genres,
        auteurs=auteurs,
        filtre_auteur=auteur,
    )


# ===== LANCER L'APPLICATION =====
if __name__ == "__main__":
    print("🚀 Serveur Flask démarré !")
    print("📱 Ouvre ton navigateur et va sur : http://localhost:5000")
    app.run(debug=True, host="localhost", port=5000)

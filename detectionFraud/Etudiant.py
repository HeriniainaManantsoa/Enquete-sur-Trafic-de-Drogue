from enum import Enum
import random

class Statut (Enum):
    NORMAL = 1
    FUMEUR = 2
    DEALER = 3
    FOURNISSEUR = 4

class Faculte (Enum):
    SCIENCE = 1
    EGS = 2
    DROIT = 3
    MEDECINE = 4
    AGRO = 5
    LETTRE = 6

class Niveau (Enum):
    l1 = 1
    l2 = 2
    l3 = 3
    m1 = 4
    m2 = 5

class Etudiant:
    def __init__ (self):
        self.id = 0
        self.faculte = None
        self.niveau = None
        self.statut = None
    def creer_faculte (self):
        self.faculte = random.choice(list(Faculte))
    def creer_niveau (self):
        n = random.randint(0,100)
        if n >= 60:
            self.niveau = Niveau.l1
        elif n >= 30:
            self.niveau = Niveau.l2
        elif n >= 10:
            self.niveau = Niveau.l3
        elif n >= 4:
            self.niveau = Niveau.m1
        else:
            self.niveau = Niveau.m2
    def creer_etudiant (self):
        self.creer_faculte()
        self.creer_niveau()
        self.statut = Statut.NORMAL
    def affiche_information (self):
        print ("id : ",self.id)
        print ("faculte : ",self.faculte.name)
        print ("niveau : ",self.niveau.name)
        print ("statut : ",self.statut.name)






















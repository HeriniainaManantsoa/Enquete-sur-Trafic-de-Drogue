import Etudiant
import random

class Generateur:
    def __init__ (self,n,p):
        self.E = {}
        self.V = []
        self.creer_G(n,p)

    def connecter (self,e1,e2):
        if e1 not in self.E:
            self.E[e1] = []
        self.E[e1].append(e2)

    def creer_V (self,tailleG):
        self.V = []
        for x in range(tailleG):
            e = Etudiant.Etudiant ()
            e.creer_etudiant()
            e.id = x
            self.V.append (e)

    def creer_G (self,n,p): # n est le nombre de sommet et p une probabilite fixe
        self.E = {}
        self.creer_V(n)
        for e1 in self.V:
            for e2 in self.V:
                proba = random.random() # on cree aleatoirement G suivant la probabilite p
                if proba <= p:
                    self.connecter(e1,e2)

    def supprime_boucle (self):
        for e in self.V:
            if e in self.E:
                while e in self.E[e]:   # tant que e est son propre voisin
                    self.E[e].remove(e) # -> on le supprime dans la liste des ses voisins

    def supprime_connection_multiple (self):
        for e1 in self.E:
            newE = []
            for e2 in self.E[e1]:   # on creer une nouvelle liste qui met une seule fois le voisin dans la liste des voisins
                if e2 not in newE:  # -> ca evite les connections multiples
                    newE.append(e2)
            self.E[e1] = newE

    def oriente_G (self):
        ancienE = self.E.copy()
        for e1 in ancienE:
            for e2 in ancienE[e1]:
                if e2 not in self.E:
                    self.E[e2] = []
                if e1 not in self.E[e2]:
                    self.E[e2].append(e1) # on met e1 dans les voisins de e2 et e2 dans les voisins de 1
                                          # -> G est non oriente, on peut aller de e1 vers e2 et vis versa
    
    def existe_chemin (self,q,qs,Couleurs,Parent):
        if q == qs:
            return True
        Couleurs[q] = "noir"
        for q_prime in self.E.get(q, []):
            if Couleurs[q_prime] == "blanc":
                Parent[q_prime] = q
                trouve = self.existe_chemin(q_prime,qs,Couleurs,Parent)
                if trouve == True:
                    return True
        return False

    def connexe_G (self):
        Couleurs = {}
        Parent = {}
        for e1 in self.V:
            for e2 in self.V:
                for e in self.V:
                    Couleurs[e] = "blanc"
                    Parent[e] = None
                trouve = self.existe_chemin(e1,e2,Couleurs,Parent)
                if trouve == False:
                    if e1 not in self.E:
                        self.E[e1] = []
                    if e2 not in self.E[e1]:
                        self.E[e1].append(e2)
                    if e2 not in self.E:
                        self.E[e2] = []
                    if e1 not in self.E[e2]:
                        self.E[e2].append(e1)

    def get_G_prime (self):
        self.supprime_boucle()
        self.supprime_connection_multiple()
        self.oriente_G()
        self.connexe_G()
        return self
        
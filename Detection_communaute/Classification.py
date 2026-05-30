from neo4j import GraphDatabase
import Etudiant
from collections import deque

class Classificateur:
    def __init__ (self):
        self.driver = None
        self.V = []
        self.E = {}

    def connection (self,username,password):
        URI = "neo4j://localhost:7687"
        self.driver = GraphDatabase.driver (URI,auth=(username,password))
        print ("connexion reussie")

    def recherche_noeuds (self,id):
        for e in self.V:
            if e.id == id:
                return e

    def connecter (self,e1,e2):
        if e1 != e2:
            if e1 not in self.E:
                self.E[e1] = []
            if e2 not in self.E[e1]:
                self.E[e1].append(e2)
            if e2 not in self.E:
                self.E[e2] = []
            if e1 not in self.E[e2]:
                self.E[e2].append(e1)

#-----------------------------Recuperation-Donnees-----------------------------#

    def restore_noeuds (self,tx):
        query = """MATCH (n:Etudiant)
                   RETURN n.id AS id, n.faculte AS faculte, n.niveau AS niveau,n.statut AS statut
                   ORDER BY id ASC"""
        result = tx.run (query)
        for record in result:
            e = Etudiant.Etudiant()
            e.id = record['id']
            e.faculte = record['faculte']
            e.niveau = record['niveau']
            e.statut = record['statut']
            self.V.append(e)

    def restore_aretes (self,tx):
        query = """MATCH (n1:Etudiant)-[:CONNAIS]->(n2:Etudiant)
                   RETURN n1.id AS id1, n2.id AS id2"""
        result = tx.run (query)
        for record in result:
            e1 = self.recherche_noeuds(record['id1'])
            e2 = self.recherche_noeuds(record['id2'])
            self.connecter (e1,e2)

    # On recupere les noeuds et relations depuis neo4j pour rechercher les cliques et les sous-graphes
    def restore_data (self):
        with self.driver.session() as session:
            session.execute_read(self.restore_noeuds)
            session.execute_read(self.restore_aretes)
        self.driver.close()

#-----------------------------Cliques-----------------------------#

    def agrandi_clique (self,clique):
        continuer = False
        for x in list(clique):
            for voisin in self.E.get(x, []):
                if voisin not in clique and all(voisin in self.E.get(y, []) for y in clique):
                    clique.append(voisin)
                    continuer = True
        if continuer == True:
            self.agrandi_clique(clique)
        return clique

    def rechercher_cliques (self):
        cliquesListe = []
        for e in self.E:
            clique = [e]
            clique = self.agrandi_clique(clique)
            if len(clique) >= 3:
                ids = frozenset(n.id for n in clique)
                if ids not in [frozenset(n.id for n in c) for c in cliquesListe]:
                    cliquesListe.append(clique)

        return cliquesListe

#-----------------------------Sous-Graphe-----------------------------#

    def rechercher_sous_graphes(self):
        visites = set()
        sous_graphes = []

        for noeud in self.V:
            if noeud in visites:
                continue

            # BFS depuis ce noeud non encore visité
            composante = []
            file = deque([noeud])
            visites.add(noeud)

            while file:
                courant = file.popleft()
                composante.append(courant)
                for voisin in self.E.get(courant, []):
                    if voisin not in visites:
                        visites.add(voisin)
                        file.append(voisin)

            if len(composante) >= 2:   # on ignore les noeuds isolés
                sous_graphes.append(composante)

        return sous_graphes

    def classification (self,username,password):
        self.connection(username,password)
        self.restore_data()
        classe = {"cliques": [],"sous-graphes": []}
        classe["cliques"] = self.rechercher_cliques()
        classe["sous-graphes"] = self.rechercher_sous_graphes()
        return classe
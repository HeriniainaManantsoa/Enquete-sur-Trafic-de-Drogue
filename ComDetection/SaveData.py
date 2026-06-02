from neo4j import GraphDatabase
import networkx as nx
import Classification

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "examencomfraud@neo4j"

def clear (tx):
    query = """
    MATCH (n) DETACH DELETE n"""
    tx.run(query)

def saveNodes (tx,etudiant,couleur):
    id = etudiant.id
    faculte = etudiant.faculte.name
    niveau = etudiant.niveau.name
    statut = etudiant.statut.name
    query = """MERGE (e:Etudiant {id:$id,faculte:$faculte,niveau:$niveau,statut:$statut})
               SET e.couleur = $couleur"""
    tx.run (query,id=id,faculte=faculte,niveau=niveau,statut=statut,couleur=couleur)

def saveRelationships (tx,etudiant1,etudiant2,poids):
    id1 = etudiant1.id
    id2 = etudiant2.id
    query = """MATCH (e1:Etudiant {id:$id1})
               MATCH (e2:Etudiant {id:$id2})
               MERGE (e1)-[:CONNAIS {poids:$poids}]->(e2)"""
    tx.run (query,id1=id1,id2=id2,poids=poids)

def save_data (Graphe,V,E):
    print ("Sauvegarde des donnees dans noe4j....")
    driver = GraphDatabase.driver (URI,auth=(USERNAME,PASSWORD))
    with driver.session() as session:
        session.execute_write(clear)
        classificateur = Classification.Classificateur()
        classificateur.V = V
        classificateur.E = E
        couleurs = classificateur.coloration()

        for etudiant in Graphe.V:
            couleur = couleurs[etudiant]
            session.execute_write (saveNodes,etudiant,couleur)
            
        for etudiant in Graphe.E:
            for voisin in Graphe.E[etudiant]:
                session.execute_write (saveRelationships,etudiant,voisin,1)
    driver.close()
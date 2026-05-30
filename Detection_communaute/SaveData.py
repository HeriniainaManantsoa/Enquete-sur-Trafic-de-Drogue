from neo4j import GraphDatabase
import networkx as nx

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "examencomfraud@neo4j"

def clear (tx):
    query = """
    MATCH (n) DETACH DELETE n"""
    tx.run(query)

def saveNodes (tx,etudiant):
    id = etudiant.id
    faculte = etudiant.faculte.name
    niveau = etudiant.niveau.name
    statut = etudiant.statut.name
    query = """MERGE (:Etudiant {id:$id,faculte:$faculte,niveau:$niveau,statut:$statut})"""
    tx.run (query,id=id,faculte=faculte,niveau=niveau,statut=statut)

def saveRelationships (tx,etudiant1,etudiant2,poids):
    id1 = etudiant1.id
    id2 = etudiant2.id
    query = """MATCH (e1:Etudiant {id:$id1})
               MATCH (e2:Etudiant {id:$id2})
               MERGE (e1)-[:CONNAIS {poids:$poids}]->(e2)"""
    tx.run (query,id1=id1,id2=id2,poids=poids)

def save_data (Graphe):
    driver = GraphDatabase.driver (URI,auth=(USERNAME,PASSWORD))
    print ("connexion reussie")
    with driver.session() as session:
        session.execute_write(clear)

        for etudiant in Graphe.V:
            session.execute_write (saveNodes,etudiant)
            
        for etudiant in Graphe.E:
            for voisin in Graphe.E[etudiant]:
                session.execute_write (saveRelationships,etudiant,voisin,1)
    driver.close()
from neo4j import GraphDatabase
import Universite
import Simulateur

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "examencomfraud@neo4j"

driver = GraphDatabase.driver (URI,auth=(USERNAME,PASSWORD))
print ("connexion reussie")

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

with driver.session() as session:
    ankatso = Universite.Universite()
    ankatso.creer_universite(1000)
    comGeneral = Simulateur.ComGeneral (ankatso.liste)
    comGeneral.simuler_graph ()

    for etudiant in comGeneral.listeEtudiant:
        session.execute_write (saveNodes,etudiant)
        
    for etudiant in comGeneral.grapheCom:
        for voisin in comGeneral.grapheCom[etudiant]:
            session.execute_write (saveRelationships,etudiant,voisin,comGeneral.grapheCom[etudiant][voisin])

driver.close()
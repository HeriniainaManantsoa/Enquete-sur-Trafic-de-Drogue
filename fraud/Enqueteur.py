from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "examencomfraud@neo4j"

driver = GraphDatabase.driver (URI,auth=(USERNAME,PASSWORD))
print ("connexion reussie")

def graph_projection (tx):
    query = """
    CALL gds.graph.project (
    'myGraph','Etudiant',
    {
        CONNAIS:{
            orientation:'NATURAL',
            properties: {
                    poids: {
                        property: 'poids',
                        defaultValue: 1
                    }
            }
        }
    },
    {
        nodeProperties:'id'
    })"""
    tx.run(query)

def drop_projection (tx):
    query = """
    CALL gds.graph.exists('myGraph') YIELD exists
    WITH exists WHERE exists = true
    CALL gds.graph.drop('myGraph') YIELD graphName
    RETURN graphName"""
    tx.run(query)

def louvain (tx):
    query = """
    CALL gds.louvain.stream('myGraph')
    YIELD nodeId, communityId, intermediateCommunityIds
    RETURN gds.util.asNode(nodeId).id AS id,
           gds.util.asNode(nodeId).faculte AS faculte,
           gds.util.asNode(nodeId).niveau AS niveau,
           gds.util.asNode(nodeId).statut AS statut,
           communityId
    ORDER BY communityId ASC"""
    result = tx.run(query)
    communities = {}
    for record in result:
        if record['communityId'] not in communities:
            currentId = record['communityId']
            communities[currentId] = []
        communities[currentId].append(record['id'])
    return communities

def weighted_louvain (tx):
    query = """
    CALL gds.louvain.stream('myGraph',{ relationshipWeightProperty: 'poids'})
    YIELD nodeId, communityId, intermediateCommunityIds
    RETURN gds.util.asNode(nodeId).id AS id,
           gds.util.asNode(nodeId).faculte AS faculte,
           gds.util.asNode(nodeId).niveau AS niveau,
           gds.util.asNode(nodeId).statut AS statut,
           communityId
    ORDER BY communityId ASC"""
    result = tx.run(query)
    communities = {}
    for record in result:
        if record['communityId'] not in communities:
            currentId = record['communityId']
            communities[currentId] = []
        communities[currentId].append(record['id'])
    return communities

def calculDensite (tx,comMembers):
    ids = comMembers
    query = """
        MATCH (e1:Etudiant)-[:CONNAIS]->(e2:Etudiant)
        WHERE e1.id IN $ids AND e2.id IN $ids AND e1.id <> e2.id
        RETURN count(*) AS nb_liens"""
    result = tx.run(query,ids=ids)
    nb_liens = result.single()["nb_liens"]
    n = len(comMembers)
    liens_possibles = n * (n - 1)
    return round(nb_liens / liens_possibles, 4) if liens_possibles > 0 else 0.0

def densite_taille (densite,comMembers):
    taille = len(comMembers)
    return densite * (1 + taille / 100)

def getFraudCom (tx,fraudMembers):
    ids = fraudMembers
    query = """MATCH (e:Etudiant)
               WHERE e.id IN $ids
               RETURN e.id AS id, e.faculte AS faculte, e.niveau AS niveau, e.statut AS statut"""
    result = tx.run (query,ids=ids)
    comMembers = []
    for record in result:
        comMembers.append(record['id'])
        print (f"id: {record['id']} , faculte : {record['faculte']} , niveau : {record['niveau']} , statut : {record['statut']}")
    return comMembers

def getRoles (comMembers):
    dicoDegreSortant = session.execute_read(degre_sortant,comMembers)
    dicoDegreEntrant = session.execute_read(degre_entrant,comMembers)
    s_s = seuil(dicoDegreSortant.values())
    s_e = seuil(dicoDegreEntrant.values())
    roles = {"fournisseurs": [],"dealer": [],"consommateurs": []}
    for id in comMembers:
        degreEntrant = dicoDegreEntrant.get(id,0)
        degreSortant = dicoDegreSortant.get(id,0)
        if degreSortant >= s_s and degreSortant <= s_s:
            roles["fournisseurs"].append(id)
#-------------------------------------------------------------------------------------
def moyenne_sortant (tx,comMembers):
    ids = comMembers
    query = """
    MATCH (e1:Etudiant)-[r:CONNAIS]->(e2:Etudiant)
    WHERE e1.id IN $ids AND e2.id IN $ids
    RETURN e1.id AS id, avg(r.poids) AS poids_moyen_sortant
    ORDER BY poids_moyen_sortant DESC"""
    result = tx.run (query,ids=ids)
    dico = {}
    for record in result:
        dico[record['id']] = record['poids_moyen_sortant']
    return dico

def moyenne_entrant (tx,comMembers):
    ids = comMembers
    query = """
    MATCH (e1:Etudiant)<-[r:CONNAIS]-(e2:Etudiant)
    WHERE e1.id IN $ids AND e2.id IN $ids
    RETURN e1.id AS id, avg(r.poids) AS poids_moyen_entrant
    ORDER BY poids_moyen_entrant DESC"""
    result = tx.run (query,ids=ids)
    dico = {}
    for record in result:
        dico[record['id']] = record['poids_moyen_entrant']
    return dico

def seuil (dico,k = 2):
    valeurs = list(dico.values())
    moyenne = sum(valeurs) / len(dico)
    ecartType = (sum((x - moyenne)**2 for x in valeurs) / len(valeurs))**0.5
    return moyenne + k * ecartType

def get_roles (comMembers,session):
    dico_sortant = session.execute_read(moyenne_sortant,comMembers)
    dico_entrant = session.execute_read(moyenne_entrant,comMembers)
    seuil_sortant = seuil(dico_sortant)
    seuil_entrant = seuil(dico_entrant)

    hierarchie = {"fournisseurs":[], "dealers":[], "consommateurs": []}
    for id in comMembers:
        pm_s = dico_sortant.get(id,0)
        pm_e = dico_entrant.get(id,0)
        if pm_s >= seuil_sortant and pm_e < seuil_entrant:
            hierarchie["fournisseurs"].append(id)
        elif pm_s >= seuil_sortant and pm_e >= seuil_entrant:
            hierarchie["dealers"].append(id)
        else:
            hierarchie["consommateurs"].append(id)
    return hierarchie

#-------------------------------------------------------------------------------------

with driver.session() as session:
    session.execute_write (drop_projection)
    session.execute_write(graph_projection)
#-------------------------------------------------------------------------------------
    communities = session.execute_read(weighted_louvain)
    listDensiteTaille = {}
    for comId,comMembers in communities.items():
        densite = session.execute_read(calculDensite,comMembers)
        densiteTaille = densite_taille(densite,comMembers)
        listDensiteTaille[comId] = densiteTaille
    listeDensitySorted = sorted(listDensiteTaille.items(), key=lambda x: x[1], reverse=True)
    comId, densite = listeDensitySorted[0]
    comMembers = session.execute_read(getFraudCom,communities[comId])
#-------------------------------------------------------------------------------------
    hierarchie = get_roles (comMembers,session)
    print ("fournisseurs: ")
    for fournisseurs in hierarchie["fournisseurs"]:
        print (fournisseurs)
    print ("dealers: ")
    for dealers in hierarchie["dealers"]:
        print (dealers)
    print ("consommateurs: ")
    for consommateurs in hierarchie["consommateurs"]:
        print (consommateurs)

    session.execute_write (drop_projection)
driver.close()
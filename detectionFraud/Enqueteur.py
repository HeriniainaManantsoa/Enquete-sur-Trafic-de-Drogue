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

def degre_sortant (tx,comMembers):
    ids=comMembers
    query = """
    MATCH (e1:Etudiant)
    WHERE e1.id IN $ids
    OPTIONAL MATCH (e1)-[:CONNAIS]->(e2:Etudiant)
    WHERE e2.id IN $ids
    WITH e1.id AS id, count(e2) AS degre
    RETURN id, degre
    ORDER BY degre DESC"""
    result = tx.run(query,ids=ids)
    dicoDegreSortant = {}
    for record in result:
        dicoDegreSortant[record['id']] = record['degre']
    return dicoDegreSortant

def degre_entrant (tx,comMembers):
    ids = comMembers
    query = """
    MATCH (e1:Etudiant)
    WHERE e1.id IN $ids
    OPTIONAL MATCH (e2:Etudiant)-[:CONNAIS]->(e1) WHERE e2.id IN $ids
    WITH e1.id AS id, count(e2) AS degre
    RETURN id, degre
    ORDER BY degre DESC"""
    result = tx.run(query,ids=ids)
    dicoDegreEntrant = {}
    for record in result:
        dicoDegreEntrant[record['id']] = record['degre']
    return dicoDegreEntrant

def seuil (valeurs):
    moyenne = sum(valeurs)/len(valeurs)
    ecartType = (sum((x - moyenne)**2 for x in valeurs)/len(valeurs))**0.5
    resultat = moyenne + 1.5 * ecartType
    return resultat

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

def scc (tx):
    query = """
    CALL gds.scc.stream('myGraph')
    YIELD nodeId, componentId 
    WITH componentId,
         collect (gds.util.asNode(nodeId).id) AS members,
         count(*) AS taille
    WHERE taille > 10
    RETURN componentId, taille, members
    ORDER BY taille DESC"""
    result = tx.run(query)
    for record in result:
        print (f"Composante {record['componentId']}")

with driver.session() as session:
    session.execute_write (drop_projection)
    session.execute_write(graph_projection)

    communities = session.execute_read(weighted_louvain)
    listDensiteTaille = {}
    for comId,comMembers in communities.items():
        densite = session.execute_read(calculDensite,comMembers)
        densiteTaille = densite_taille(densite,comMembers)
        listDensiteTaille[comId] = densiteTaille
    listeDensitySorted = sorted(listDensiteTaille.items(), key=lambda x: x[1], reverse=True)
    #print(listeDensitySorted)
    comId, densite = listeDensitySorted[0]
    comMembers = session.execute_read(getFraudCom,communities[comId])
    
    session.execute_write (drop_projection)
driver.close()
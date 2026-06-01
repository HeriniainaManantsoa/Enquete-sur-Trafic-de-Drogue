import Interface
import Classification
import Generation
import SaveData
import math

n = 500
p = math.log(n) / n
G = Generation.Generateur(n,p)
GPrime = G.get_G_prime()

SaveData.save_data(GPrime)

affichageGPrime = Interface.Interface(GPrime)
affichageGPrime.create_interface()

classificateur = Classification.Classificateur()
classificateur.restore_data()
couleurs = classificateur.coloration()
classe = classificateur.classe_graphe("neo4j", "examencomfraud@neo4j")
for clique in classe["cliques"]:
    print (clique)
for sous-graphe in classe["sous-graphes"]:
    print (sous-graphe)
import Interface
import Classification
import Generation
import SaveData
import math


if __name__ == "__main__":
    n = 50
    p = math.log(n) / n
    G = Generation.Generateur(n,p)
    GPrime = G.get_G_prime()

    #SaveData.save_data(GPrime,GPrime.V,GPrime.E)

    classificateur = Classification.Classificateur()
    classificateur.V = GPrime.V
    classificateur.E = GPrime.E
    cliques = classificateur.rechercher_cliques()
    for clique in cliques:
        for e in clique:
            print (e.id)
        print ()

    affichageGPrime = Interface.Interface(GPrime)
    affichageGPrime.create_interface()
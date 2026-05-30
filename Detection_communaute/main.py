import Interface
import Classification
import Generation
import SaveData

G = Generation.Generateur(500,0.002)
GPrime = G.get_G_prime()

SaveData.save_data(GPrime)

affichageGPrime = Interface.Interface(GPrime)
affichageGPrime.create_interface()
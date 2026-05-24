import Universite
import Simulateur
import Interface

ankatso = Universite.Universite()
ankatso.creer_universite(1000)

simulateur = Simulateur.ComGeneral (ankatso.liste)
simulateur.simuler_graph ()

interface = Interface.Interface ()
interface.define_style()
interface.define_nodes (simulateur.listeEtudiant)
interface.define_edges(simulateur.grapheCom)
interface.create_interface()
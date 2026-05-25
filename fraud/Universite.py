import Etudiant

class Universite:
    def __init__ (self):
        self.liste = []
    def inscrire (self, etudiant):
        self.liste.append(etudiant)
    def renvoyer (self, etudiant):
        self.liste.remove(etudiant)
    def creer_universite (self,nombreEtudiant):
        for id in range(nombreEtudiant):
            etudiant = Etudiant.Etudiant()
            etudiant.creer_etudiant()
            etudiant.id = id
            self.inscrire(etudiant)
    def affiche_etudiant (self):
        for etudiant in self.liste:
            etudiant.affiche_information()
            print ("")
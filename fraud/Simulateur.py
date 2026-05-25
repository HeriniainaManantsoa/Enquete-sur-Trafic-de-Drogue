import random
import Etudiant

class ComFraude:
    def __init__ (self):
        self.listeMembre = []
        self.listeFournisseur = []
        self.listeDealer = []
        self.listeConsommateur = []
        self.grapheCom = {}

    def ajouterMembre (self,groupe,etudiant):
        if etudiant not in groupe:
            groupe.append(etudiant)

    def get_membre (self,listeEtudiant):
        effectifEtudiant = len(listeEtudiant)
        effectifComFraude = int((8 * effectifEtudiant) / 100) + 1
        listeMembre = random.sample(listeEtudiant,effectifComFraude)
        for membre in listeMembre:
            membre.statut = Etudiant.Statut.FUMEUR
            self.ajouterMembre(self.listeMembre,membre)

    def get_fournisseur (self):
        effectifComFraude = len(self.listeMembre)
        effectifFournisseur = int((2 * effectifComFraude) / 100) + 1
        fumeurs = [e for e in self.listeMembre if e.statut == Etudiant.Statut.FUMEUR]
        fournisseurs = random.sample(fumeurs,effectifFournisseur)
        for fournisseur in fournisseurs:
            fournisseur.statut = Etudiant.Statut.FOURNISSEUR
            self.ajouterMembre(self.listeFournisseur,fournisseur)

    def get_dealer (self):
        effectifComFraude = len(self.listeMembre)
        effectifDealer = int((7 * effectifComFraude) / 100) + 1
        fumeurs = [e for e in self.listeMembre if e.statut == Etudiant.Statut.FUMEUR]
        dealers = random.sample(fumeurs,effectifDealer)
        for dealer in dealers:
            dealer.statut = Etudiant.Statut.DEALER
            self.ajouterMembre (self.listeDealer,dealer)

    def get_fumeur (self):
        for etudiant in self.listeMembre:
            if etudiant.statut == Etudiant.Statut.FUMEUR:
                self.ajouterMembre (self.listeConsommateur,etudiant)

    def connecter (self,e1,e2,poids):
        if e1 != e2:
            if e1 not in self.grapheCom:
                self.grapheCom[e1] = {}
            if e2 not in self.grapheCom[e1]:
                self.grapheCom[e1][e2] = poids

    def connecter_fournisseur_dealer (self):
        effectifDealer = len(self.listeDealer)
        connectionMin = int((10 * effectifDealer) / 100) + 1
        connectionMax = int((20 * effectifDealer) / 100) + 1
        poidsMin = 8
        poidsMax = 10
        for fournisseur in self.listeFournisseur:
            nbConnection = random.randint(connectionMin,connectionMax)
            dealers = random.sample(self.listeDealer,nbConnection)
            for dealer in dealers:
                poids = random.randint(poidsMin,poidsMax)
                self.connecter(fournisseur,dealer,poids)
        for dealer in self.listeDealer:
            fournisseur = random.choice (self.listeFournisseur)
            poids = random.randint(poidsMin,poidsMax)
            self.connecter (fournisseur,dealer,poids)

    def connecter_dealer_consommateur (self):
        effectifConsommateur = len(self.listeConsommateur)
        connectionMin = 5
        connectionMax = 15
        poidsMin = 7
        poidsMax = 9
        for dealer in self.listeDealer:
            nbConnection = random.randint(connectionMin,connectionMax)
            consommateurs = random.sample(self.listeConsommateur,nbConnection)
            for consommateur in consommateurs:
                poids = random.randint(poidsMin,poidsMax)
                self.connecter (dealer,consommateur,poids)
        for consommateur in self.listeConsommateur:
            dealer = random.choice(self.listeDealer)
            poids = random.randint (poidsMin,poidsMax)
            self.connecter(dealer,consommateur,poids)

    def connecter_consommateur (self):
        poidsMin = 4
        poidsMax = 6
        for consommateur in self.listeConsommateur:
            nbConnection = random.randint(5,10)
            for i in range(nbConnection):
                poids = random.randint (poidsMin,poidsMax)
                ami = random.choice(self.listeConsommateur)
                self.connecter(consommateur,ami,poids)

    def creer_com (self,listeEtudiant):
        self.get_membre(listeEtudiant)
        self.get_fournisseur()
        self.get_dealer()
        self.get_fumeur()
        self.connecter_fournisseur_dealer()
        self.connecter_dealer_consommateur()
        self.connecter_consommateur ()

class ComSain:
    def __init__ (self):
        self.listeMembre = []
        self.grapheCom = {}

    def ajouterMembre (self,groupe,etudiant):
        if etudiant not in groupe:
            groupe.append(etudiant)

    def connecter (self,e1,e2,poids):
        if e1 != e2:
            if e1 not in self.grapheCom:
                self.grapheCom[e1] = {}
            if e2 not in self.grapheCom[e1]:
                self.grapheCom[e1][e2] = poids

    def get_membre (self,listeEtudiant):
        for etudiant in listeEtudiant:
            if etudiant.statut == Etudiant.Statut.NORMAL:
                self.ajouterMembre(self.listeMembre,etudiant)
            
    def connecter_membre (self):
        effectifMembre = len(self.listeMembre)
        connectionMin = 2
        connectionMax = 6
        poidsMin = 2
        poidsMax = 4
        for etudiant in self.listeMembre:
            nbConnection = random.randint(connectionMin,connectionMax)
            for i in range(nbConnection):
                poids = random.randint(poidsMin,poidsMax)
                ami = random.choice(self.listeMembre)
                self.connecter(etudiant,ami,poids)

    def creer_com (self,listeEtudiant):
        self.get_membre(listeEtudiant)
        self.connecter_membre()

class ComGeneral:
    def __init__ (self,listeEtudiant):
        self.listeEtudiant = listeEtudiant
        self.grapheCom = {}

    def connecter (self,e1,e2,poids):
        if e1 != e2:
            if e1 not in self.grapheCom:
                self.grapheCom[e1] = {}
            if e2 not in self.grapheCom[e1]:
                self.grapheCom[e1][e2] = poids

    def connect_fraud_sain (self,comFraud,comSain):
        effectifSain = len(comSain.listeMembre)
        sainMax = int((4 * effectifSain) / 100) + 1
        poidsMin = 1
        poidsMax = 3
        sain = random.sample(comSain.listeMembre,sainMax)
        for etudiant in sain:
            poids = random.randint (poidsMin,poidsMax)
            ami = random.choice(comFraud.listeConsommateur)
            self.connecter(etudiant,ami,poids)

    def connection_global (self):
        lienMax = int(len(self.listeEtudiant) / 50)
        poidsMin = 2
        poidsMax = 4
        for i in range(lienMax):
            etudiant1 = random.choice (self.listeEtudiant)
            etudiant2 = random.choice (self.listeEtudiant)
            poids = random.randint (poidsMin,poidsMax)
            self.connecter (etudiant1,etudiant2,poids)

    def simuler_graph (self):
        comFraude = ComFraude ()
        comFraude.creer_com (self.listeEtudiant)

        comSain = ComSain ()
        comSain.creer_com (self.listeEtudiant)

        self.grapheCom = {**comFraude.grapheCom,**comSain.grapheCom}
        self.connect_fraud_sain(comFraude,comSain)
        self.connection_global ()
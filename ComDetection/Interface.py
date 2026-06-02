from dash import Dash, html
import networkx as nx
import dash_cytoscape as cyto
import Etudiant
import Classification

class Interface:
    def __init__ (self,Graphe):
        self.style = []
        self.elements = []
        self.app = Dash ()
        self.define_style()
        self.define_nodes(Graphe.V,Graphe.E)
        self.define_edges(Graphe.E)

    def define_style (self):
        self.style = [
            {
                'selector':'edge',
                'style':{'line-color':'#aaaaaa',
                        'width':1}
            },
            {
                'selector':'node',
                'style':{'label':'data(label)',
                        'background-color':'red',
                        'color':'white',
                        'text-valign':'center',
                        'text-halign':'center',
                        'width':70,
                        'height':70}
            },       
            {
                'selector':'.rouge',
                'style':{'background-color':'red'}
            },
            {
                'selector':'.vert',
                'style':{'background-color':'green'}
            },
            {
                'selector':'.bleu',
                'style':{'background-color':'blue'}
            },
            {
                'selector':'.jaune',
                'style':{'background-color':'yellow'}
            },
            {
                'selector':'.noir',
                'style':{'background-color':'black'}
            },
            {
                'selector':'.blanc',
                'style':{'background-color':'white',
                          'color':'black'}
            },
            {
                'selector':'.violet',
                'style':{'background-color':'purple'}
            },
            {
                'selector':'.orange',
                'style':{'background-color':'orange'}
            },
            {
                'selector':'.marron',
                'style':{'background-color':'brown'}
            },
            {
                'selector':'.beige',
                'style':{'background-color':'beige'}
            },
            {
                'selector':'.gris',
                'style':{'background-color':'grey'}
            },
            {
                'selector':'.rose',
                'style':{'background-color':'pink'}
            },
        ]

    def calculer_positions(self,listeEtudiant, graphe):
        G = nx.DiGraph()
 
        for etudiant in listeEtudiant:
            G.add_node(etudiant.id)
 
        for source, voisins in graphe.items():
            for cible in voisins:
                G.add_edge(source.id, cible.id, weight=1)

        pos = nx.spring_layout(G, k=2.5, iterations=60, seed=42)

        scale = 3000
        positions = {
            node_id: {'x': float(coords[0]) * scale,
                      'y': float(coords[1]) * scale}
            for node_id, coords in pos.items()
        }
        return positions

    def define_nodes (self,listeEtudiant,graphe):
        positions = self.calculer_positions(listeEtudiant,graphe)
        classificateur = Classification.Classificateur()
        classificateur.V = listeEtudiant
        classificateur.E = graphe
        couleurs = classificateur.coloration()

        for etudiant in listeEtudiant:
            pos = positions.get(etudiant.id,{'x':0,'y':0})
            data = dict(data=dict(id=str(etudiant.id),label=str(etudiant.id)),position=pos,classes=couleurs[etudiant])
            self.elements.append(data)

    def define_edges (self,graph):
        for etudiant in graph:
            for voisin in graph[etudiant]:
                data = dict(data=dict(source=str(etudiant.id),target=str(voisin.id)))
                self.elements.append(data)

    def create_interface (self):
        print ("Visualisation....")
        import webbrowser
        webbrowser.open("http://127.0.0.1:8050") 
        self.app.layout = html.Div ([
        cyto.Cytoscape(
            id='reseau-etudiant-ankatso',
            layout={'name':'preset','nodeRepulsion':1000000,
                    'idealEdgeLength':100,
                    'idealElasticity':100,
                    'gravity':1,
                    'numIter':1000},
            style={'width':'100%','height':'1000px'},
            stylesheet=self.style,
            elements=self.elements
            )
        ])
        self.app.run(debug=True)
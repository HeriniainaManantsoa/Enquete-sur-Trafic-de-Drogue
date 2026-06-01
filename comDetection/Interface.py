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
        self.calculer_positions(Graphe.V,Graphe.E)
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
                        'text-halign':'center'}
            },
            {
                'selector':'.normal',
                'style':{'background-color':'green'}
            }
        ]

    def calculer_positions(self,listeEtudiant, graphe):
        G = nx.DiGraph()
 
        for etudiant in listeEtudiant:
            G.add_node(etudiant.id)
 
        for source, voisins in graphe.items():
            for cible in voisins:
                G.add_edge(source.id, cible.id, weight=1)
 
        # k contrôle l'espacement — augmente si les nœuds se chevauchent
        pos = nx.spring_layout(G, k=2.5, iterations=60, seed=42)
 
        # Mise à l'échelle vers les coordonnées Cytoscape (pixels)
        scale = 5000
        positions = {
            node_id: {'x': float(coords[0]) * scale,
                      'y': float(coords[1]) * scale}
            for node_id, coords in pos.items()
        }
        return positions

    def define_nodes (self,listeEtudiant,graphe):
        positions = self.calculer_positions(listeEtudiant,graphe)
        for etudiant in listeEtudiant:
            pos = positions.get(etudiant.id,{'x':0,'y':0})
            data = dict(data=dict(id=str(etudiant.id),label=str(etudiant.id)),position=pos)
            if etudiant.statut == Etudiant.Statut.NORMAL:
                data = dict(data=dict(id=str(etudiant.id),label=str(etudiant.id)),position=pos,classes='normal')
            self.elements.append(data)

    def define_edges (self,graph):
        for etudiant in graph:
            for voisin in graph[etudiant]:
                data = dict(data=dict(source=str(etudiant.id),target=str(voisin.id)))
                self.elements.append(data)

    def create_interface (self):
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
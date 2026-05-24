from dash import Dash, html
import dash_cytoscape as cyto
import Universite
import Simulateur
import Etudiant

class Interface:
    def __init__ (self):
        self.style = []
        self.elements = []
        self.app = Dash ()

    def define_style (self):
        self.style = [
            {
                'selector':'edge',
                'style':{'line-color':'blue','width':1}
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

    def define_nodes (self,listeEtudiant):
        for etudiant in listeEtudiant:
            data = dict(data=dict(id=str(etudiant.id),label=str(etudiant.id)))
            if etudiant.statut == Etudiant.Statut.NORMAL:
                data = dict(data=dict(id=str(etudiant.id),label=str(etudiant.id)),classes='normal')
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
            layout={'name':'cose','nodeRepulsion':1000000,
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
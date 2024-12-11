from graphviz import Digraph

# Ініціалізація графу
dot = Digraph('Class Diagram', format='png')
# Add DPI setting for higher resolution
dot.attr(dpi='300')
dot.attr(rankdir='TB')
# Add global font settings
dot.attr('node', shape='record', style='rounded', fontsize='14', fontname='Arial')
dot.attr('edge', fontsize='12', fontname='Arial')
dot.graph_attr['splines'] = 'ortho'
dot.graph_attr['nodesep'] = '0.8'
dot.graph_attr['ranksep'] = '1.0'
# Increase size of the entire graph
dot.attr(size='8,8')  # width,height in inches

# Додавання класів
dot.node('Customer', '''{ Customer |
+ name: string\l
+ contact_info: string\l
+ company_type: string\l|
+ placeOrder()\l
+ editDetails()\l}''')

dot.node('AdCampaign', '''{ AdCampaign |
+ name: string\l
+ budget: float\l
+ goal: string\l
+ period: string\l|
+ launchCampaign()\l
+ analyzeResults()\l}''')

dot.node('Employee', '''{ Employee |
+ name: string\l
+ position: string\l
+ salary: float\l|
+ assignTask()\l
+ editTask()\l}''')

dot.node('Report', '''{ Report |
+ name: string\l
+ creation_date: date\l
+ results: string\l|
+ createReport()\l
+ viewReport()\l}''')

dot.node('Manager', '''{ Manager |
|
(Inherits from Employee)\l}''')

# Зв'язки між класами
dot.edge('Customer', 'AdCampaign', label='places')
dot.edge('AdCampaign', 'Employee', label='manages')
dot.edge('AdCampaign', 'Report', label='has')
dot.edge('Manager', 'Employee', label='inherits', arrowhead='onormal')

# Збереження та візуалізація
dot.render('class_diagram', view=True)
print("Diagram generated: class_diagram.png")

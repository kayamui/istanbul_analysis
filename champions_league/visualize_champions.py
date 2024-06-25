def visualize_champions():

    """
    Takes a list of the names and the protocols which were sent to the command center not in time and creates a graph of each personnel,
    the graph shows the name of the staff in x axis, the amount of the problematic forms in y axis and the protocols and the dates in the hover.
    """
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    import plotly.express as px
    import os

    import pandas as pd
    import numpy as np


    #Finding the path of the file named most_known_names
    content = [item for item in os.listdir() if 'most_known_names' in item]
    content_path= os.path.join(os.getcwd(), content[0])
    most_known_names= pd.read_excel(content_path)

    #Creates a column just for showing the forms month
    most_known_names['Vaka Ayı'] = most_known_names['Vaka Tarihi'].dt.month

    #Added a value 1 for each form and summed up them by grouping by the names
    most_known_names['Miktar'] = 1
    most_known_names['Vaka Sayısı'] = most_known_names.groupby(['Personel Adı'])['Miktar'].transform('sum')

    #starting the visualization
    df = most_known_names.sort_values(by =['Vaka Sayısı', 'Vaka Ayı'])
    fig = px.bar(df, x="Personel Adı", y="Miktar", color="Vaka Ayı",barmode='stack',hover_data= ['KKM Protokol', 'Vaka Tarihi'], title="Vaka Formunu Geç Gönderenler")
    return fig.show()
visualize_champions()
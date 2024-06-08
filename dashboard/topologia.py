import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns  
import matplotlib.pyplot as plt 
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import json
import altair as alt
from streamlit_option_menu import option_menu
from sklearn.metrics import mean_squared_error, mean_absolute_error

def topologia():
        cenario = option_menu(None, ["Cenário Um", "Cenário Dois", "Cenário Três"], 
        icons=['bi bi-tv', 'bi bi-tv','bi bi-tv'], 
        menu_icon="cast",
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important"},
            "nav-link": {"font-size": "20px", "text-align": "center", "margin":"0px", "wigth": "10px"},
            "nav-link-selected": {"background-color": "#1564c0"},
        })
        data = pd.read_csv('./Dados/Dados_Sudeste-Centro-Oeste_mensal.csv')
        data['DATA'] = pd.to_datetime(data['DATA'])
        fim = pd.to_datetime('2020-12-01')
        data_limite = data.loc[data['DATA'] <= fim]
        data_dict = {
                    "PLD_SECO": "Preço das Liquidações das Diferenças",
                    "EA_SECO": "Energia Armazenada",
                    "TER": "Geração Térmica",
                    "HID": "Geração Hídrica",
                    "LPC_SECO": "Preço"
                }
        df = pd.DataFrame(list(data_dict.items()), columns=["Variável", "Descrição"])


        results = pd.read_csv('./Dados/resultados/resultados/preco/Expe_1/resultados_previsao.csv')
        results['Data'] = pd.to_datetime(results['Data'])
        results = results.loc[results['Data'] <= fim]

        results2 = pd.read_csv('./Dados/resultados/resultados/preco/Expe_2/resultados_previsao_3_anos_2_exper.csv')
        results2['Data'] = pd.to_datetime(results2['Data'])
        results2 = results2.loc[results2['Data'] <= fim]

        results3 = pd.read_csv('./Dados/resultados/resultados/preco/Expe_3_melhor/resultados_previsao_3_anos_INf_HI_PLD_AE.csv')
        results3['Data'] = pd.to_datetime(results3['Data'])
        results3 = results3.loc[results3['Data'] <= fim]


        def load_inference_data(file_path):
            with open(file_path, 'r') as file:
                inference_data = json.load(file)
            return inference_data

        topology_data = load_inference_data('./Dados/ind_006.json')
        topology_data2 = load_inference_data('./Dados/resultados/resultados/preco/Expe_2/ind_005.json')

        if cenario == "Cenário Um":

            tab1, tab2 = st.tabs(["Topologia", "Previsão"])

            with tab1:
                c3, c4, c5= st.columns([2,1,1])
                with st.container():
                    c3.write("")
                    c4.write("")

                with c3:
                    G = nx.DiGraph()

                    # # Adicionar nós e arestas ao grafo
                    for edge in topology_data["topologia"]:
                        G.add_edge(edge[0], edge[1])

                    # Layout do grafo
                    pos = nx.spring_layout(G, dim=3, seed=41)  # Layout usando algoritmo Spring em 3D

                    # Criar os nós do grafo
                    node_x = []
                    node_y = []
                    node_z = []
                    for node in G.nodes:
                        x, y, z = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_z.append(z)

                    # Criar as arestas do grafo
                    edge_x = []
                    edge_y = []
                    edge_z = []
                    for edge in G.edges():
                        x0, y0, z0 = pos[edge[0]]
                        x1, y1, z1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        edge_z.extend([z0, z1, None])

                    # Criar a figura
                    fig = go.Figure()

                    
                    # # Adicionar arestas à figura
                    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='limegreen', width=0.8), hoverinfo='none'))

                    # Adicionar nós à figura
                    fig.add_trace(go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers+text', text=list(G.nodes()), 
                                            textposition="middle center", marker=dict(color='limegreen', size=40)))

                    # # Configurar layout da figura
                    fig.update_layout(title=f"Topologia: {topology_data['name']}", titlefont_size=12, showlegend=False, hovermode='closest', 
                                    margin=dict(b=20,l=5,r=5,t=40), 
                                    annotations=[ dict(text="", showarrow=False, xref="paper", yref="paper", x=0.005, y=-0.002 ) ], scene=dict(xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

                    frames = []
                    for i in range(36):
                        new_x = node_x + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em x
                        new_y = node_y + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em y
                        new_z = node_z + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em z
                        frames.append(go.Frame(data=[go.Scatter3d(x=new_x, y=new_y, z=new_z, mode='markers+text', text=list(G.nodes()), textposition="middle center", marker=dict(color="skyblue", size=15))]))

                    fig.frames = frames

                    # Exibir a figura
                    st.plotly_chart(fig)
                with c5:
                    st.json(topology_data)
                with c4:
                    st.write("Dicionário de Dados:")
                    st.dataframe(df.set_index('Variável'))

            with tab2:
                st.write('##### Nesse cenário foi inserido aleatoriamento inferências na variável Energia Armazenada. Os dados de Energia Armazendo foram categorizados em: Nível Baixo, Nível Médio e Nível Alto As inferências foram sempre na categoria Alto para os meses de Dezembro/2019 até Novembro/2020.')
                          
                confidence_factor = 0.2
                results['lower_lim'] = results['mean'] - ((results['mean'] - results['lower_lim']) * confidence_factor)
                results['upper_lim'] = results['mean'] + ((results['upper_lim'] - results['mean']) * confidence_factor) 
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data_limite['DATA'], y=data_limite['LPC_SECO'], mode='lines', name='Real'))

                # Adicionar os limites superior e inferior
                fig.add_trace(go.Scatter(x=results['Data'], y=results['upper_lim'], mode='lines', 
                                            line=dict(color='rgba(0,0,0,0)', width=1),
                                        showlegend=False))
                fig.add_trace(go.Scatter(x=results['Data'], y=results['lower_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Inferior'))
                fig.add_trace(go.Scatter(x=results['Data'], y=results['upper_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Superior'))
                fig.add_trace(go.Scatter(x=results['Data'], y=results['mean'], mode='lines', fillcolor='rgba(0,100,80,0.2)',
                                        name='Previsto'))

                fig.update_layout(title='Intervalo de Confiança',
                                xaxis_title='Período',
                                yaxis_title='Valor (R$)',
                                width=1275)
                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)

        if cenario == "Cenário Dois":
            tab1, tab2 = st.tabs(["Topologia", "Previsão"])

            with tab1:
                c3, c4, c5= st.columns([2,1,1])
                with st.container():
                    c3.write("")
                    c4.write("")

                with c3:
                    G = nx.DiGraph()

                    # # Adicionar nós e arestas ao grafo
                    for edge in topology_data2["topologia"]:
                        G.add_edge(edge[0], edge[1])

                    # Layout do grafo
                    pos = nx.spring_layout(G, dim=3, seed=41)  # Layout usando algoritmo Spring em 3D

                    # Criar os nós do grafo
                    node_x = []
                    node_y = []
                    node_z = []
                    for node in G.nodes:
                        x, y, z = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_z.append(z)

                    # Criar as arestas do grafo
                    edge_x = []
                    edge_y = []
                    edge_z = []
                    for edge in G.edges():
                        x0, y0, z0 = pos[edge[0]]
                        x1, y1, z1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        edge_z.extend([z0, z1, None])

                    # Criar a figura
                    fig = go.Figure()

                    # # Adicionar arestas à figura
                    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='limegreen', width=0.8), hoverinfo='none'))

                    # Adicionar nós à figura
                    fig.add_trace(go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers+text', text=list(G.nodes()), 
                                            textposition="middle center", marker=dict(color='limegreen', size=40)))

                    # # Configurar layout da figura
                    fig.update_layout(title=f"Topologia: {topology_data2['name']}", titlefont_size=12, showlegend=False, hovermode='closest', 
                                    margin=dict(b=20,l=5,r=5,t=40), 
                                    annotations=[ dict(text="", showarrow=False, xref="paper", yref="paper", x=0.005, y=-0.002 ) ], scene=dict(xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

                    frames = []
                    for i in range(36):
                        new_x = node_x + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em x
                        new_y = node_y + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em y
                        new_z = node_z + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em z
                        frames.append(go.Frame(data=[go.Scatter3d(x=new_x, y=new_y, z=new_z, mode='markers+text', text=list(G.nodes()), textposition="middle center", marker=dict(color="skyblue", size=15))]))

                    fig.frames = frames

                    # Exibir a figura
                    st.plotly_chart(fig)
                with c5:
                    st.json(topology_data2)
                with c4:
                    st.write("Dicionário de Dados:")
                    st.dataframe(df.set_index('Variável'))

            with tab2:
                st.write('##### Nesse Cenário foi realizado inferências nas variáveis Geração Hídrica e Energia Armazenada. Os dados de Energia Armazendo e Geração Hídrica foram categorizados em: Nível Baixo, Nível Médio e Nível Alto, Para o mes de Novembro/2018 foi inferido que o Nível da Energia Armazendada e a Geração Hídrica estava Médio. Para o segundo semestre/2020 foi inserido que o nível da Energia Armazendas estava Alto e a Nível da Geração Hídrica estava modificando de Médio para  Alto.')

                '''
                confidence_factor = 0.3
                results2['lower_lim'] = results2['mean'] - ((results2['mean'] - results2['lower_lim']) * confidence_factor)
                results2['upper_lim'] = results2['mean'] + ((results2['upper_lim'] - results2['mean']) * confidence_factor) 
                '''
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data_limite['DATA'], y=data_limite['LPC_SECO'], mode='lines', name='Real'))

                # Adicionar os limites superior e inferior
                fig.add_trace(go.Scatter(x=results2['Data'], y=results2['upper_lim'], mode='lines', 
                                            line=dict(color='rgba(0,0,0,0)', width=1),
                                        showlegend=False))
                fig.add_trace(go.Scatter(x=results2['Data'], y=results2['lower_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Inferior'))
                fig.add_trace(go.Scatter(x=results2['Data'], y=results2['upper_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Superior'))
                fig.add_trace(go.Scatter(x=results2['Data'], y=results2['mean'], mode='lines', fillcolor='rgba(0,100,80,0.2)',
                                        name='Previsto'))

                fig.update_layout(title='Intervalo de Confiança',
                                xaxis_title='Período',
                                yaxis_title='Valor (R$)',
                                width=1275)
                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)

        if cenario == "Cenário Três":
            tab1, tab2 = st.tabs(["Topologia", "Previsão"])

            with tab1:
                c3, c4, c5= st.columns([2,1,1])
                with st.container():
                    c3.write("")
                    c4.write("")

                with c3:
                    G = nx.DiGraph()

                    # # Adicionar nós e arestas ao grafo
                    for edge in topology_data["topologia"]:
                        G.add_edge(edge[0], edge[1])

                    # Layout do grafo
                    pos = nx.spring_layout(G, dim=3, seed=41)  # Layout usando algoritmo Spring em 3D

                    # Criar os nós do grafo
                    node_x = []
                    node_y = []
                    node_z = []
                    for node in G.nodes:
                        x, y, z = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_z.append(z)

                    # Criar as arestas do grafo
                    edge_x = []
                    edge_y = []
                    edge_z = []
                    for edge in G.edges():
                        x0, y0, z0 = pos[edge[0]]
                        x1, y1, z1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        edge_z.extend([z0, z1, None])

                    # Criar a figura
                    fig = go.Figure()

                    # # Adicionar arestas à figura
                    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='limegreen', width=0.8), hoverinfo='none'))

                    # Adicionar nós à figura
                    fig.add_trace(go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers+text', text=list(G.nodes()), 
                                            textposition="middle center", marker=dict(color='limegreen', size=40)))

                    # # Configurar layout da figura
                    fig.update_layout(title=f"Topologia: {topology_data['name']}", titlefont_size=12, showlegend=False, hovermode='closest', 
                                    margin=dict(b=20,l=5,r=5,t=40), 
                                    annotations=[ dict(text="", showarrow=False, xref="paper", yref="paper", x=0.005, y=-0.002 ) ], scene=dict(xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

                    frames = []
                    for i in range(36):
                        new_x = node_x + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em x
                        new_y = node_y + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em y
                        new_z = node_z + np.sin(i * 100 * np.pi / 180) * 0.1  # Movimento sinusoidal em z
                        frames.append(go.Frame(data=[go.Scatter3d(x=new_x, y=new_y, z=new_z, mode='markers+text', text=list(G.nodes()), textposition="middle center", marker=dict(color="skyblue", size=15))]))

                    fig.frames = frames

                    # Exibir a figura
                    st.plotly_chart(fig)
                with c5:
                    st.json(topology_data)
                with c4:
                    st.write("Dicionário de Dados:")
                    st.dataframe(df.set_index('Variável'))

            with tab2:
                st.write('##### Nesse cenário foi realizado inferências nas variáveis Preço de Liquidação das Diferenças, Energia Armazenada e Geração Hídrica. Os dados de Energia Armazendo, Geração Hídrica e Preço de Liquidação das Diferenças foram categorizados em: Nível Baixo, Nível Médio e Nível Alto.')

                confidence_factor = 0.3
                results3['lower_lim'] = results3['mean'] - ((results3['mean'] - results3['lower_lim']) * confidence_factor)
                results3['upper_lim'] = results3['mean'] + ((results3['upper_lim'] - results3['mean']) * confidence_factor) 
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data_limite['DATA'], y=data_limite['LPC_SECO'], mode='lines', name='Real'))

                # Adicionar os limites superior e inferior
                fig.add_trace(go.Scatter(x=results3['Data'], y=results3['upper_lim'], mode='lines', 
                                            line=dict(color='rgba(0,0,0,0)', width=1),
                                        showlegend=False))
                fig.add_trace(go.Scatter(x=results3['Data'], y=results3['lower_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Inferior'))
                fig.add_trace(go.Scatter(x=results3['Data'], y=results3['upper_lim'], mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
                                        name='Limite Superior'))
                fig.add_trace(go.Scatter(x=results3['Data'], y=results3['mean'], mode='lines', fillcolor='rgba(0,100,80,0.2)',
                                        name='Previsto'))

                fig.update_layout(title='Intervalo de Confiança',
                                xaxis_title='Período',
                                yaxis_title='Valor (R$)',
                                width=1275)
                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)
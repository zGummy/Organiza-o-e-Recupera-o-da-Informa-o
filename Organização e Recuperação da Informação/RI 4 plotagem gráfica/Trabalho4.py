# -------------------------------->BIBLIOTECAS<--------------------------------
import sys
import matplotlib.pyplot as plt
# -----------------------------------------------------------------------------

'''
Este trabalho consiste no cálculo
e plotagem do gráfico e precisão
e revocação média para uma coleçãode
referência.
'''

#------------------------------->Classe Plotagem<--------------------------------
class cPlot:

        #ler arquivo
        def readFile():
                file = open(sys.argv[1], 'r').readlines()
                return file

        #representação x e y
        def graphicRepresentation(query):
                x = query.keys()
                y = query.values()
                plt.plot(x, y)
                plt.show()

        #calcula a porcentagem relevante
        def calculate(relevant, query):
                first_correlation = {}
                final_correlation = {}
                total_counter = 0
                relevant_counter = 0
                
                for doc in query:
                        total_counter += 1

                        if doc in relevant:
                                relevant_counter += 1
                                recall = relevant_counter/len(relevant) * 100
                                precision = relevant_counter/total_counter * 100
                                first_correlation[recall] = precision

                print(first_correlation)
                percentage = 0
                while percentage <= 100:
                        values = []

                        for value in first_correlation.keys():
                                if value >= percentage:
                                        values.append(first_correlation[value])

                        if len(values) > 0:
                                final_correlation[percentage] = max(values)
                        else:
                                final_correlation[percentage] = 0
                        percentage = percentage + 10                
                return final_correlation

        #Cálculo e plotagem do gráfico
        def retriveInfo():
                lines = cPlot.readFile()              
                n = int(lines[0])
                
                queries = {}
                i = 1

                while i <= n:
                        relevant = lines[i].replace("\n", "").rsplit(" ")
                        query = lines[i + n].replace("\n", "").rsplit(" ")                        
                        queries[i] = cPlot.calculate(relevant, query)
                        cPlot.graphicRepresentation(queries[i])
                        i += 1

                average = {}  
                percentage = 0

                while percentage <= 100:
                        summation = 0.0
                        for key in queries.keys():
                                summation += queries[key][percentage]
                        average[percentage] = round(summation/n, 2)
                        percentage += 10       

                cPlot.graphicRepresentation(average)                
                indexFile = open("media.txt", 'w')

                for key in average.keys():
                        indexFile.write(str(round(average[key]/100, 2)) + " ")        
        
# ----------------------------------------------------------------------------



# ----------------------------------->MAIN<------------------------------------
if __name__ == "__main__":
    cPlot.retriveInfo()
    '''
    Para executar o programa, use no terminal:
    py   trabalho04.py   referencia.txt
    '''
# ----------------------------------------------------------------------------
#----------------------------------------->README<-------------------------------------------------
#Tentei rodar o corretor do python 3.9, mas ficou dando esse erro, mesmo na mesma versão
#
#C:\Users\b0car\Desktop\ultimao>py waxm_corretor_pagerank.pyc base0 T05Final.py
#Rodando meu programa
#Links de origem:  {}
#
#Links de destino:
#Traceback (most recent call last):
#  File "waxm_corretor_page_rank.py", line 166, in <module>
#  File "waxm_pagerank.py", line 147, in sample_pagerank
#  File "C:\Users\b0car\AppData\Local\Programs\Python\Python39\lib\random.py", line 346, in choice
#    return seq[self._randbelow(len(seq))]
#IndexError: list index out of range


#Apenas consegui rodar com a base, só que sem o corretor
#py T05Final.py base0
#'''

# -------------------------------->BIBLIOTECAS<--------------------------------
import sys
import random
from pathlib import Path
# -----------------------------------------------------------------------------

#-------------------------------->Classe Rank<---------------------------------

class pageRank:

    #Abrir arquivo
    def openFile():
        file = Path(sys.argv[1])
        return file

    #Salvar o grafo em um arquivo
    def setGraph(graph, name):

        fileArq = open(name,'w')
        nodes = list(graph.keys())
        nodes.sort()
        for i in nodes:
            fileArq.write(str(i)+':')
            for j in graph[i]:
                fileArq.write(' '+str(j))
            fileArq.write('\n')
        fileArq.close()

    #Salvar o pagerank em um arquivo
    def savePageRank(pr,name):        
        savePageRank = open(name,'w')
        files = list(pr.keys())
        files.sort()
        for i in files:
            savePageRank.write(str(i)+' '+str(pr[i])+'\n')
        savePageRank.close()

    #Ranquear
    def ranked():
        file = pageRank.openFile()
        arqs = set()
        graphOut = {}
        graphIn = {}

        for f in [x for x in file.iterdir()]:
            fileName = str(f)[len(sys.argv[1])+1:]
            arqs.add(fileName)
            graphOut[fileName] = set()
            graphIn[fileName] = set()

        for f in [x for x in file.iterdir()]:
            fileName = str(f)[len(sys.argv[1])+1:]
            document = open(f,'r')
            for i in document:                
                j = 0
                while j<len(i):
                    pos = i.find('<a href=',j)                    
                    if pos==-1:
                        break                    
                    temp=''
                    j = pos+1
                    pos += len('<a href=')+1      
                    while(i[pos]!="'" and i[pos]!='"'):
                        temp+=i[pos]
                        pos+=1
                    
                    if temp in arqs and temp!=fileName:
                        if fileName in graphOut:
                            graphOut[fileName].add(temp)
                        else:
                            graphOut[fileName] = {temp}

        for i in arqs:
            for j in graphOut:
                if i in graphOut[j]:
                    if i in graphIn:
                        graphIn[i].add(j)
                    else:
                        graphIn[i] = {j}

        pageRank.calculateRank(arqs,graphOut,graphIn)       

    #Mostrar na tela os resultados
    def show(graphIn,graphOut,numberV,page):
            pageRank.setGraph(graphIn,'links_destino.txt')
            pageRank.setGraph(graphOut,'links_origem.txt')
            pageRank.savePageRank(numberV,'pg_amostragem.txt')
            pageRank.savePageRank(page,'pg_iterativo.txt')

    #Calcular o ranqueamento das amostragens
    def calculateRank(arqs,graphOut,graphIn):            
            aux = 0
            index = list(arqs)[0]
            numberV = {}
            randomTransitions = 10000  #Transições aleatorias
            while aux < randomTransitions:
                rand = random.random()
                
                if index in numberV:
                    numberV[index]+=1
                else:
                    numberV[index]=1

                if rand >= .85 or len(graphOut[index])==0:
                    index = list(arqs)[random.randrange(0,len(arqs))]
                else:
                    index = list(graphOut[index])[random.randrange(0,len(graphOut[index]))]
                aux+=1

            for i in numberV:
                numberV[i] = numberV[i]/randomTransitions
            pageRank.iterativePageRank(numberV,arqs,graphIn,graphOut)            

    #Calcular o pagerank iterativo
    def iterativePageRank(numberV,arqs,graphIn,graphOut):
            page = {}
            otherPage = {}
            for i in arqs:
                page[i] = 1/len(arqs)

            while True:
                fixed = 0.85
                for i in page:
                    otherPage[i]=page[i]
               
                count = 0
                for i in page:
                    scount = 0
                    if i in graphIn:
                        for j in graphIn[i]:
                            scount+=(otherPage[j]/len(graphOut[j]))
                    page[i] = (1-fixed)/len(arqs)+fixed*scount
                    count += page[i]
                for i in page:
                    page[i] = page[i]/count
                flag = True
                for i in page:
                   
                    if abs(otherPage[i]-page[i])>10**-6:
                        flag = False
                        break
                if flag:
                    break            
            pageRank.show(graphIn,graphOut,numberV,page)
# -----------------------------------------------------------------------------

# ----------------------------------->MAIN<------------------------------------
if __name__ == "__main__":    
    #Para rodar o arquivo, utilize o terminal
    #    py T05Final.py base0   
    #    py waxm_corretor_pagerank.pyc base0 T05Final.py
    pageRank.ranked()    
# ----------------------------------------------------------------------------
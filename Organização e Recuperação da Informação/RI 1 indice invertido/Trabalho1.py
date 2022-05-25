#-------------------------------->BIBLIOTECAS<--------------------------------
import sys                                           
import nltk                                          
import pickle
                                                
from nltk.corpus import stopwords                    
from nltk.tag import UnigramTagger   
#-----------------------------------------------------------------------------

#---------------------------------->CLASSE<-----------------------------------
class InvertedIndex():    

    def startInvertedIndex():#Inicia o indice invertido (o que estava antes no trabalho 1 na Main)
        uniTagger = "trained_tagger.bin"
        u_tagger = None
        try:
            u_tagger = pickle.load(open(uniTagger, "rb"))
        except:
            print("Loading... this may take a while :)")
            u_tagger = nltk.tag.UnigramTagger(nltk.corpus.mac_morpho.tagged_sents())
            pickle.dump(u_tagger, open(uniTagger, "wb"))
        cont = 1
        dic = {} #dic[number of a document][root word] = number of occurances of that root word in that document
        new_dictionary = {} #new_dictionary[root word] = ['number of a document, number of occurances of that root word in that document']
        
        baseFile = open(sys.argv[1], 'r', encoding='utf8')
        lines = baseFile.readlines()
        for line in lines:    
            subfile = open(line.strip(), 'r', encoding='utf8')
            sublines = subfile.read().lower()
            #If you want to see the filtering of the tokens step by step, uncomment the printTokensEvolution function
            finalTokens = InvertedIndex.removeSuffix(InvertedIndex.removeStopwords(InvertedIndex.getFilteredTokens(InvertedIndex.getTokens(sublines)), u_tagger))
            dic[cont] = InvertedIndex.createSubDic(finalTokens)
           
            cont += 1
        return InvertedIndex.createInvertedIndex(dic)

    def getTokens(sublines):#Pega os tokens
        return nltk.word_tokenize(sublines)

    def getFilteredTokens(tokens):#Filtra os espaços e pontuações
        punctuation = [".","..","...", ",", "!", "?", " "]
        novoToken = [] #Salva os tokens sem pontuação e sem espaços
        for word in tokens:
            if word not in punctuation:
                novoToken.append(word)
        return novoToken

    def removeStopwords(novoToken, uniTagger):#Filtra as stopwords
        notAlowed = ["PREP", "ART", "KC", "KS"]
        novo_novoToken = [] #Salvar os tokens do novoToken sem as stopwords
        for token in novoToken:
            if token not in stopwords.words("portuguese"):
                novo_novoToken.append(token)
                
        novo_novoToken2 = [] #Salva os tokens com o filtrados
        for token in uniTagger.tag(novo_novoToken):
            if token[1] not in notAlowed:
                novo_novoToken2.append(token[0])
        return novo_novoToken2

    def removeSuffix(novo_novoToken):#Filtra os sufixos
        stemmer = nltk.stem.RSLPStemmer()
        NovoDoNovo_novoToken = [] #NovoDoNovo_novoToken -> Salvar os tokens do novo_novoToken sem os sufixos
        for token in novo_novoToken:
            NovoDoNovo_novoToken.append(stemmer.stem(token))
        return NovoDoNovo_novoToken

    def createSubDic(NovoDoNovo_novoToken):#Retorna um novo dicionário com todos os tratamentos filtrados
        dic = {}
        for token in NovoDoNovo_novoToken:
            if token not in dic:
                dic[token] = 1
            else:
                dic[token] += 1
        return dic

    def createInvertedIndex(dic):#Cria e retorna o indice invertido
        setOfTokens = set()
        for subdic in dic:
            for token in dic[subdic]:
                if token not in setOfTokens:
                    setOfTokens.add(token)
                    
        invertedIndex = str()
        for token in sorted(setOfTokens):
            intermediateList = list()
            for subdic in dic.keys():
                for subtoken in dic[subdic].keys():
                    if token == subtoken:
                        intermediateList.append("{},{}".format(subdic, dic[subdic][subtoken]))
            invertedIndex = invertedIndex + "{}: {}\n".format(token, " ".join(intermediateList))    
        return invertedIndex
    
#------------------------------>Modelo Booleano<------------------------------
    def startBooleanModel(new_dictionary):
        queryFile = open(sys.argv[2], 'r', encoding='utf8')
        query = queryFile.readline().lower()
        
        print("======")
        print("Query:")
        print("======")
        print(query)
        
        queryA = []
        print("===========")
        print("Subqueries:")
        print("===========")
        for subquery in query.split("|"):
            print(subquery)
            queryA.append(subquery.split("&"))
            
        finalResult = []
        for subquery in queryA: 
            finalResult.append(InvertedIndex.levelOne(subquery, new_dictionary))

        ultimateResult = finalResult[0]
        print("=====================")
        print("Sets (Intersections):")
        print("=====================")
        for item in finalResult:
            print(item)
            ultimateResult = ultimateResult.union(item)
        
        print("================")
        print("Result (Unions):")
        print("================")
        print(sorted(ultimateResult))
        
        indexFile = open("resposta.txt", 'w')
        indexFile.write(str(len(ultimateResult)) + "\n")
        for item in sorted(ultimateResult):
            indexFile.write(str(item) + "\n")    
        print("\nAll right! open resposta.txt file and see the result!\n")
    
    def levelOne(subquery, new_dictionary):
        queryB = []
        for token in subquery:
            queryB.append(token.replace(" ", "").replace("\n", ""))
        
        result = InvertedIndex.levelTwo(queryB, new_dictionary)
        if result == []:
            intermediateResult = set()
        else:
            intermediateResult = result[0]
        
        for item in result:
            intermediateResult = intermediateResult.intersection(item)
            
        return intermediateResult
    
    def levelTwo(subquery, new_dictionary):
        stemmer = nltk.stem.RSLPStemmer()
        lines = open(sys.argv[1], 'r', encoding='utf8').readlines()
        
        result = [] 
        hasNot = False
        for token in subquery: 
            resultSet = set() 
            if token[0] == "!":
                token = token.rsplit("!")[1] 
                hasNot = True
            if  token not in stopwords.words("portuguese") and new_dictionary.get(stemmer.stem(token), 0) != 0:
                sub_dictionary = new_dictionary[stemmer.stem(token)] 
                for item in sub_dictionary:
                    file_number = int(item.rsplit(",")[0])
                    file_name = lines[file_number - 1]
                    resultSet.add(file_name.replace("\n", ""))
                if hasNot == False:
                    result.append(resultSet)
                else:
                    fullSet = set()
                    counter = 1
                    while counter <= len(lines):
                        file_name = lines[counter - 1]
                        fullSet.add(file_name.replace("\n", ""))
                        counter = counter + 1
                    result.append(fullSet.difference(resultSet))
                    hasNot = False
        return result

#-----------------------------------------------------------------------------
        
#----------------------------------->MAIN<------------------------------------
def main():
    #Inicio das variáveis
    indice = InvertedIndex    
    indice.startBooleanModel(indice.startInvertedIndex())
#----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
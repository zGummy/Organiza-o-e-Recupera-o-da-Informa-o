# -------------------------------->BIBLIOTECAS<--------------------------------
import sys
import nltk
import pickle

from nltk.corpus import stopwords
from nltk.tag import UnigramTagger

from math import log10
from math import sqrt
# -----------------------------------------------------------------------------

# ------------------------------->CLASSES<-------------------------------------

# ---------------------------->Inverted Index<---------------------------------
class InvertedIndex:
    def startInvertedIndex(baseFile):
        counter = 1
        dictionary = {} 
        
        for line in baseFile:  
            subfile = open(line.strip(), 'r', encoding='utf8').read().lower()
            
            finalTokens = InvertedIndex.removeSuffix(InvertedIndex.removeStopwords(InvertedIndex.getFilteredTokens(InvertedIndex.getTokens(subfile))))
            dictionary[counter] = InvertedIndex.creatingSubDictionary(finalTokens)
            
            counter += 1

        return InvertedIndex.creatingInvertedIndex(dictionary)

    def creatingInvertedIndex(dictionary):
        setOfTokens = set()
        for subdictionary in dictionary:
            for token in dictionary[subdictionary]:
                if token not in setOfTokens:
                    setOfTokens.add(token)
                    
        invertedIndex = str()
        newDictionary = {}
        for token in sorted(setOfTokens):
            intermediateList = list()
            for subdictionary in dictionary.keys():
                for subtoken in dictionary[subdictionary].keys():
                    if token == subtoken:
                        intermediateList.append("{},{}".format(subdictionary, dictionary[subdictionary][subtoken]))
                        newDictionary[token] = intermediateList
            invertedIndex = invertedIndex + "{}: {}\n".format(token, " ".join(intermediateList))
            
        indexFile = open("indice.txt", 'w')
        indexFile.write(invertedIndex)
        return newDictionary


    def getTokens(sublines): # Pega os tokens
        return nltk.word_tokenize(sublines)

    def getFilteredTokens(tokens): # Filtra os espaços e pontuações  
        punctuation = [".","..", "...", ",", "!", "?", " ", "\n"]
        newtokens = [] # Salva os tokens sem pontuação e sem espaços
        for word in tokens:
            if word not in punctuation:
                newtokens.append(word)
        return newtokens

    def removeStopwords(newtokens):
        loaded_u_tagger = "trained_tagger.bin"
        u_tagger = None
        try:
            u_tagger = pickle.load(open(loaded_u_tagger, "rb"))
        except:
            
            u_tagger = nltk.tag.UnigramTagger(nltk.corpus.mac_morpho.tagged_sents())
            pickle.dump(u_tagger, open(loaded_u_tagger, "wb"))
            
        notAlowed = ["PREP", "ART", "KC", "KS"]
        novo_novoToken = []  # Salvar os tokens do novo_novoToken sem as stopwords
        for token in newtokens:
            if token not in stopwords.words("portuguese"):
                novo_novoToken.append(token)
                
        novo_novoToken2 = [] # Salva os tokens com o filtrados
        for token in u_tagger.tag(novo_novoToken):
            if token[1] not in notAlowed:
                novo_novoToken2.append(token[0])
        return novo_novoToken2

    def removeSuffix(novo_novoToken):
        stemmer = nltk.stem.RSLPStemmer()
        NovoDoNovo_novoToken = [] # NovoDoNovo_novo_novoToken -> Salvar os tokens do novo_novo_novoToken sem os sufixos
        for token in novo_novoToken:
            NovoDoNovo_novoToken.append(stemmer.stem(token))
        return NovoDoNovo_novoToken

    def creatingSubDictionary(NovoDoNovo_novoToken): # Retorna um novo dicionário com todos os tratamentos filtrados
        dictionary = {}
        for token in NovoDoNovo_novoToken:
            if token not in dictionary:
                dictionary[token] = 1
            else:
                dictionary[token] += 1
        return dictionary

    
# ---------------------------------->VECTOR Model<-----------------------------------
class VectorModel:   
    def idf(numberOfFiles, frequency):
        if frequency > 0:
            return log10(numberOfFiles/frequency)
        else:
            return 0.0

    def tf(numberOfOccurences):
        return 1 + log10(numberOfOccurences)

    def startWeighting(invertedIndex, numberOfFiles, lines):
        counter = 1
        weights = {}
        
        indexFile = open("pesos.txt", 'w')
        while counter <= numberOfFiles:
            file_name = lines[counter - 1].replace("\n", "")
            #ZA WARUDO
            weights[file_name] = {}
            for token in invertedIndex:
                for item in invertedIndex[token]:
                    if int(item.rsplit(",")[0]) == counter:
                        numberOfOccurences = int(item.rsplit(",")[1])
                        frequency = len(invertedIndex[token])
                        tfidf = VectorModel.tf(numberOfOccurences) * VectorModel.idf(numberOfFiles, frequency)
                        if tfidf> 0:
                            weights[file_name][token] = tfidf

            indexFile.write("{}: ".format(file_name))
            for item in weights[file_name]:
                indexFile.write("{},{} ".format(item, weights[file_name][item]))
            indexFile.write("\n")
            counter += 1
            
        return weights
    
    def similarity(document, query):

        internalProduct = 0
        euclidianNormA = 0
        euclidianNormB = 0

        documentWeight = 0
        for key in query:
            if key in document.keys():
                documentWeight = document[key]
            else:
                documentWeight = 0
            internalProduct += query[key] * documentWeight
            
        for key in document.keys():
            euclidianNormA += pow(document[key], 2)
        euclidianNormA = sqrt(euclidianNormA)
        
        for key in query.keys():
            euclidianNormB += pow(query[key], 2)
        euclidianNormB = sqrt(euclidianNormB)

        #print("Internal Product: " + str(internalProduct))
        #print("Euclidian Norm: " + str(euclidianNormA * euclidianNormB))
        if (euclidianNormA * euclidianNormB) == 0:
            return 0
        else:
            return internalProduct/(euclidianNormA * euclidianNormB)

    def startVectorModel():
        query = open(sys.argv[2], 'r', encoding='utf8').readline().lower()
        baseFile = open(sys.argv[1], 'r', encoding='utf8').readlines()
        numberOfFiles = len(baseFile)

        invertedIndex = InvertedIndex.startInvertedIndex(baseFile)
        weights = VectorModel.startWeighting(invertedIndex, numberOfFiles, baseFile)
        
        queryDictionary = InvertedIndex.creatingSubDictionary(InvertedIndex.removeSuffix(InvertedIndex.removeStopwords(InvertedIndex.getFilteredTokens(InvertedIndex.getTokens(query)))))
        if "&" in queryDictionary.keys():
            queryDictionary.pop("&")

        for token in queryDictionary.keys():
            if token in invertedIndex.keys():
                queryDictionary[token] = VectorModel.tf(queryDictionary[token]) * VectorModel.idf(numberOfFiles, len(invertedIndex[token]))
            else:
                queryDictionary[token] = 0.0
        #print(queryDictionary)
        counter = 0
        sim = {}
        minThreshold = 1/1000
        for document in weights.keys():
            result = VectorModel.similarity(weights[document], queryDictionary)
            if result > minThreshold:
                counter += 1
                sim[document] = result

        indexFile = open("resposta.txt", 'w')
        indexFile.write(str(counter) + "\n")
        for value in sorted(sim.values(), reverse=True):
            indexFile.write("{}: {}".format(list(sim.keys())[list(sim.values()).index(value)], value) + "\n")
            
    
    
# ----------------------------------->MAIN<------------------------------------
def main():
    # Inicio das variáveis    
    vm = VectorModel
    vm.startVectorModel()
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

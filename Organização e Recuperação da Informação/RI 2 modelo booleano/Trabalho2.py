# -------------------------------->BIBLIOTECAS<--------------------------------
import sys
import nltk
import pickle

from nltk.corpus import stopwords
from nltk.tag import UnigramTagger
# -----------------------------------------------------------------------------

# ------------------------------->CLASSES<-------------------------------------

# ---------------------------->Inverted Index<---------------------------------
class InvertedIndex:
    def startInvertedIndex():  # Inicia o indice invertido (o que estava antes no trabalho 1 na Main)
        uniTagger = "trained_tagger.bin"
        u_tagger = None
        try:
            u_tagger = pickle.load(open(uniTagger, "rb"))
        except:
            u_tagger = nltk.tag.UnigramTagger(nltk.corpus.mac_morpho.tagged_sents())
            pickle.dump(u_tagger, open(uniTagger, "wb"))
        cont = 1
        dic = {}
        new_dictionary = {}

        baseFile = open(sys.argv[1], "r", encoding="utf8")
        lines = baseFile.readlines()
        for line in lines:
            subfile = open(line.strip(), "r", encoding="utf8")
            sublines = subfile.read().lower()

            finalTokens = InvertedIndex.removeSuffix(
                InvertedIndex.removeStopwords(
                    InvertedIndex.getFilteredTokens(InvertedIndex.getTokens(sublines)),
                    u_tagger,
                )
            )
            dic[cont] = InvertedIndex.creatingSubDictionary(finalTokens)

            cont += 1
        return InvertedIndex.creatingInvertedIndex(dic)

    def getTokens(sublines):  # Pega os tokens
        return nltk.word_tokenize(sublines)

    def getFilteredTokens(tokens):  # Filtra os espaços e pontuações
        punctuation = [".", ",", "!", "?", " ", "\n"]
        newtokens = []  # Salva os tokens sem pontuação e sem espaços
        for word in tokens:
            if word not in punctuation:
                newtokens.append(word)
        return newtokens

    def removeStopwords(newtokens, u_tagger):  # Filtra as stopwords
        notAlowed = ["PREP", "ART", "KC", "KS"]
        novo_novoToken = []  # Salvar os tokens do novo_novoToken sem as stopwords
        for token in newtokens:
            if token not in stopwords.words("portuguese"):
                novo_novoToken.append(token)

        novo_novoToken2 = []  # Salva os tokens com o filtrados
        for token in u_tagger.tag(novo_novoToken):
            if token[1] not in notAlowed:
                novo_novoToken2.append(token[0])
        return novo_novoToken2

    def removeSuffix(novo_novoToken):
        stemmer = nltk.stem.RSLPStemmer()
        NovoDoNovo_novoToken = (
            []
        )  # NovoDoNovo_novo_novoToken -> Salvar os tokens do novo_novo_novoToken sem os sufixos
        for token in novo_novoToken:
            NovoDoNovo_novoToken.append(stemmer.stem(token))
        return NovoDoNovo_novoToken

    def creatingSubDictionary(
        NovoDoNovo_novoToken,
    ):  # Retorna um novo dicionário com todos os tratamentos filtrados
        dictionary = {}
        for token in NovoDoNovo_novoToken:
            if token not in dictionary:
                dictionary[token] = 1
            else:
                dictionary[token] += 1
        return dictionary

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

# ---------------------------------->Boolean Model<-----------------------------------
class BooleanModel:
    def startBooleanModel(newDictionary):  # Tratamentos "OU" e "E"
        queryFile = open(sys.argv[2], "r", encoding="utf8")
        query = queryFile.readline().lower()

        queryA = []

        for subquery in query.split("|"):
            queryA.append(subquery.split("&"))

        finalResult = []
        for subquery in queryA:
            finalResult.append(BooleanModel.filterOne(subquery, newDictionary))

        ultimateResult = finalResult[0]

        for item in finalResult:
            print(item)
            ultimateResult = ultimateResult.union(item)

        indexFile = open("resposta.txt", "w")
        indexFile.write(str(len(ultimateResult)) + "\n")
        for item in sorted(ultimateResult):
            indexFile.write(str(item) + "\n")

    def filterOne(subquery, newDictionary):
        queryB = []
        for token in subquery:
            queryB.append(token.replace(" ", "").replace("\n", ""))

        result = BooleanModel.filterTwo(queryB, newDictionary)
        if result == []:
            intermediateResult = set()
        else:
            intermediateResult = result[0]

        for item in result:
            intermediateResult = intermediateResult.intersection(item)

        return intermediateResult

    def filterTwo(subquery, newDictionary):  # Tratamento "NOT"
        stemmer = nltk.stem.RSLPStemmer()
        lines = open(sys.argv[1], "r", encoding="utf8").readlines()

        result = []
        hasNot = False
        for token in subquery:
            resultSet = set()
            if token[0] == "!":
                token = token.rsplit("!")[1]
                hasNot = True
            if (
                token not in stopwords.words("portuguese")
                and newDictionary.get(stemmer.stem(token), 0) != 0
            ):
                sub_dictionary = newDictionary[stemmer.stem(token)]
                for item in sub_dictionary:
                    file_number = int(item.rsplit(",")[0])
                    file_name = lines[file_number - 1]
                    resultSet.add(file_name.replace("\n", ""))
                if hasNot == False:
                    result.append(resultSet)
                else:
                    fullSet = set()
                    cont = 1
                    while cont <= len(lines):
                        file_name = lines[cont - 1]
                        fullSet.add(file_name.replace("\n", ""))
                        cont = cont + 1
                    result.append(fullSet.difference(resultSet))
                    hasNot = False
        return result
# -----------------------------------------------------------------------------

# ----------------------------------->MAIN<------------------------------------
def main():
    # Inicio das variáveis
    inv = InvertedIndex
    bm = BooleanModel
    bm.startBooleanModel(inv.startInvertedIndex())
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

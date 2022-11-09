# Fonctions utilisées dans le cadre du projet 2 :
#
# discover              Charge un fichier csv, affiche les informations générales le concernant,
#                       et retourne le dataframe le concernant
#
# missingDataRate       Affiche le taux de manquants (%) pour chaque colonne du dataframe
#
# missingData           Affiche les noms de colonnes et lignes dont le taux de manquants
#                       est inférieur aux seuils spécifiés
#
# detectDuplicatedData  Indique le nombre de doublons dans un dataframe et en renvoie les
#                       lignes dans un dataframe
#
# missingData4listCol   indique le % de données manquantes pour les indicateurs listés
#                       dans la colonne "Indicator Code" du dataframe en entrée,
#                       et pour une liste spécifiée de colonnes de valeurs
#
# extractIndicator      extrait un indicateur contenu dans un dataframe contenant la liste
#                       des indicateurs dans la colonne "Indicator Code" et pour une liste
#                       de valeurs (colonnes) spécifiée
#
# polyPredict           prédiction polynomiale de l'évolution de données
#
# pivotData             Création de matrice pivot

# Import des librairies
import numpy as np
import pandas as pd
import os

# Suppression du warning (faux positif)
pd.options.mode.chained_assignment = None

# Fonction de prise de connaissance d'un tableau de données
# Affiche des informations sauf omission explicitement demandée dans args
# L'argument kwargs sert à expliciter le caractère de séparation des données si différent de ','
def discover(url, *args, **kwargs):
# Arguments kwargs, lecture du fichier CSV
    if 'sep' in dict.keys(kwargs):
        data = pd.read_csv(url, sep=kwargs['sep'])
    else:
        data = pd.read_csv(url, sep=',')

    print('Découverte du fichier de données ', os.path.basename(url), '\n')
# Arguments args
    if 'no_shape' not in args:
        print('Taille du tableau de données: ', data.shape, '\n')
    if 'no_index' not in args:
        print('Index de la table de données: ', data.index, '\n')
    if 'no_head' not in args:
        print('Variables et premières lignes du tableau de données:\n\n', data.head(), '\n')
    if 'no_dtypes' not in args:
        print('Types de données du tableau :\n', data.dtypes, '\n')
    if 'no_var' not in args:
        print('Liste des variables :')
        for var in data.columns.tolist():
            print(' - ', var)
        print('\n')
    if 'no_desc' not in args:
        print('Description des variables numériques: ', data.describe(), '\n')
    return data

# Calcule le taux de manquant par colonne
# L'argument 'return' spécifie de renvoyer la matrice de manquants (booleen)
# La fonction affiche le résultat
def missingDataRate(data, *args):
    dataMissing = pd.DataFrame(100.0 * data.isna().sum(axis=0) / data.shape[0])
    dataMissing.rename(columns={'0': 'Manquants'}, inplace=True)
    with pd.option_context('display.float_format', '{:.0f}%'.format):
        print("% de données manquantes par variable :", '\n', dataMissing, '\n')
    if 'return' in args:
        return dataMissing

# Identifie les colonnes ou lignes au-dessus du seuil de données manquantes
# spécifié par l'argument kwargs vThr pour les colonnes et
# iThr pour les lignes - Valeurs de seuil par défaut = 20%
# La liste des variables est donnée par le nom de colonne
# La liste des lignes est donné par défaut par la donnée de la première colonne de la ligne
# ou selon la donnée de la colonne clé dont le nom est passé en kwarg 'kVar'
# Le résultat est affiché à l'écran
def missingData(data, **kwargs):
    #print(kwargs)
    if 'vThr' in dict.keys(kwargs):
        vSeuil = kwargs['vThr']
    else:
        vSeuil = 0.2
    if 'iThr' in dict.keys(kwargs):
        iSeuil = kwargs['iThr']
    else:
        iSeuil = 0.2
    if 'kVar' in dict.keys(kwargs):
        cleVar = kwargs['kVar']
    else:
        cleVar = data.columns[0] # Attribuer par défaut la première colonne de données
    #    print(cleVar)
        with pd.option_context('display.float_format', '{:0.0f}%'.format):
            print(f'Total données manquantes : ',
                  f'{(100 * float(data.isna().sum().sum()) / (data.shape[0] * data.shape[1])):.0f} \n')
    # print('Données manquantes par variable :\n', data.isna().sum(axis=0))
    # print('Données manquantes par individu :\n', data.isna().sum(axis=1))

    # Variables sous le seuil de données manquantes
    maskVar = (data.isna().sum(axis=0) < np.full(data.shape[1], vSeuil * data.shape[0]))
    varValides = maskVar * data.columns
    print(f'{maskVar.sum()} sur {data.shape[1]} variables avec moins de {(100*vSeuil):.0f}% de manquants : ')
    for var in varValides:
        if len(var) > 0: print('-', var)

    # Individus sous le seuil de données manquantes
    maskInd = (data.isna().sum(axis=1) < np.full(data.shape[0], iSeuil * data.shape[1]))
    indValides = maskInd * data[cleVar]
    print(f'\n{maskInd.sum()} sur {data.shape[0]} individus avec moins de {100*iSeuil:.0f}% de manquants : ')
    for ind in indValides:
        if len(ind) > 0: print('-', ind)

# Recherche de doublons (lignes)
def detectDuplicatedData(data, *args, **kwargs):
    #print(kwargs)
    if 'subset' in dict.keys(kwargs):
        doublons = data.duplicated(subset=kwargs['subset'], keep='first')
    else:
        doublons = data.duplicated(keep='first')
    print("\nNombre de doublons: ", doublons.sum(), "\n")
    if 'return' in args:
        return doublons

# Fonction indiquant le % de données manquantes pour les indicateurs
# listés dans la colonne "Indicator Code" du dataframe "data",
# et dont les valeurs sont dans les colonnes "listCol"
# Le résultat affiche en ligne la liste des indicateurs et en
# colonne le % de manquants pour chaque colonne de valeur (année)
# --> Permet d'examiner la qualité de chaque indicateur, année
#     par année
def missingData4listCol(data, listCol):
    df = data[["Country Code", "Indicator Code"]]
    dataMissing = pd.DataFrame([])
    for colName in listCol:
        if colName in data.columns.tolist():
            df[colName] = data[colName]
            df.sort_values(by=["Country Code", "Indicator Code"], inplace=True)
            dfReshaped = df.pivot(index="Country Code", columns="Indicator Code", values=colName)
            dataMissing[colName] = dfReshaped.isna().sum(axis=0)
            nbLignes = dfReshaped.shape[0]
        else:
            print("Nom de colonne erronée!!!")
    dataMissing = 100.0 * dataMissing / nbLignes
    with pd.option_context('display.float_format', '{:0.0f}%'.format):
        print('% de données manquantes par indicateur:', '\n', dataMissing, '\n')

# Fonction d'extraction de l'indicateur de nom "indicatorName"
# à partir du dataframe "data" contenant la liste de tous les
# indicateurs dans la colonne "Indicator Code" et pour une
# liste de valeurs en colonnes ("listYears")
# Le résultat est un dataframe indexé en ligne avec les valeurs
# de "Country Code" et les colonnes labellisées avec les valeurs
# de listYears ; les lignes non renseignées sont filtrées.
def extractIndicator(data, indicatorName, listYears):
    df = data[["Country Code", "Indicator Code"]]
    #print(df)
    for year in listYears:
        if year in data.columns.tolist():
            df[year] = data[year]
    if indicatorName in df["Indicator Code"].tolist():
        df = df[df["Indicator Code"] == indicatorName]
    df.sort_values(by=["Country Code", "Indicator Code"], inplace=True)
    dfReshaped = df.pivot(index="Country Code", columns="Indicator Code", values=listYears)
    dfReshaped.columns = dfReshaped.columns.get_level_values(0)
    return dfReshaped.dropna()

# Fonction de prédiction d'évolution des données pour la liste "xPredict"
# - Les valeurs "x" sont les labels des colonnes
# - Les valeurs "y" sont en ligne
# La prédiction basée sur un polynôme de degré "deg" obtenu par
# régression des données connues ("data")
# * Entrée: le dataframe "data" contenant les données connues,
#   et la liste des valeurs de x ("xPredict") pour lesquelles
#   la prédiction est recherchée
# * Arguments facultatifs:
#   - "deg" (=1 par défaut) le degré du polynôme de régression,
#   - "min" pour spécifier une valeur minimum pour les valeurs y
#   - "max" pour spécifier une valeur minimum pour les valeurs y
#   - "xtype='int'" à préciser si les valeurs de x sont entières,
#     afin d'en tenir compte pour la labellisation des colonnes
# * Sortie: dataframe contenant "data" et les colonnes prédites de "xPredict"
#   indexé pour les colonnes par valeurs croissantes (les données de "xPredict"
#   peuvent être inférieures et supérieures à celles de "data" pour x)
#   indexé pour les lignes avec l'index de "data" (clé pour les données)
def polyPredict(data, xPredict, **kwargs):
    xSerie = data.columns.tolist()
    xSerie = np.array([float(xSerie[i]) for i in range(0, len(xSerie))])
    xPredict = np.array([float(xPredict[i]) for i in range(0, len(xPredict))])
    dataResult = pd.DataFrame([])
    if 'deg' in dict.keys(kwargs):
        deg = kwargs['deg']
    else:
        deg = 1
    for ySerieName in data.index.values:
        ySerie = np.array(data.loc[ySerieName])
        # Regression avec np.polynomial.polynomial.Polynomial.fit ne retourne pas de valeurs cohérentes!!!
        #poly = np.polynomial.polynomial.Polynomial.fit(xSerie, ySerie, deg=deg).coef
        poly = np.polynomial.polynomial.polyfit(xSerie, ySerie, deg=deg)
        # np.polynomial.Polynomial._val donne le même résultat que np.polynomial.polynomial.polyval
        #print(np.polynomial.Polynomial._val(xPredict, poly))
        yPredict = np.polynomial.polynomial.polyval(xPredict, poly)
        if 'min' in dict.keys(kwargs):
            yPredict = np.maximum(yPredict, float(kwargs['min']))
        if 'max' in dict.keys(kwargs):
            yPredict = np.minimum(yPredict, float(kwargs['max']))
        xySerie = np.vstack([xSerie, ySerie])
        xyPredict = np.vstack([xPredict, yPredict])
        serie = pd.DataFrame(np.hstack([xySerie, xyPredict]))
        ligne = serie.iloc[0]
        if 'xtype' in dict.keys(kwargs):
            if kwargs['xtype'] == 'int':
                ligne = ligne.astype('int')
        serie.columns = ligne
        serie.set_index(pd.Index(['col', ySerieName]), inplace=True)
        serie.sort_values(by=ySerieName, axis=1, inplace=True)
        serie.drop('col', inplace=True)
        #dataResult = dataResult.append(serie)
        dataResult = pd.concat([dataResult, serie])
    return(dataResult)



# Trie la matrice selon les 2 colonnes clés "clePrim" et "cleSec" et
# pivote autour de "cleSec" en affectant les valeurs de la colonne "values"
def pivotData(data, clePrim, cleSec, valeurs):
    dataSorted = data.sort_values(by=[clePrim, cleSec])
    return dataSorted.pivot(index=clePrim, columns=cleSec, values=valeurs)


#dossier = ".\P2_05_data"
#fichier = "EdStatsData_preselected.csv"
#data = discover(dossier + "\\" + fichier, 'no_index', 'no_head', 'no_dtypes', 'no_var', 'no_desc')
#print(data.head())
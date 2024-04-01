import bibliothèque as bib
import time
import threading

#Initialisation des variables
X=None
Y=None
Z=None
xlist=[]
ylist=[]
message=""

#On créé les verrous pour empêcher plusieurs variables de modifier en même temps une valeur
lockX=threading.Lock()
lockY=threading.Lock()
lockZ=threading.Lock()
lockxlist=threading.Lock()
lockylist=threading.Lock()
lockmessage=threading.Lock()

def add_message(var):
    global message
    message+=var

def x_plus_1(): 
    global X
    X=X+1

def y_plus_1():
    global Y
    Y+=1

def setX():
    global X
    time.sleep(1)
    X = 5
    # Pour savoir si la fonction detTestRnd() peut détecter si un système n'est pas déterministe
    # X = random.randint(1, 10)

def setY():
    global Y
    # time.sleep(10)
    Y = 3
    # Y = random.randint(1, 10)

def computeZ():
    global Z
    Z = X + Y

def addX(val):
    global xlist
    xlist.append(val)

def addY(val):
    global ylist
    ylist.append(val)

def computeZlist ():
    global xlist, ylist, Z
    Z = sum(xlist) + sum(ylist)

def add_lots_values():
    global message
    for i in "Lorem ipsum dolor sit amet, consectetur adipiscing elit":
        
        message+=i
        time.sleep(0.01)


def test_parra(N): #On va essayer de faire un grand écart de temps

    tasksX = [bib.Task(f"TX{i+1}", [], ["X"], x_plus_1) for i in range(N)]
    tasksY = [bib.Task(f"TY{i+1}", [], ["Y"], y_plus_1) for i in range(N)]
    tX_0 = bib.Task("TX0", [], ["X"], setX)
    tY_0 = bib.Task("TY0", [], ["Y"], setY)
    tSomme = bib.Task("somme", ["X", "Y"], ["Z"], computeZ)

    #Création du dictionnaire nommé précédence
    precedence = {"TX0": [], "TY0": [], "somme":[f"TX{N}", f"TY{N}"]}
    #ajout des dépendances des tâches X
    precedence.update({f"TX{i+1}":[f"TX{i}"] for i in range(N)})
    precedence.update({f"TY{i+1}":[f"TY{i}"] for i in range(N)})

    s1 = bib.TaskSystem([tX_0, tY_0, tSomme]+tasksX+tasksY, precedence)

    s1.runSeq()
    print(X,Y,Z)    
    assert X == 5+N
    assert Y == N+3
    assert Z == 2*N+8

    s1.run()
    print(X,Y,Z)
    assert X == 5+N
    assert Y == N+3
    assert Z == 2*N+8


    # s1.draw()

    # Test de déterminisme avec des exécutions randomisées
    # s1.detTestRnd()

    # Comparaison des temps d'exécution séquentielle et parallèle
    s1.parCost()

#graphe correcte pour précédences complexes     
def test_maxpar_complex():
    global X, Y, xlist, ylist
    t1 = bib.Task("T1", [], ["X"], setX)
    t2 = bib.Task("T2", [], ["Y"], setY)
    ajout_x_to_xlist=bib.Task("ajout_x_to_xlist", ["X"], ["xlist"], lambda : addX(X))
    ajout_y_to_xlist=bib.Task("ajout_y_to_xlist", ["Y"], ["xlist"], lambda : addX(Y))
    ajout_x_to_ylist=bib.Task("ajout_x_to_ylist", ["X"], ["ylist"], lambda : addY(X))
    ajout_y_to_ylist=bib.Task("ajout_y_to_ylist", ["Y"], ["ylist"], lambda : addY(Y))
    somme_x_et_y=bib.Task("somme_x_et_y", ["xlist","ylist"], ["Z"], computeZlist)
    
    s1 = bib.TaskSystem([t1, t2, ajout_x_to_xlist, ajout_x_to_ylist, ajout_y_to_xlist, ajout_y_to_ylist, somme_x_et_y], {"T1": [], "T2": [], "ajout_x_to_xlist" : ["T1"], "ajout_y_to_xlist" : ["T2"],"ajout_x_to_ylist": ["T1"], "ajout_y_to_ylist" : ["T2"], "somme_x_et_y" :["ajout_x_to_xlist", "ajout_y_to_xlist","ajout_x_to_ylist", "ajout_y_to_ylist"]})
    
    s1.runSeq()
    print(X,Y,Z,xlist,ylist)    
    assert X == 5
    assert Y == 3
    assert Z == 16
    xlist.sort(),ylist.sort()
    assert xlist == [3,5]
    assert ylist == [3,5]

    s1.run()
    print(X,Y,Z,xlist,ylist)
    assert X == 5
    assert Y == 3
    assert Z == 32
    xlist.sort(),ylist.sort()
    assert xlist == [3,3,5,5]
    assert ylist == [3,3,5,5]

    s1.draw()

    # # Test de déterminisme avec des exécutions randomisées
    s1.detTestRnd()

    # Comparaison des temps d'exécution séquentielle et parallèle
    s1.parCost()

#Preuve parrallèle>séquentiel
def test_rapidité():
    t1 = bib.Task("T1",[], [], lambda : time.sleep(1))
    t2 = bib.Task("T2",[],[], lambda : time.sleep(30))
    s1 = bib.TaskSystem([t1, t2], {"T1": [], "T2": []})
    s1.parCost()

#On a essayé de faire en sorte que 2 tâches modifient en même temps une valeur
def test_lock():
    t1 = bib.Task("T1",[],[lockmessage], add_lots_values)
    t2 = bib.Task("T2", [], [lockmessage], lambda : add_message("Coucou") )
    s1 = bib.TaskSystem([t1, t2], {"T1":[], "T2":[]})
    s1.run()
    print(message)

    
def test_maxpar_simple():
    # Création des tâches avec leurs dépendances et leurs fonctions de mise à jour
    t1 = bib.Task("T1", [], [lockX], setX)
    t2 = bib.Task("T2", [], [lockY], setY)
    tSomme = bib.Task("somme", ["T1","T2"], [lockZ], computeZ)

    # Création du système de tâches avec la liste des tâches et leurs relations de précédence
    s1 = bib.TaskSystem([t1, t2, tSomme], {"T1": [], "T2": [], "somme": ["T1", "T2"]})
    
    # Exécution parallèle des tâches
    s1.run()
    assert X == 5
    assert Y == 3
    assert Z == 8
    print(X, Y, Z)

    # Exécution séquentielle des tâches
    s1.runSeq()
    # assert test si val =/= val attendue
    assert X == 5
    assert Y == 3
    assert Z == 8
    print(X,Y,Z)

    # Affichage du graphe de précédence
    s1.draw()

    # Test de déterminisme avec des exécutions randomisées
    s1.detTestRnd()

    # Comparaison des temps d'exécution séquentielle et parallèle
    s1.parCost()

# Appel de la fonction de test lors de l'exécution du fichier
if __name__ == "__main__":
    # test_maxpar_simple()
    # test_maxpar_complex()
    # test_parra(1000)
    test_rapidité()
    # test_lock()
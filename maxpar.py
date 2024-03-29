import bibliothèque

def test_maxpar():
    # Création des tâches avec leurs dépendances et leurs fonctions de mise à jour
    t1 = bibliothèque.Task("T1", [], ["X"], lambda: bibliothèque.runT1(s1))
    t2 = bibliothèque.Task("T2", [], ["Y"], lambda: bibliothèque.runT2(s1))
    tSomme = bibliothèque.Task("somme", ["X", "Y"], ["Z"], lambda: bibliothèque.runTsomme(s1))

    # Création du système de tâches avec la liste des tâches et leurs relations de précédence
    s1 = bibliothèque.TaskSystem([t1, t2, tSomme], {"T1": [], "T2": [], "somme": ["T1", "T2"]})
    
    # Exécution séquentielle des tâches
    s1.runSeq()
    print(s1.X, s1.Y, s1.Z)

    # Exécution parallèle des tâches
    s1.run()
    print(s1.X, s1.Y, s1.Z)

    # Affichage du graphe de précédence
    s1.draw()

    # Test de déterminisme avec des exécutions randomisées
    s1.detTestRnd()

    # Comparaison des temps d'exécution séquentielle et parallèle
    s1.parCost()

# Appel de la fonction de test lors de l'exécution du fichier
if __name__ == "__main__":
    test_maxpar()

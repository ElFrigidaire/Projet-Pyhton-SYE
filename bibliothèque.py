import threading
import random
import time
import networkx as nx
import matplotlib.pyplot as plt


# La classe Task représente une tâche avec un nom, les ressources qu'elle lit et écrit, et une fonction pour exécuter la tâche
class Task:
    def __init__(self, name="", reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run

class TaskSystem:
    def __init__(self, tasks, precedence):
        self.tasks = tasks
        self.precedence = precedence

        self.validate_inputs()
        self.graph = self.build_graph()

    # Cette fonction valide les entrées fournies lors de la création d'un objet TaskSystem
    def validate_inputs(self):
        # Vérification des noms de tâches uniques
        task_names = [task.name for task in self.tasks]
        if len(task_names) != len(set(task_names)):
            raise ValueError("Les noms des tâches doivent être uniques")

        # Vérification de la cohérence des noms de tâches dans le graphe de précédence
        for task_name in self.precedence.keys():
            if task_name not in task_names:
                raise ValueError(
                    f"Le nom de tâche {task_name} dans le dictionnaire de précédence n'est pas dans la liste des tâches")

        # Vérification de la validité des dépendances de chaque tâche
        for dependencies in self.precedence.values():
            for dep in dependencies:
                if dep not in task_names:
                    raise ValueError(
                        f"La dépendance {dep} n'est pas une tâche valide")

    # Cette fonction retourne les dépendances d'une tâche spécifique
    def getDependencies(self, task_name):
        return self.precedence.get(task_name, [])

    # Cette fonction exécute les tâches de manière séquentielle en respectant l'ordre topologique
    def runSeq(self):
        ordered_tasks = list(nx.topological_sort(self.graph))
        for task_name in ordered_tasks:
            task = next(t for t in self.tasks if t.name == task_name)
            task.run()

    # Cette fonction exécute les tâches en parallèle en utilisant des threads
    def run(self):
        # Obtient une liste ordonnée des tâches en suivant l'ordre topologique du graphe de précédence
        ordered_tasks = list(nx.topological_sort(self.graph))
        threads = {}
        # Pour chaque tâche, créer un thread pour l'exécuter et l'ajouter à la liste de threads
        for task_name in ordered_tasks:
            print(task_name)
            task = next(t for t in self.tasks if t.name == task_name)
            dependencies = self.getDependencies(task_name)
            def newtarget():
                for i in dependencies:
                    threads[i].join()

                # for lock in task.writes:
                #     lock.acquire()
                
                with task.writes[0]:
                    task.run()
                
                # for lock in task.writes:
                #     # if lock.locked():
                #     print("Je suis locked")
                #     lock.release()
                
            thread = threading.Thread(target=newtarget)
            thread.start()
            threads[task_name] = thread

        # Attendre la fin de l'exécution de tous les threads
        for thread in threads.values():
            thread.join()

    # Cette fonction construit le graphe de précédence à partir des informations fournies
    def build_graph(self):
        # Crée un graphe orienté vide
        G = nx.DiGraph()
        # Ajoute chaque tâche comme un nœud dans le graphe
        for task in self.tasks:
            G.add_node(task.name)
            # Pour chaque dépendance de la tâche, ajoute un arc dans le graphe
            for dep in self.precedence[task.name]:
                G.add_edge(dep, task.name)
        return G

    def detTestRnd(self, num_tests=100):

        for _ in range(num_tests):
            # Générer des valeurs aléatoires pour les variables X, Y et Z
            self.X = random.randint(1, 100)
            self.Y = random.randint(1, 100)
            self.Z = self.X + self.Y

            # Exécuter les tâches en parallèle avec le premier jeu de valeurs
            self.run()
            result1 = (self.X, self.Y, self.Z)

            # Réinitialiser les variables avec les mêmes valeurs aléatoires
            self.X = random.randint(1, 100)
            self.Y = random.randint(1, 100)
            self.Z = self.X + self.Y

            # Exécuter les tâches en parallèle avec le second jeu de valeurs
            self.run()
            result2 = (self.X, self.Y, self.Z)

            # Comparer les résultats des deux exécutions parallèles
            if result1 != result2:
                print("Le système n'est pas déterministe")
                # quit()
                return
        print(f"Aucune indétermination détectée après {num_tests} tests")

    
    def parCost(self):
        num_runs = 10
        seq_times = []  
        par_times = []  

        for _ in range(num_runs):
            # Mesurer le temps d'exécution en séquentiel
            start_time = time.perf_counter()
            self.runSeq()
            end_time = time.perf_counter()
            seq_times.append(end_time - start_time)

            # Mesurer le temps d'exécution en parallèle
            start_time = time.perf_counter()
            self.run()
            end_time = time.perf_counter()
            par_times.append(end_time - start_time)

        # Calculer le temps d'exécution moyen pour chaque méthode
        avg_seq_time = sum(seq_times) / num_runs
        avg_par_time = sum(par_times) / num_runs

        # Afficher les temps d'exécution moyens pour chaque méthode
        print("Temps d'exécution moyen en séquentiel :",avg_seq_time,"s")
        print("Temps d'exécution moyen en parallèle :",avg_par_time,"s")
    
    # Cette fonction affiche le graphe de précédence en utilisant networkx et matplotlib
    def draw(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=2000,
                node_color="lightblue", font_size=10, font_weight="bold")
        plt.show()


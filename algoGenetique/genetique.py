# Algorithme génétique
# Ledieu Clement
import random
import sys
import time


class Objet:
    objGlobal = 0

    def __init__(self, poids, couleur):
        self.id = Objet.objGlobal
        Objet.objGlobal += 1
        self.poids = poids
        self.couleur = couleur

    def __str__(self):
        return "Obj. {} <Pds: {} | Clr: {}>".format(self.id, self.poids, self.couleur)


# Prend deux solutions et les fusionnent, pour la renvoyer après
def fusionDance(sols, mutation):
    nouvSolution = Solution()
    for i in range(len(nouvSolution.xij)):
        if random.random() < mutation:
            nouvSolution.xij[i] = random.randint(0, len(Solution.objets) - 1)
        else:
            nouvSolution.xij[i] = random.choice([sols[0].xij[i], sols[1].xij[i]])
    nouvSolution.calculsInternes()
    return nouvSolution


class Solution:
    objets = None
    capacites = None
    generation = 0
    numsol = 0
    mutation = 0

    def __init__(self):
        self.generation = Solution.generation
        # Toutes les solutions partagent la même liste d'objets et capacités.
        # self.xij est la liste des objets, allant de 0 a n, et leurs boites attribuées
        # self.ykj est la liste des boites et leurs capacités, allant de 0 a m
        # 0 signifie qu'aucune capacité n'est assignée a la boite (Boite inexistante).
        # Il ne peut pas y avoir plus de boites que d'item dans une solution donc on génère une liste de boites
        # de taille égale au nombre d'objet.
        self.xij = [None for _ in range(len(Solution.objets))]
        self.ykj = [max(Solution.capacites) for _ in range(len(Solution.objets))]
        # Fitness: Indicateur de la qualité de la solution.
        # Plus la fitness est élevée, mieux est la solution
        self.fitness = 0
        # espaceUtilise contient l'espace utilisé d'une boite. Mis a jour après avoir fait tous les calculs
        self.espaceUtilise = [0 for _ in range(len(Solution.objets))]
        # couleursBoites contient les couleurs qu'on peut trouver par boite
        self.couleursBoites = [[] for _ in range(len(Solution.objets))]
        # objDansBoites contient un dict avec pour clé la boite et la valeur la liste des objets
        self.objDansBoites = {}

    def randomSolution(self):
        # Genère une solution aléatoire, pas forcément valide.
        for x in range(len(self.xij)):
            self.xij[x] = random.choice(range(len(Solution.objets)))
        self.calculsInternes()

    def calculsInternes(self):
        # Espace utilisé
        self.espaceUtilise = [0 for _ in range(len(Solution.objets))]
        self.couleursBoites = [[] for _ in range(len(Solution.objets))]
        for i in range(len(self.xij)):
            self.espaceUtilise[self.xij[i]] += Solution.objets[i].poids
            # Couleurs par boites
            if Solution.objets[i].couleur not in self.couleursBoites[self.xij[i]]:
                self.couleursBoites[self.xij[i]].append(Solution.objets[i].couleur)
        # Optimisation des boites
        self.optimisationBoites()
        # Objets dans Boite
        self.objDansBoites = {i: [] for i in range(len(self.xij))}
        for i in range(len(self.xij)):
            self.objDansBoites[self.xij[i]].append(i)
        self.calculerFitness()

    # https://www.youtube.com/watch?v=_of6UVV4HGo&list=PLRqwX-V7Uu6bJM3VgzjNV5YxVxUwzALHV&index=5
    def calculerFitness(self):
        # La fitness devrait être entre 0 et 1
        # 1er essai: espaceUtilise / espaceParfait, *0.1 si solution inutilisable
        self.fitness = 0
        # for x in range(len(self.xij)):
        #     self.fitness += abs(self.ykj[x] - self.espaceUtilise[x])
        #     self.fitness += abs(self.ykj[x] - self.espaceUtilise[x])
        # self.fitness = self.fitness / sum(self.ykj)
        self.fitness = sum(self.espaceUtilise) / sum(self.ykj)
        # Solution 1
        # if not self.solutionValable():
        #     self.fitness *= 0.1
        for x in range(len(self.ykj)):
            if self.espaceUtilise[x] > self.ykj[x]:
                self.fitness *= 0.8
        for y in self.couleursBoites:
            if len(y) > 2:
                self.fitness *= 0.8

    def optimisationBoites(self):
        # Réduit la taille des boites au mieux.
        self.ykj = [max(Solution.capacites) for _ in range(len(Solution.objets))]
        for i in range(len(self.ykj)):
            if self.espaceUtilise[i] == 0:
                self.ykj[i] = 0
            else:
                try:
                    self.ykj[i] = min(sol for sol in Solution.capacites if sol >= self.espaceUtilise[i])
                except ValueError:
                    self.ykj[i] = max(Solution.capacites)

    def solutionValable(self):
        # Test si une boite est en surcharge
        for x in range(len(self.ykj)):
            if self.espaceUtilise[x] > self.ykj[x]:
                return False
        # Test si il y a 3+ couleurs différentes dans une boite
        for y in self.couleursBoites:
            if len(y) > 2:
                return False
        return True

    def __str__(self):
        rep = "Solution {}-{} | Fitness: {} | {} / {} | Valable: {}\n".format(self.generation, self.numsol,
                                                                              self.fitness,
                                                                              sum(self.espaceUtilise), sum(self.ykj),
                                                                              self.solutionValable())
        for x in self.objDansBoites:
            if not self.objDansBoites[x]:
                continue
            rep += "Boite {} ~ {} / {}\n".format(x, self.espaceUtilise[x], self.ykj[x])
            for y in self.objDansBoites[x]:
                rep += " | {}\n".format(Solution.objets[y])
        rep += "{}".format(self.couleursBoites)
        return rep


class Bench:
    def __init__(self, file, population, mutation):
        with open(file, "r") as f:
            self.boites = [int(x) for x in f.readline().split()[1:]]
            self.nb_couleurs = int(f.readline())
            self.nb_objets = int(f.readline())
            self.liste_objets = []
            for i in range(self.nb_objets):
                l = f.readline().split()
                self.liste_objets.append(Objet(int(l[0]), int(l[1])))
                i += 1
        Solution.objets = self.liste_objets[:]
        Solution.capacites = self.boites[:]
        Solution.mutation = mutation
        Solution.generation = 0
        Solution.numsol = 0
        self.population = population
        self.generation = []
        self.fitnesses = []
        self.fitnessesp1 = [0 for _ in range(self.population)]
        self.generationp1 = [None for _ in range(self.population)]
        self.meilleureSolution = None
        self.meilleureFitness = 0

    def start(self, timer=60, noprint=False):
        self.generation = [Solution() for _ in range(self.population)]
        for x in range(self.population):
            # self.generation.append(Solution())
            self.generation[x].randomSolution()
            self.fitnesses.append(self.generation[x].fitness)
        debut = time.time()
        print("> Début du calcul génétique")
        while (time.time() - debut < timer) and (1 not in self.fitnesses):
            print("> Génération {}...\n".format(Solution.generation))
            for x in range(self.population):
                self.generationp1[x] = fusionDance(random.choices(self.generation, self.fitnesses, k=2),
                                                   Solution.mutation)
                self.fitnessesp1[x] = self.generationp1[x].fitness
            if not noprint:
                print("> Meilleure solution de la génération {}: \n".format(Solution.generation))
                print(self.generationp1[self.fitnessesp1.index(max(self.fitnessesp1))])
                print("\n\n")
            if self.meilleureFitness < max(self.fitnessesp1):
                self.meilleureSolution = self.generationp1[self.fitnessesp1.index(max(self.fitnessesp1))]
                self.meilleureFitness = max(self.fitnessesp1)
            self.generation = self.generationp1[:]
            self.fitnesses = self.fitnessesp1[:]
            Solution.generation += 1
        print("> Fin de la simulation. Temps écoulé: {}s\a\n".format(time.time() - debut))
        print("> Meilleure solution:\n")
        print(self.meilleureSolution)
        # print("> Meilleure solution de la dernière génération:\n")
        # print(self.generation[self.fitnesses.index(max(self.fitnesses))])


if len(sys.argv) >= 2:
    fichier = sys.argv[1]
else:
    fichier = "bench_20_4"

# LANCEMENT DU CODE YAAAS QUEEN
if __name__ == '__main__':
    TIMER = 60  # secondes
    POPULATION = 200  #
    MUTATION = 0.04
    BENCH = Bench('../benches/{}.txt'.format(fichier), POPULATION, MUTATION)
    BENCH.start(timer=TIMER, noprint=True)

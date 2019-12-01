import os
import time
import sys


class Bench:
    """ Objet contenant un bench.
    La liste des objets est contenue dans une liste.
    Un objet est représenté par un Objet avec poids et couleur.
    La liste des boites disponibles est une liste.
    """

    def __init__(self, file):
        self.filename = file
        with open(file, "r") as f:
            self.boites = [int(x) for x in f.readline().split()[1:]]
            self.nb_couleurs = int(f.readline())
            self.nb_objets = int(f.readline())
            self.liste_objets = []
            i = 0
            for i in range(self.nb_objets):
                l = f.readline().split()
                self.liste_objets.append(Objet(i, l[0], l[1]))
                i += 1

    def __str__(self):
        rendu = "BENCH {}\n".format(self.filename)
        rendu += "Boites dispos: "
        for x in self.boites:
            rendu += "{} ".format(x)
        rendu += "\nCouleurs différentes: {}\nObjets ({}): \n".format(self.nb_couleurs, len(self.liste_objets))
        rendu += "Pds | Clr\n"
        for y in self.liste_objets:
            rendu += "{:<4}| {}\n".format(y.poids, y.couleur)
        return rendu


class Objet:
    def __init__(self, id, poids, couleur):
        self.id = id
        self.poids = int(poids)
        self.couleur = int(couleur)


class Boite:
    def __init__(self, id, taillemax):
        self.id = id
        self.taillemax = taillemax
        self.objets = []

    def poids_total(self):
        m = 0
        for x in self.objets:
            m += x.poids
        return m

    def poids_restant(self):
        m = self.taillemax
        for x in self.objets:
            m -= x.poids
        return m

    def couleurs(self):
        c = []
        for x in self.objets:
            if x.couleur not in c:
                c.append(x.couleur)
        return c

    def couleur_ok(self, objet):
        if len(self.couleurs()) < 2:
            return True
        elif objet.couleur in self.couleurs():
            return True
        else:
            return False

    def vide_apres_ajout(self, objet):
        # Renvoie combien il restera de place si on met l'objet
        # -1 Si impossible
        if objet.poids <= self.poids_restant() and self.couleur_ok(objet):
            return self.poids_restant() - objet.poids
        else:
            return -1

    def add_objet(self, objet):
        # True si ajouté, False sinon
        if objet.poids <= self.poids_restant() and self.couleur_ok(objet):
            self.objets.append(objet)
            return True
        else:
            return False


# <editor-fold desc="First fit & Best fit">
# Heuristique: First fit / Best fit
# C'est pas vraiment ce qui est demandé mais eh, we take those.
def first_fit(bench):
    # Algo. First Fit.
    # On utilise les boites les plus grandes au début.
    time_start = time.time()
    boites_u = []
    for o in bench.liste_objets:
        obj_ok = False
        i_b = 0
        while not obj_ok:
            while i_b < len(boites_u) and obj_ok == False:
                obj_ok = boites_u[i_b].add_objet(o)
                i_b += 1
            if not obj_ok:
                boites_u.append(Boite(len(boites_u), max(bench.boites)))
    optimisation_boites(boites_u, bench)
    time_stop = time.time()
    print_solution(boites_u, time_stop - time_start)


def best_fit(bench):
    # Algo. Best Fit.
    # On utilise la boite qui laisse le moins de place après avoir mis un item dedans.
    time_start = time.time()
    boites_u = []
    for o in bench.liste_objets:
        obj_ok = False
        i_b = 0
        best_boite = [None, 999999]
        while i_b < len(boites_u) and obj_ok == False:
            if 0 <= boites_u[i_b].vide_apres_ajout(o) < best_boite[1]:
                best_boite = [i_b, boites_u[i_b].vide_apres_ajout(o)]
            i_b += 1
        if best_boite[0] == None:
            boites_u.append(Boite(len(boites_u), max(bench.boites)))
            boites_u[-1].add_objet(o)
        else:
            boites_u[best_boite[0]].add_objet(o)

    optimisation_boites(boites_u, bench)
    time_stop = time.time()
    print_solution(boites_u, time_stop - time_start)
# </editor-fold>


def optimisation_boites(boites_u, bench):
    for b in boites_u:
        mScore = 99999
        mBoite = 99999
        for c in bench.boites:
            if (c - b.poids_total()) < mScore and c - b.poids_total() >= 0:
                mScore = c - b.poids_total()
                mBoite = c
        b.taillemax = mBoite


def print_solution(boites_u, timer=None):
    print("Boite | Objet | Poids | Couleur | B: U/T")
    stats_total = [0, 0]
    if timer != None:
        print("Solution trouvée en {}s".format(timer))
    for b in boites_u:
        f = True
        for i in b.objets:
            if f:
                print("{:^6}|{:^7}|{:^7}|{:^9}|{:>3}/{:<3}".format(b.id, i.id, i.poids, i.couleur, b.poids_total(),
                                                                   b.taillemax))
                stats_total[0] += b.poids_total()
                stats_total[1] += b.taillemax
                f = False
            else:
                print("{:^6}|{:^7}|{:^7}|{:^9}".format(b.id, i.id, i.poids, i.couleur))
        print("-" * 32)
    print("Total: {} / {} (Vide: {})".format(stats_total[0], stats_total[1], stats_total[1] - stats_total[0]))


# Ecrire ici le nom de fichier bench a utiliser, sans dossier ni extension, ou utiliser les arguments de commande.
# Les arguments prennent priorité sur le texte hardcodé.
# Les fichiers bench devraient se situer dans un dossier "benches", au même niveau que ce .py.
if len(sys.argv) >= 2:
    fichier = sys.argv[1]
else:
    fichier = "test0"
test = Bench("./benches/{}.txt".format(fichier))

print(test)
print("---------------------------------------------")
first_fit(test)
print("---------------------------------------------")
best_fit(test)


class GeneticAlgorithm:
    pass

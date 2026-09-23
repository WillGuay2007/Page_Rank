from __future__ import annotations

import logging
import random
import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

DAMPING: float = 0.85
SAMPLES: int = 10000

log = logging.getLogger(__name__)


def run(data: Path) -> None:
    """
    Exécute l'algorithme PageRank par échantillonnage et par itération.

    Affiche les résultats du calcul des PageRanks dans la sortie standard.

    Args:
        data:
            Le chemin vers le répertoire contenant le corpus de pages HTML.

    """
    log.debug("Chemin vers les données %s", data)
    corpus = crawl(data)

    ranks_sampled = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")

    for page in sorted(ranks_sampled):
        print(f"  {page}: {ranks_sampled[page]:.4f}")

    ranks_iterated = iterate_pagerank(corpus, DAMPING)
    print("PageRank Results from Iteration")

    for page in sorted(ranks_iterated):
        print(f"  {page}: {ranks_iterated[page]:.4f}")

#J'ai modifié crawl vu qu'il retournait pas des strings comme key mais plutot des Path
def crawl(directory: Path) -> dict[str, set[str]]:
    """
    Analyse un répertoire de pages HTML à la recherche de liens.

    Extrait tous les liens (`href`) des balises `<a>` dans les fichiers HTML
    du répertoire fourni.

    Args:
        directory:
            Le chemin vers le répertoire contenant les fichiers HTML.

    Returns:
        Un dictionnaire où chaque clé est le nom d'une page, et la valeur
        est un ensemble de toutes les autres pages du corpus vers lesquelles
        la page pointe.

    """
    pages: dict[str, set[str]] = {}

    # Extrait tous les liens des fichiers HTML
    for filename in directory.iterdir():
        if not filename.name.endswith(".html"):
            continue

        with filename.open(encoding="utf-8") as f:
            contents = f.read()
            links = re.findall(r'<a\s+(?:[^>]*?)href="([^"]*)"', contents)
            pages[filename.name] = set(links) - {filename.name}

    # Inclut uniquement les liens vers d'autres pages du corpus
    for filename in pages:
        pages[filename] = {
            link
            for link in pages[filename]  # Ok
            if link in pages
        }

    return pages


def transition_model(
    corpus: dict[str, set[str]], page: str, damping_factor: float
) -> dict[str, float]:
    """
       Retourne une distribution de probabilité sur la prochaine page à visiter.

       Avec une probabilité `damping_factor`, choisit au hasard un lien
       pointé par la `page`. Avec une probabilité `1 - damping_factor`, choisit
       au hasard un lien parmi toutes les pages du corpus.

       Args:
           corpus:
               Le dictionnaire représentant le graphe des pages du corpus.
           page:
               Le nom de la page actuelle sur laquelle se trouve le surfeur.
           damping_factor:
               Le facteur d'amortissement (probabilité de suivre un lien existant).

       Returns:
           Un dictionnaire associant chaque page du corpus à la probabilité
           (entre 0 et 1) qu'elle soit la prochaine page visitée.
           La somme des probabilités est de 1.

       """
    #J'aime quand c'est explicit comme ca.
    numberOfPages = len(corpus)
    numberOfLinks = len(corpus[page])
    oddsIfNoLinks = 1 / numberOfPages
    teleportChance = (1 - damping_factor) / numberOfPages
    oddsPerLink = damping_factor / numberOfLinks + teleportChance
    oddsDictionary = {}

    if numberOfLinks == 0:
        for iterPageName in corpus:
            oddsDictionary[iterPageName] = oddsIfNoLinks
        return oddsDictionary

    for iterPageName in corpus:
        if iterPageName in corpus[page]:
            oddsDictionary[iterPageName] = oddsPerLink
        else:
            oddsDictionary[iterPageName] = teleportChance
    return oddsDictionary


def sample_pagerank(
    corpus: dict[str, set[str]], damping_factor: float, n: int
) -> dict[str, float]:
    """
    Calcule les valeurs de PageRank par échantillonnage.

    Échantillonne `n` pages selon le modèle de transition, en commençant
    par une page au hasard, pour estimer l'importance de chaque page.

    Args:
        corpus:
            Le dictionnaire représentant le graphe des pages du corpus.
        damping_factor:
            Le facteur d'amortissement utilisé par le modèle de transition.
        n:
            Le nombre total d'échantillons à générer.

    Returns:
        Un dictionnaire où les clés sont les noms des pages, et les valeurs
        sont leur estimation de PageRank (entre 0 et 1). La somme de toutes
        les valeurs de PageRank est de 1.

    """
    visitAmountPerPageDict = {}
    for iterPageName in corpus:
        visitAmountPerPageDict[iterPageName] = 0

    initialPage: str = random.choice(list(corpus.keys()))
    visitAmountPerPageDict[initialPage] += 1
    lastVisitedPage: str = initialPage
    totalEntries = n
    n -= 1
    while n > 0:
        n -= 1
        pageChoicesOdds = transition_model(corpus, lastVisitedPage, damping_factor)
        lastVisitedPage = random.choices(
            list(pageChoicesOdds.keys()),
            weights=list(pageChoicesOdds.values()),
        )[0]
        visitAmountPerPageDict[lastVisitedPage] += 1
    pageRankDict = {}
    for iterPageName in visitAmountPerPageDict:
        pageRankDict[iterPageName] = visitAmountPerPageDict[iterPageName] / totalEntries
    return pageRankDict



def iterate_pagerank(
    corpus: dict[str, set[str]], damping_factor: float
) -> dict[str, float]:
    """
    Calcule les valeurs de PageRank par itération jusqu'à convergence.

    Met à jour itérativement les valeurs de PageRank selon la formule
    mathématique jusqu'à ce qu'aucune valeur ne change de plus de 0.001
    entre deux itérations.

    Args:
        corpus:
            Le dictionnaire représentant le graphe des pages du corpus.
        damping_factor:
            Le facteur d'amortissement utilisé dans la formule itérative.

    Returns:
        Un dictionnaire où les clés sont les noms des pages, et les valeurs
        sont leur PageRank final calculé (entre 0 et 1).
        La somme de toutes les valeurs de PageRank est de 1.

    """
    raise NotImplementedError
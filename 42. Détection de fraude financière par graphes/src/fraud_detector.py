"""
Moteur de détection de fraude financière par graphes.

Ce module contient la classe principale FraudDetector qui orchestre
la détection de trois types de structures suspectes:
1. Cycles de blanchiment (boucles de transferts)
2. Smurfing/Schtroumpfage (fractionnements de montants)
3. Anomalies de réseaux (comportements atypiques)

Auteurs: Malak El Idrissi et Joe Boueri
Groupe: 42
Projet: Détection de fraude financière par graphes
"""

import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import numpy as np

from utils import (
    load_transactions_from_csv,
    load_transactions_from_json,
    validate_transactions,
    build_transaction_graph,
    find_cycles_in_graph,
    compute_centrality_metrics,
    detect_communities,
    get_account_statistics
)


# ============================================================================
# CLASSE PRINCIPALE
# ============================================================================

class FraudDetector:
    """
    Moteur principal de détection de fraude financière par graphes.

    Cette classe permet de charger des transactions, construire des graphes
    transactionnels et détecter différents types de fraudes.

    Attributes:
        transactions: Liste des transactions chargées
        graph: Graphe transactionnel construit
        detection_results: Résultats des détections effectuées

    Example:
        >>> detector = FraudDetector()
        >>> detector.load_from_csv("data/transactions.csv")
        >>> detector.build_graph()
        >>> results = detector.detect_all()
        >>> report = detector.generate_report()
    """

    def __init__(self):
        """Initialise le détecteur de fraude."""
        self.transactions: List[Dict[str, Any]] = []
        self.graph: Optional[nx.DiGraph] = None
        self.detection_results: Dict[str, Any] = {
            'money_laundering_cycles': [],
            'smurfing_patterns': [],
            'network_anomalies': []
        }
        self.detection_params: Dict[str, Any] = {
            # Paramètres pour la détection de cycles
            'cycle_min_length': 3,
            'cycle_max_length': 10,
            'cycle_time_window_hours': 72,
            
            # Paramètres pour la détection de smurfing
            'smurfing_threshold': 10000,  # Seuil de déclaration typique
            'smurfing_min_transactions': 5,
            'smurfing_time_window_hours': 48,
            'smurfing_amount_ratio': 0.8,  # Ratio de similarité des montants
            
            # Paramètres pour la détection d'anomalies
            'anomaly_degree_threshold': 0.1,  # Seuil de centralité
            'anomaly_burst_threshold': 20,  # Nombre de tx en peu de temps
            'anomaly_burst_window_hours': 2,
            'anomaly_isolation_threshold': 0.7  # Ratio de tx internes
        }

    # =========================================================================
    # CHARGEMENT DES DONNÉES
    # =========================================================================

    def load_from_csv(self, filepath: str) -> None:
        """
        Charge les transactions depuis un fichier CSV.

        Args:
            filepath: Chemin vers le fichier CSV

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le format des données est invalide
        """
        self.transactions = load_transactions_from_csv(filepath)
        self._validate_loaded_data()

    def load_from_json(self, filepath: str) -> None:
        """
        Charge les transactions depuis un fichier JSON.

        Args:
            filepath: Chemin vers le fichier JSON

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le format des données est invalide
        """
        self.transactions = load_transactions_from_json(filepath)
        self._validate_loaded_data()

    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """
        Charge directement une liste de transactions.

        Args:
            transactions: Liste de dictionnaires de transactions

        Raises:
            ValueError: Si les transactions sont invalides
        """
        self.transactions = transactions
        self._validate_loaded_data()

    def _validate_loaded_data(self) -> None:
        """Valide les données chargées."""
        is_valid, errors = validate_transactions(self.transactions)
        if not is_valid:
            raise ValueError(f"Données invalides:\n" + "\n".join(errors))

    # =========================================================================
    # CONSTRUCTION DU GRAPHE
    # =========================================================================

    def build_graph(
        self,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None
    ) -> nx.DiGraph:
        """
        Construit le graphe transactionnel à partir des transactions chargées.

        Args:
            min_amount: Montant minimum pour inclure une transaction
            max_amount: Montant maximum pour inclure une transaction
            date_start: Date de début pour filtrer les transactions
            date_end: Date de fin pour filtrer les transactions

        Returns:
            Graphe NetworkX orienté
        """
        self.graph = build_transaction_graph(
            self.transactions,
            min_amount=min_amount,
            max_amount=max_amount,
            date_start=date_start,
            date_end=date_end
        )
        return self.graph

    # =========================================================================
    # DÉTECTION DE CYCLES DE BLANCHIMENT
    # =========================================================================

    def detect_money_laundering_cycles(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        time_window_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Détecte les cycles de blanchiment dans le graphe transactionnel.

        Un cycle de blanchiment est une boucle de transferts où les fonds
        reviennent à leur point d'origine après être passés par plusieurs
        comptes intermédiaires, masquant ainsi leur provenance.

        Args:
            min_length: Longueur minimale du cycle (défaut: paramètre de classe)
            max_length: Longueur maximale du cycle (défaut: paramètre de classe)
            time_window_hours: Fenêtre temporelle en heures (défaut: paramètre de classe)

        Returns:
            Liste de cycles détectés avec leurs métadonnées:
            [
                {
                    'cycle': ['ACC_0001', 'ACC_0002', 'ACC_0003', 'ACC_0001'],
                    'length': 4,
                    'total_amount': 50000.0,
                    'transactions': [...],
                    'risk_score': 0.85
                },
                ...
            ]
        """
        if self.graph is None:
            raise ValueError("Le graphe n'a pas été construit. Appelez build_graph() d'abord.")

        # Utiliser les paramètres par défaut si non spécifiés
        min_length = min_length or self.detection_params['cycle_min_length']
        max_length = max_length or self.detection_params['cycle_max_length']
        time_window_hours = time_window_hours or self.detection_params['cycle_time_window_hours']

        # Trouver tous les cycles dans le graphe
        all_cycles = find_cycles_in_graph(self.graph, min_length=min_length)

        detected_cycles = []

        for cycle in all_cycles:
            # Filtrer par longueur maximale
            if max_length and len(cycle) > max_length:
                continue

            # Analyser le cycle
            cycle_info = self._analyze_cycle(cycle, time_window_hours)
            if cycle_info:
                detected_cycles.append(cycle_info)

        # Trier par score de risque décroissant
        detected_cycles.sort(key=lambda x: x['risk_score'], reverse=True)

        self.detection_results['money_laundering_cycles'] = detected_cycles
        return detected_cycles

    def _analyze_cycle(
        self,
        cycle: List[str],
        time_window_hours: int
    ) -> Optional[Dict[str, Any]]:
        """
        Analyse un cycle pour déterminer s'il est suspect.

        Args:
            cycle: Liste des nœuds formant le cycle
            time_window_hours: Fenêtre temporelle en heures

        Returns:
            Informations sur le cycle ou None si non suspect
        """
        # Trouver les transactions formant le cycle
        cycle_transactions = []
        total_amount = 0
        amounts = []

        for i in range(len(cycle)):
            sender = cycle[i]
            receiver = cycle[(i + 1) % len(cycle)]

            # Trouver les transactions entre sender et receiver
            txs = [
                tx for tx in self.transactions
                if tx['sender_id'] == sender and tx['receiver_id'] == receiver
            ]

            if not txs:
                return None  # Cycle incomplet

            # Prendre la transaction la plus récente
            tx = max(txs, key=lambda x: x['timestamp'])
            cycle_transactions.append(tx)
            total_amount += tx['amount']
            amounts.append(tx['amount'])

        # Vérifier la fenêtre temporelle
        timestamps = [tx['timestamp'] for tx in cycle_transactions]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600

        if time_span > time_window_hours:
            return None  # Cycle trop étalé dans le temps

        # Calculer le score de risque
        risk_score = self._calculate_cycle_risk_score(
            cycle, cycle_transactions, total_amount, amounts, time_span
        )

        return {
            'cycle': cycle,
            'length': len(cycle),
            'total_amount': total_amount,
            'transactions': cycle_transactions,
            'time_span_hours': time_span,
            'amounts': amounts,
            'risk_score': risk_score,
            'detection_type': 'money_laundering_cycle'
        }

    def _calculate_cycle_risk_score(
        self,
        cycle: List[str],
        transactions: List[Dict[str, Any]],
        total_amount: float,
        amounts: List[float],
        time_span: float
    ) -> float:
        """
        Calcule un score de risque pour un cycle de blanchiment.

        Le score est basé sur plusieurs facteurs:
        - Montant total (plus élevé = plus suspect)
        - Variation des montants (plus faible = plus suspect)
        - Durée du cycle (plus courte = plus suspect)
        - Longueur du cycle (plus long = plus suspect)

        Args:
            cycle: Liste des nœuds
            transactions: Transactions du cycle
            total_amount: Montant total
            amounts: Liste des montants
            time_span: Durée en heures

        Returns:
            Score de risque entre 0 et 1
        """
        score = 0.0

        # Facteur 1: Montant total (normalisé)
        amount_score = min(total_amount / 100000, 1.0)  # 100k = score max
        score += amount_score * 0.3

        # Facteur 2: Variation des montants (plus faible = plus suspect)
        if len(amounts) > 1:
            amount_std = np.std(amounts)
            amount_mean = np.mean(amounts)
            variation_ratio = amount_std / amount_mean if amount_mean > 0 else 1
            variation_score = max(0, 1 - variation_ratio)
            score += variation_score * 0.25

        # Facteur 3: Durée du cycle (plus courte = plus suspect)
        time_score = max(0, 1 - time_span / 72)  # 72h = score min
        score += time_score * 0.25

        # Facteur 4: Longueur du cycle (plus long = plus suspect)
        length_score = min(len(cycle) / 10, 1.0)  # 10 nœuds = score max
        score += length_score * 0.2

        return min(score, 1.0)

    # =========================================================================
    # DÉTECTION DE SMURFING
    # =========================================================================

    def detect_smurfing(
        self,
        threshold: Optional[float] = None,
        min_transactions: Optional[int] = None,
        time_window_hours: Optional[int] = None,
        amount_ratio: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Détecte les patterns de smurfing (schtroumpfage).

        Le smurfing consiste à fractionner un montant important en plusieurs
        petites transactions vers un compte pivot pour éviter les seuils de
        déclaration obligatoire.

        Args:
            threshold: Seuil de déclaration (défaut: paramètre de classe)
            min_transactions: Nombre minimum de transactions (défaut: paramètre de classe)
            time_window_hours: Fenêtre temporelle en heures (défaut: paramètre de classe)
            amount_ratio: Ratio de similarité des montants (défaut: paramètre de classe)

        Returns:
            Liste de patterns de smurfing détectés:
            [
                {
                    'pivot_account': 'ACC_0042',
                    'total_amount': 95000.0,
                    'num_transactions': 12,
                    'avg_amount': 7916.67,
                    'transactions': [...],
                    'risk_score': 0.92
                },
                ...
            ]
        """
        if self.graph is None:
            raise ValueError("Le graphe n'a pas été construit. Appelez build_graph() d'abord.")

        # Utiliser les paramètres par défaut si non spécifiés
        threshold = threshold or self.detection_params['smurfing_threshold']
        min_transactions = min_transactions or self.detection_params['smurfing_min_transactions']
        time_window_hours = time_window_hours or self.detection_params['smurfing_time_window_hours']
        amount_ratio = amount_ratio or self.detection_params['smurfing_amount_ratio']

        detected_patterns = []

        # Analyser chaque compte comme pivot potentiel
        for node in self.graph.nodes():
            # Trouver toutes les transactions entrantes vers ce compte
            incoming_txs = [
                tx for tx in self.transactions
                if tx['receiver_id'] == node and tx['amount'] < threshold
            ]

            if len(incoming_txs) < min_transactions:
                continue

            # Analyser les transactions entrantes
            pattern_info = self._analyze_smurfing_pattern(
                node, incoming_txs, threshold, time_window_hours, amount_ratio
            )

            if pattern_info:
                detected_patterns.append(pattern_info)

        # Trier par score de risque décroissant
        detected_patterns.sort(key=lambda x: x['risk_score'], reverse=True)

        self.detection_results['smurfing_patterns'] = detected_patterns
        return detected_patterns

    def _analyze_smurfing_pattern(
        self,
        pivot_account: str,
        incoming_txs: List[Dict[str, Any]],
        threshold: float,
        time_window_hours: int,
        amount_ratio: float
    ) -> Optional[Dict[str, Any]]:
        """
        Analyse un pattern de smurfing potentiel.

        Args:
            pivot_account: Compte pivot
            incoming_txs: Transactions entrantes
            threshold: Seuil de déclaration
            time_window_hours: Fenêtre temporelle
            amount_ratio: Ratio de similarité des montants

        Returns:
            Informations sur le pattern ou None si non suspect
        """
        # Trier par timestamp
        incoming_txs.sort(key=lambda x: x['timestamp'])

        # Trouver les fenêtres temporelles avec suffisamment de transactions
        patterns = []

        for i in range(len(incoming_txs)):
            window_txs = [incoming_txs[i]]
            window_start = incoming_txs[i]['timestamp']

            for j in range(i + 1, len(incoming_txs)):
                time_diff = (incoming_txs[j]['timestamp'] - window_start).total_seconds() / 3600

                if time_diff > time_window_hours:
                    break

                window_txs.append(incoming_txs[j])

            if len(window_txs) >= self.detection_params['smurfing_min_transactions']:
                # Vérifier la similarité des montants
                amounts = [tx['amount'] for tx in window_txs]
                amount_mean = np.mean(amounts)
                amount_std = np.std(amounts)

                if amount_mean > 0:
                    cv = amount_std / amount_mean  # Coefficient de variation
                    if cv <= (1 - amount_ratio):  # Montants similaires
                        patterns.append({
                            'transactions': window_txs,
                            'amounts': amounts,
                            'cv': cv
                        })

        if not patterns:
            return None

        # Prendre le pattern le plus suspect
        best_pattern = max(patterns, key=lambda p: len(p['transactions']))

        total_amount = sum(best_pattern['amounts'])
        avg_amount = np.mean(best_pattern['amounts'])

        # Calculer le score de risque
        risk_score = self._calculate_smurfing_risk_score(
            pivot_account, best_pattern, total_amount, avg_amount, threshold
        )

        return {
            'pivot_account': pivot_account,
            'total_amount': total_amount,
            'num_transactions': len(best_pattern['transactions']),
            'avg_amount': avg_amount,
            'transactions': best_pattern['transactions'],
            'coefficient_of_variation': best_pattern['cv'],
            'risk_score': risk_score,
            'detection_type': 'smurfing'
        }

    def _calculate_smurfing_risk_score(
        self,
        pivot_account: str,
        pattern: Dict[str, Any],
        total_amount: float,
        avg_amount: float,
        threshold: float
    ) -> float:
        """
        Calcule un score de risque pour un pattern de smurfing.

        Args:
            pivot_account: Compte pivot
            pattern: Informations sur le pattern
            total_amount: Montant total
            avg_amount: Montant moyen
            threshold: Seuil de déclaration

        Returns:
            Score de risque entre 0 et 1
        """
        score = 0.0

        # Facteur 1: Nombre de transactions (plus élevé = plus suspect)
        num_tx_score = min(len(pattern['transactions']) / 20, 1.0)
        score += num_tx_score * 0.3

        # Facteur 2: Montant total (plus élevé = plus suspect)
        amount_score = min(total_amount / 200000, 1.0)
        score += amount_score * 0.3

        # Facteur 3: Proximité du seuil (juste en dessous = plus suspect)
        threshold_proximity = 1 - (avg_amount / threshold)
        proximity_score = max(0, threshold_proximity)
        score += proximity_score * 0.2

        # Facteur 4: Similarité des montants (plus similaire = plus suspect)
        similarity_score = 1 - pattern['cv']
        score += similarity_score * 0.2

        return min(score, 1.0)

    # =========================================================================
    # DÉTECTION D'ANOMALIES DE RÉSEAU
    # =========================================================================

    def detect_network_anomalies(
        self,
        degree_threshold: Optional[float] = None,
        burst_threshold: Optional[int] = None,
        burst_window_hours: Optional[int] = None,
        isolation_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Détecte les anomalies de réseau dans le graphe transactionnel.

        Les anomalies de réseau incluent:
        - Hubs: Comptes avec une centralité anormalement élevée
        - Bursts: Rafales de transactions sur une courte période
        - Communautés isolées: Groupes de comptes avec des transactions internes denses

        Args:
            degree_threshold: Seuil de centralité (défaut: paramètre de classe)
            burst_threshold: Nombre de tx pour un burst (défaut: paramètre de classe)
            burst_window_hours: Fenêtre temporelle pour burst (défaut: paramètre de classe)
            isolation_threshold: Ratio de tx internes (défaut: paramètre de classe)

        Returns:
            Liste d'anomalies détectées:
            [
                {
                    'account': 'ACC_0015',
                    'anomaly_type': 'hub',
                    'centrality_metrics': {...},
                    'risk_score': 0.78
                },
                ...
            ]
        """
        if self.graph is None:
            raise ValueError("Le graphe n'a pas été construit. Appelez build_graph() d'abord.")

        # Utiliser les paramètres par défaut si non spécifiés
        degree_threshold = degree_threshold or self.detection_params['anomaly_degree_threshold']
        burst_threshold = burst_threshold or self.detection_params['anomaly_burst_threshold']
        burst_window_hours = burst_window_hours or self.detection_params['anomaly_burst_window_hours']
        isolation_threshold = isolation_threshold or self.detection_params['anomaly_isolation_threshold']

        detected_anomalies = []

        # 1. Détecter les hubs (centralité élevée)
        hub_anomalies = self._detect_hub_anomalies(degree_threshold)
        detected_anomalies.extend(hub_anomalies)

        # 2. Détecter les bursts (rafales de transactions)
        burst_anomalies = self._detect_burst_anomalies(burst_threshold, burst_window_hours)
        detected_anomalies.extend(burst_anomalies)

        # 3. Détecter les communautés isolées
        community_anomalies = self._detect_isolated_communities(isolation_threshold)
        detected_anomalies.extend(community_anomalies)

        # Trier par score de risque décroissant
        detected_anomalies.sort(key=lambda x: x['risk_score'], reverse=True)

        self.detection_results['network_anomalies'] = detected_anomalies
        return detected_anomalies

    def _detect_hub_anomalies(self, degree_threshold: float) -> List[Dict[str, Any]]:
        """
        Détecte les comptes avec une centralité anormalement élevée.

        Args:
            degree_threshold: Seuil de centralité

        Returns:
            Liste d'anomalies de type hub
        """
        anomalies = []

        # Calculer les métriques de centralité
        centrality_metrics = compute_centrality_metrics(self.graph)

        # Calculer les seuils basés sur les percentiles
        degree_values = [m['degree_centrality'] for m in centrality_metrics.values()]
        if not degree_values:
            return anomalies

        degree_mean = np.mean(degree_values)
        degree_std = np.std(degree_values)
        dynamic_threshold = max(degree_threshold, degree_mean + 2 * degree_std)

        # Identifier les hubs
        for account, metrics in centrality_metrics.items():
            if metrics['degree_centrality'] > dynamic_threshold:
                risk_score = self._calculate_hub_risk_score(account, metrics, degree_mean, degree_std)

                anomalies.append({
                    'account': account,
                    'anomaly_type': 'hub',
                    'centrality_metrics': metrics,
                    'threshold': dynamic_threshold,
                    'risk_score': risk_score,
                    'detection_type': 'network_anomaly'
                })

        return anomalies

    def _calculate_hub_risk_score(
        self,
        account: str,
        metrics: Dict[str, float],
        mean: float,
        std: float
    ) -> float:
        """
        Calcule un score de risque pour une anomalie de type hub.

        Args:
            account: Compte
            metrics: Métriques de centralité
            mean: Moyenne de centralité
            std: Écart-type de centralité

        Returns:
            Score de risque entre 0 et 1
        """
        score = 0.0

        # Facteur 1: Écart par rapport à la moyenne
        z_score = (metrics['degree_centrality'] - mean) / std if std > 0 else 0
        z_score = min(z_score, 5)  # Plafonner à 5
        score += (z_score / 5) * 0.4

        # Facteur 2: Centralité d'intermédiarité
        betweenness_score = min(metrics['betweenness_centrality'] * 10, 1.0)
        score += betweenness_score * 0.3

        # Facteur 3: PageRank
        pagerank_score = min(metrics['pagerank'] * 10, 1.0)
        score += pagerank_score * 0.3

        return min(score, 1.0)

    def _detect_burst_anomalies(
        self,
        burst_threshold: int,
        burst_window_hours: int
    ) -> List[Dict[str, Any]]:
        """
        Détecte les rafales de transactions sur une courte période.

        Args:
            burst_threshold: Nombre minimum de transactions
            burst_window_hours: Fenêtre temporelle en heures

        Returns:
            Liste d'anomalies de type burst
        """
        anomalies = []

        # Grouper les transactions par émetteur
        sender_txs = {}
        for tx in self.transactions:
            sender = tx['sender_id']
            if sender not in sender_txs:
                sender_txs[sender] = []
            sender_txs[sender].append(tx)

        # Analyser chaque émetteur
        for sender, txs in sender_txs.items():
            if len(txs) < burst_threshold:
                continue

            # Trier par timestamp
            txs.sort(key=lambda x: x['timestamp'])

            # Chercher les fenêtres avec beaucoup de transactions
            for i in range(len(txs)):
                window_txs = [txs[i]]
                window_start = txs[i]['timestamp']

                for j in range(i + 1, len(txs)):
                    time_diff = (txs[j]['timestamp'] - window_start).total_seconds() / 3600

                    if time_diff > burst_window_hours:
                        break

                    window_txs.append(txs[j])

                if len(window_txs) >= burst_threshold:
                    risk_score = self._calculate_burst_risk_score(
                        sender, window_txs, burst_threshold, burst_window_hours
                    )

                    anomalies.append({
                        'account': sender,
                        'anomaly_type': 'burst',
                        'num_transactions': len(window_txs),
                        'time_window_hours': burst_window_hours,
                        'transactions': window_txs,
                        'risk_score': risk_score,
                        'detection_type': 'network_anomaly'
                    })
                    break  # Un burst par compte suffit

        return anomalies

    def _calculate_burst_risk_score(
        self,
        account: str,
        transactions: List[Dict[str, Any]],
        threshold: int,
        window_hours: int
    ) -> float:
        """
        Calcule un score de risque pour une anomalie de type burst.

        Args:
            account: Compte
            transactions: Transactions dans la fenêtre
            threshold: Seuil de transactions
            window_hours: Fenêtre temporelle

        Returns:
            Score de risque entre 0 et 1
        """
        score = 0.0

        # Facteur 1: Nombre de transactions
        num_tx_score = min(len(transactions) / (threshold * 2), 1.0)
        score += num_tx_score * 0.5

        # Facteur 2: Densité temporelle (transactions par heure)
        density = len(transactions) / window_hours
        density_score = min(density / 20, 1.0)  # 20 tx/heure = score max
        score += density_score * 0.5

        return min(score, 1.0)

    def _detect_isolated_communities(self, isolation_threshold: float) -> List[Dict[str, Any]]:
        """
        Détecte les communautés isolées avec des transactions internes denses.

        Args:
            isolation_threshold: Ratio minimum de transactions internes

        Returns:
            Liste d'anomalies de type communauté isolée
        """
        anomalies = []

        # Détecter les communautés
        communities = detect_communities(self.graph)

        # Analyser chaque communauté
        for community in communities:
            if len(community) < 3:  # Ignorer les petites communautés
                continue

            # Compter les transactions internes et externes
            internal_txs = 0
            external_txs = 0

            for tx in self.transactions:
                sender_in = tx['sender_id'] in community
                receiver_in = tx['receiver_id'] in community

                if sender_in and receiver_in:
                    internal_txs += 1
                elif sender_in or receiver_in:
                    external_txs += 1

            total_txs = internal_txs + external_txs
            if total_txs == 0:
                continue

            internal_ratio = internal_txs / total_txs

            if internal_ratio >= isolation_threshold:
                risk_score = self._calculate_community_risk_score(
                    community, internal_ratio, len(community)
                )

                anomalies.append({
                    'community': list(community),
                    'anomaly_type': 'isolated_community',
                    'internal_transactions': internal_txs,
                    'external_transactions': external_txs,
                    'internal_ratio': internal_ratio,
                    'risk_score': risk_score,
                    'detection_type': 'network_anomaly'
                })

        return anomalies

    def _calculate_community_risk_score(
        self,
        community: Set[str],
        internal_ratio: float,
        size: int
    ) -> float:
        """
        Calcule un score de risque pour une communauté isolée.

        Args:
            community: Ensemble de comptes
            internal_ratio: Ratio de transactions internes
            size: Taille de la communauté

        Returns:
            Score de risque entre 0 et 1
        """
        score = 0.0

        # Facteur 1: Ratio de transactions internes
        ratio_score = internal_ratio
        score += ratio_score * 0.6

        # Facteur 2: Taille de la communauté (plus grande = plus suspecte)
        size_score = min(size / 20, 1.0)
        score += size_score * 0.4

        return min(score, 1.0)

    # =========================================================================
    # DÉTECTION COMPLÈTE
    # =========================================================================

    def detect_all(self) -> Dict[str, Any]:
        """
        Exécute tous les algorithmes de détection.

        Returns:
            Dictionnaire contenant tous les résultats de détection:
            {
                'money_laundering_cycles': [...],
                'smurfing_patterns': [...],
                'network_anomalies': [...],
                'summary': {...}
            }
        """
        # Détecter les cycles de blanchiment
        cycles = self.detect_money_laundering_cycles()

        # Détecter le smurfing
        smurfing = self.detect_smurfing()

        # Détecter les anomalies de réseau
        anomalies = self.detect_network_anomalies()

        # Générer un résumé
        summary = {
            'total_cycles': len(cycles),
            'total_smurfing': len(smurfing),
            'total_anomalies': len(anomalies),
            'high_risk_cycles': len([c for c in cycles if c['risk_score'] > 0.7]),
            'high_risk_smurfing': len([s for s in smurfing if s['risk_score'] > 0.7]),
            'high_risk_anomalies': len([a for a in anomalies if a['risk_score'] > 0.7])
        }

        return {
            'money_laundering_cycles': cycles,
            'smurfing_patterns': smurfing,
            'network_anomalies': anomalies,
            'summary': summary
        }

    # =========================================================================
    # GÉNÉRATION DE RAPPORT
    # =========================================================================

    def generate_report(self, results: Optional[Dict[str, Any]] = None) -> str:
        """
        Génère un rapport de détection formaté.

        Args:
            results: Résultats de détection (si None, utilise les résultats stockés)

        Returns:
            Rapport sous forme de chaîne de caractères
        """
        if results is None:
            results = {
                'money_laundering_cycles': self.detection_results['money_laundering_cycles'],
                'smurfing_patterns': self.detection_results['smurfing_patterns'],
                'network_anomalies': self.detection_results['network_anomalies']
            }

        report = []
        report.append("=" * 80)
        report.append("RAPPORT DE DÉTECTION DE FRAUDE FINANCIÈRE")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Nombre de transactions analysées: {len(self.transactions)}")
        if self.graph:
            report.append(f"Nombre de comptes: {self.graph.number_of_nodes()}")
            report.append(f"Nombre d'arêtes: {self.graph.number_of_edges()}")
        report.append("")

        # Résumé
        report.append("-" * 80)
        report.append("RÉSUMÉ")
        report.append("-" * 80)
        report.append(f"Cycles de blanchiment détectés: {len(results['money_laundering_cycles'])}")
        report.append(f"Patterns de smurfing détectés: {len(results['smurfing_patterns'])}")
        report.append(f"Anomalies de réseau détectées: {len(results['network_anomalies'])}")
        report.append("")

        # Cycles de blanchiment
        if results['money_laundering_cycles']:
            report.append("-" * 80)
            report.append("CYCLES DE BLANCHIMENT")
            report.append("-" * 80)
            for i, cycle in enumerate(results['money_laundering_cycles'][:10], 1):
                report.append(f"\nCycle #{i} (Score: {cycle['risk_score']:.2f})")
                report.append(f"  Longueur: {cycle['length']}")
                report.append(f"  Montant total: {cycle['total_amount']:,.2f} €")
                report.append(f"  Durée: {cycle['time_span_hours']:.1f} heures")
                report.append(f"  Comptes: {' -> '.join(cycle['cycle'])}")
            if len(results['money_laundering_cycles']) > 10:
                report.append(f"\n... et {len(results['money_laundering_cycles']) - 10} autres cycles")
            report.append("")

        # Smurfing
        if results['smurfing_patterns']:
            report.append("-" * 80)
            report.append("PATTERNS DE SMURFING")
            report.append("-" * 80)
            for i, pattern in enumerate(results['smurfing_patterns'][:10], 1):
                report.append(f"\nPattern #{i} (Score: {pattern['risk_score']:.2f})")
                report.append(f"  Compte pivot: {pattern['pivot_account']}")
                report.append(f"  Nombre de transactions: {pattern['num_transactions']}")
                report.append(f"  Montant total: {pattern['total_amount']:,.2f} €")
                report.append(f"  Montant moyen: {pattern['avg_amount']:,.2f} €")
            if len(results['smurfing_patterns']) > 10:
                report.append(f"\n... et {len(results['smurfing_patterns']) - 10} autres patterns")
            report.append("")

        # Anomalies de réseau
        if results['network_anomalies']:
            report.append("-" * 80)
            report.append("ANOMALIES DE RÉSEAU")
            report.append("-" * 80)
            for i, anomaly in enumerate(results['network_anomalies'][:10], 1):
                report.append(f"\nAnomalie #{i} (Score: {anomaly['risk_score']:.2f})")
                report.append(f"  Type: {anomaly['anomaly_type']}")
                if anomaly['anomaly_type'] == 'hub':
                    report.append(f"  Compte: {anomaly['account']}")
                    report.append(f"  Centralité: {anomaly['centrality_metrics']['degree_centrality']:.4f}")
                elif anomaly['anomaly_type'] == 'burst':
                    report.append(f"  Compte: {anomaly['account']}")
                    report.append(f"  Transactions: {anomaly['num_transactions']}")
                elif anomaly['anomaly_type'] == 'isolated_community':
                    report.append(f"  Taille: {len(anomaly['community'])} comptes")
                    report.append(f"  Ratio interne: {anomaly['internal_ratio']:.2%}")
            if len(results['network_anomalies']) > 10:
                report.append(f"\n... et {len(results['network_anomalies']) - 10} autres anomalies")
            report.append("")

        # Alertes à haut risque
        high_risk_items = []
        high_risk_items.extend([
            ('Cycle', c) for c in results['money_laundering_cycles'] if c['risk_score'] > 0.7
        ])
        high_risk_items.extend([
            ('Smurfing', s) for s in results['smurfing_patterns'] if s['risk_score'] > 0.7
        ])
        high_risk_items.extend([
            ('Anomalie', a) for a in results['network_anomalies'] if a['risk_score'] > 0.7
        ])

        if high_risk_items:
            report.append("=" * 80)
            report.append("⚠️  ALERTES À HAUT RISQUE (Score > 0.7)")
            report.append("=" * 80)
            for item_type, item in high_risk_items:
                report.append(f"\n{item_type} - Score: {item['risk_score']:.2f}")
                if item_type == 'Cycle':
                    report.append(f"  Comptes: {' -> '.join(item['cycle'])}")
                elif item_type == 'Smurfing':
                    report.append(f"  Compte pivot: {item['pivot_account']}")
                elif item_type == 'Anomalie':
                    if item['anomaly_type'] == 'hub':
                        report.append(f"  Compte: {item['account']}")
                    elif item['anomaly_type'] == 'burst':
                        report.append(f"  Compte: {item['account']}")
                    elif item['anomaly_type'] == 'isolated_community':
                        report.append(f"  Communauté: {len(item['community'])} comptes")

        report.append("\n" + "=" * 80)
        report.append("FIN DU RAPPORT")
        report.append("=" * 80)

        return "\n".join(report)

    # =========================================================================
    # EXPORT DES RÉSULTATS
    # =========================================================================

    def export_results_to_json(self, filepath: str) -> None:
        """
        Exporte les résultats de détection vers un fichier JSON.

        Args:
            filepath: Chemin du fichier de sortie
        """
        import json

        # Préparer les données pour l'export
        export_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'transactions_count': len(self.transactions),
            'results': {
                'money_laundering_cycles': self._serialize_cycles(
                    self.detection_results['money_laundering_cycles']
                ),
                'smurfing_patterns': self._serialize_smurfing(
                    self.detection_results['smurfing_patterns']
                ),
                'network_anomalies': self._serialize_anomalies(
                    self.detection_results['network_anomalies']
                )
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

    def _serialize_cycles(self, cycles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sérialise les cycles pour l'export JSON."""
        serialized = []
        for cycle in cycles:
            serialized.append({
                'cycle': cycle['cycle'],
                'length': cycle['length'],
                'total_amount': cycle['total_amount'],
                'time_span_hours': cycle['time_span_hours'],
                'risk_score': cycle['risk_score'],
                'transaction_ids': [tx['transaction_id'] for tx in cycle['transactions']]
            })
        return serialized

    def _serialize_smurfing(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sérialise les patterns de smurfing pour l'export JSON."""
        serialized = []
        for pattern in patterns:
            serialized.append({
                'pivot_account': pattern['pivot_account'],
                'total_amount': pattern['total_amount'],
                'num_transactions': pattern['num_transactions'],
                'avg_amount': pattern['avg_amount'],
                'risk_score': pattern['risk_score'],
                'transaction_ids': [tx['transaction_id'] for tx in pattern['transactions']]
            })
        return serialized

    def _serialize_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sérialise les anomalies pour l'export JSON."""
        serialized = []
        for anomaly in anomalies:
            data = {
                'anomaly_type': anomaly['anomaly_type'],
                'risk_score': anomaly['risk_score']
            }
            if anomaly['anomaly_type'] == 'hub':
                data['account'] = anomaly['account']
                data['centrality_metrics'] = anomaly['centrality_metrics']
            elif anomaly['anomaly_type'] == 'burst':
                data['account'] = anomaly['account']
                data['num_transactions'] = anomaly['num_transactions']
            elif anomaly['anomaly_type'] == 'isolated_community':
                data['community'] = anomaly['community']
                data['internal_ratio'] = anomaly['internal_ratio']
            serialized.append(data)
        return serialized

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def set_detection_params(self, **kwargs) -> None:
        """
        Met à jour les paramètres de détection.

        Args:
            **kwargs: Paramètres à mettre à jour
        """
        for key, value in kwargs.items():
            if key in self.detection_params:
                self.detection_params[key] = value
            else:
                raise ValueError(f"Paramètre inconnu: {key}")

    def get_detection_params(self) -> Dict[str, Any]:
        """
        Retourne les paramètres de détection actuels.

        Returns:
            Dictionnaire des paramètres
        """
        return self.detection_params.copy()
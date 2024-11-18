from typing import List, Tuple, Dict, Set
import json

class LureNotifier:
    TERMS = ['cisco', 'gmail', 'login', 'mail', 'paying', 'paypal', '.gov']

    def __init__(self, domains: List[str], subscriptions: Dict[str, List[str]], team_hierarchy: Dict[str, str]):
        self.TARGET_DOMAINS = domains  # List of domains
        self.SUBSCRIPTIONS = subscriptions  # Dict of user subscriptions
        self.USER_TO_MANAGER_DICT = team_hierarchy  # Dict of each user and who they report to (one report at a time)
        # Cache user_hierarchy and team_notifications_map on init to prevent redundant computations
        self.USER_REPORTS_CHAIN_MAP = self._build_user_reports_chain_map() # Dict[user, Set[all users who report to this user]]
        self.TERM_NOTIFICATIONS_MAP = self._precompute_notifications(self.USER_REPORTS_CHAIN_MAP) # Dict[term, Set[users who need to be notified]]

    # Helper functions to compute invariant vars on object init
    def _build_user_reports_chain_map(self) -> Dict[str, Set[str]]:
        """Builds a dictionary where each user_id maps to a set of all users below them in the reporting chain."""
        user_hierarchy_map = {}

        def gather_subordinates(user_id: str) -> Set[str]:
            if user_id in user_hierarchy_map:
                return user_hierarchy_map[user_id]

            subordinates = set()
            for user, manager in self.USER_TO_MANAGER_DICT.items():
                if manager == user_id:
                    subordinates.add(user)
                    subordinates.update(gather_subordinates(user))
            user_hierarchy_map[user_id] = subordinates
            return subordinates

        for user in self.USER_TO_MANAGER_DICT:
            gather_subordinates(user)

        return user_hierarchy_map

    def _precompute_notifications(self, user_hierarchy_map: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """Precomputes and returns a dictionary where each term maps to a set of all users to notify for that term."""
        term_notifications = {}

        for user_id, terms in self.SUBSCRIPTIONS.items():
            for term in terms:
                if term not in term_notifications:
                    term_notifications[term] = set()
                term_notifications[term].add(user_id)
                term_notifications[term].update(user_hierarchy_map.get(user_id, set()))

        return term_notifications

    # domain argument is a little redundant because LureNotifier is initialized with a list of target domains, but will leave in case a user wants to give a new list of domains to the same notifier
    def identify_lures(self, domains: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Identifies potential phishing lures from a list of candidate domains

        :param domains: list of domains as strings
        :return: list of tuples (domain, [matched_terms...])
        """
        # store the target domains so notify can access them without changing notify signature
        self.TARGET_DOMAINS = domains
        lures = []
    
        # iterate through list of domains
        for domain in domains:
            # Convert to lower case to avoid case issues
            lower_domain = domain.lower()
            
            # Match terms from term list with terms in list of target domains
            matched_terms = [term for term in self.TERMS if term in lower_domain]
            
            # If two or more terms are present, add to the lures list
            if len(matched_terms) >= 2:
                lures.append((domain, matched_terms))
        
        return lures

    def notify(self, lures: List[Tuple[str, List[str]]]) -> List[Tuple[str, List[str]]]:
        """
        Notifies users if lures are found containing specific terms

        :param lures: output from self.identify_lures
        :return: list of tuples (domain, [user_ids...])
        """

        # We already know the team hierarchy, so we can compute who we need to notify for each term when its hit
                
        # Step 1: Create a dictionary to store notifications for each domain
        domain_notifications = {}

        # Step 2: For each lure (domain and its terms), gather users to notify
        for domain, terms in lures:
            users_to_notify = set()  # Use a set to avoid duplicate notifications

            # Step 3: Gather users to notify for each term in this domain
            for term in terms:
                users_to_notify.update(self.TERM_NOTIFICATIONS_MAP.get(term, set()))


            # Convert set to list and store it in the domain notifications
            # Does this need to be a list? Seems like it might be better as a set
            domain_notifications[domain] = list(users_to_notify)

        return domain_notifications



def test_identify_lures():
    domains = ['paypal-login.appspot.com', 'ciscomail.com', 'cisco.heroku.com', 'apple.com'] 
    # Expected: [(paypal-login.appspot.com, [paypal, login]), (ciscomail.com, [cisco, mail])]
    return notifier.identify_lures(domains)


def test_notify():
    lures = test_identify_lures()
    # Expected: [(paypal-login.appspot.com, [B, E]), (ciscomail.com, [A, C, K, B, E])]
    return notifier.notify(lures)

# Helper function to read the list of domains
def read_domain_list_from_file(file_path: str) -> List[str]:
    """Reads a list of domains from a file and returns it as a list of strings.
    :param file_path: Path to read domains from
    :return: list of domain strings 
    """
    with open(file_path, 'r') as file:
        domains = file.read().splitlines()
    return domains

def load_user_subscriptions(file_path: str) -> Dict[str, List[str]]:
    """Loads user subscriptions from a JSON lines file into a dictionary."""
    subscriptions = {}
    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line.strip())
            user_id = entry['id']
            term = entry['term']
            
            # Initialize user's list if not already present, then append the term
            if user_id not in subscriptions:
                subscriptions[user_id] = []
            subscriptions[user_id].append(term)
            
    return subscriptions

def load_user_to_manager_map(file_path: str) -> Dict[str, str]:
    """Loads team hierarchy from a JSON lines file into a dictionary."""
    hierarchy = {}
    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line.strip())
            user_id = entry['id']
            manager_id = entry['reports_to']
            hierarchy[user_id] = manager_id
            
    return hierarchy


# expected_identify_lures = [('paypal-login.appspot.com', ['paypal', 'login']), ('ciscomail.com', ['cisco', 'mail'])]
# expected_notify = [('paypal-login.appspot.com', ['B', 'E']), ('ciscomail.com', ['A', 'C', 'K', 'B', 'E'])]

# Run script
if __name__ == "__main__":
    # print("Running test_identify_lures...")
    # print(test_identify_lures())
    
    # print("\nRunning test_notify...")
    # test_notify()


    # Read data into correct structures
    subscription_file_path = 'coop-code-challenge-subscriptions.jsonlines'
    subscriptions = load_user_subscriptions(file_path=subscription_file_path)
    
    graph_file_path = 'coop-code-challenge-graph.jsonlines'
    team_hierarchy_graph = load_user_to_manager_map(file_path=graph_file_path)
    
    domain_file_path = 'coop-code-challenge-domains.txt'
    domains = read_domain_list_from_file(file_path=domain_file_path)
    
    # # init notifier with domain list, subscriptions and hierarchy
    notifier = LureNotifier(domains=domains, subscriptions=subscriptions, team_hierarchy=team_hierarchy_graph)
    # # identify the lures using the domains we initialized notifier with
    lures = notifier.identify_lures(domains=notifier.TARGET_DOMAINS)
    # notify users when needed
    # print(notifier.notify(lures=lures))
    print(test_notify())
"""DOCFIND console application: search a collection of university passages.

Run from the project folder:
    python main.py                       (interactive menu)
    python main.py --full --index "binary search"
Options: --show --index --linear --compare --full --official
"""

import sys

from src.config import (
    DATA_FILE, FULL_DATA_FILE, OFFICIAL_DATA_FILE, MAX_RESULTS, NO_EVIDENCE_MESSAGE,
)
from src.loader import REQUIRED_FIELDS, check_fields, load_passages
from src.ranking import rank_candidates
from src.search import STRATEGIES, get_candidates, run_search
from src.tokenizer import tokenize, unique_tokens
from src.versions import get_outdated_passage_ids

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:  # colorama is optional: without it the program simply prints no colours
    class _NoColour:
        def __getattr__(self, name):
            return ""
    Fore = Style = _NoColour()

TITLE_COLOR = Fore.CYAN + Style.BRIGHT
EXPECTED_COUNT = 5
KNOWN_FLAGS = ["--show", "--index", "--linear", "--compare", "--full", "--official"]
METHOD_NAMES = ["linear scan", "inverted index"]


# ---------------------------------------------------------------
# Screens: banner, passage listing, search results, comparison
# ---------------------------------------------------------------

def print_banner():
    print(TITLE_COLOR + "=" * 60)
    print(TITLE_COLOR + "              MUET DOCFIND")
    print(TITLE_COLOR + "   DSA-Powered Document Retrieval Engine")
    print(TITLE_COLOR + "=" * 60)
    print(Fore.WHITE + "  Mehran University of Engineering & Technology")
    print(Fore.YELLOW + "  Search | Rank | Compare | Retrieve")
    print("=" * 60)


def print_passage(number, passage):
    """Show one passage with all of its metadata."""
    print("-" * 60)
    print(f"Passage {number}")
    for field in REQUIRED_FIELDS:
        print(f"{field:<12}: {passage.get(field, '<MISSING>')}")


def show_all_passages(passages):
    """Show every passage, then run the basic checks on the collection."""
    print(f"Loaded {len(passages)} passage(s).")
    for number, passage in enumerate(passages, start=1):
        print_passage(number, passage)
    print("-" * 60)

    print("CHECKS")
    if len(passages) == EXPECTED_COUNT:
        print(f"PASS: exactly {EXPECTED_COUNT} passages were loaded.")
    elif len(passages) >= 100:
        print(f"PASS: full corpus contains {len(passages)} passages.")
    else:
        print(f"INFO: {len(passages)} passages were loaded.")
    problems = check_fields(passages)
    if not problems:
        print(f"PASS: every passage has all {len(REQUIRED_FIELDS)} required fields, and none are empty.")
    else:
        for problem in problems:
            print("FAIL: " + problem)


def print_result(rank, match, total_query_words, outdated_ids):
    """Show one search result with its metadata and why it was chosen."""
    passage = match["passage"]
    print("-" * 60)
    print(f"Result {rank} | Score: {match['score']} of {total_query_words} query word(s)")
    print(f"passage_id  : {passage['passage_id']}")
    print(f"document_id : {passage['document_id']}")
    print(f"title       : {passage['title']}")
    print(f"category    : {passage['category']}")
    print(f"source      : {passage['source']}")
    print(f"version     : {passage['version']}")
    if passage["passage_id"] in outdated_ids:
        print("status      : OUTDATED - newer version available")
    else:
        print("status      : CURRENT")
    print(f"date        : {passage['date']}")
    print(f"matched     : {', '.join(match['matched_words'])}")
    print(f"text        : {passage['text']}")


def print_comparison(candidates, query_words):
    """Rank the SAME candidates with every strategy and show the results side by side."""
    print(f"Comparing {len(STRATEGIES)} ranking strategies on the SAME {len(candidates)} candidate(s):")
    orders = []
    for number, strategy in enumerate(STRATEGIES, start=1):
        ranked = rank_candidates(candidates, strategy, len(query_words), MAX_RESULTS)
        print("-" * 60)
        print(f"Strategy {number}: {strategy.name}")
        order = []
        for rank, match in enumerate(ranked, start=1):
            passage = match["passage"]
            print(f"  {rank}. {passage['passage_id']}  version {passage['version']}  "
                  f"score {strategy.show(match['score'])}  matched: {', '.join(match['matched_words'])}")
            order.append(passage["passage_id"])
        orders.append(order)
    print("-" * 60)
    if all(order == orders[0] for order in orders):
        print("Result: all strategies give the same order for this query.")
    else:
        print("Result: the strategies give DIFFERENT orders for this query.")


# ---------------------------------------------------------------
# Command line
# ---------------------------------------------------------------

def parse_arguments(arguments):
    """Split the words typed after 'python main.py' into (options, query words).

    Anything starting with -- is an option; everything else is part of the query.
    """
    options = []
    query_parts = []
    for argument in arguments:
        if argument.startswith("--"):
            options.append(argument)
        else:
            query_parts.append(argument)
    return options, query_parts


def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    options, query_parts = parse_arguments(arguments)

    for option in options:
        if option not in KNOWN_FLAGS:
            print(f"ERROR: unknown option '{option}'. Known options: {', '.join(KNOWN_FLAGS)}")
            return

    if "--official" in options:
        selected_file = OFFICIAL_DATA_FILE
    elif "--full" in options:
        selected_file = FULL_DATA_FILE
    else:
        selected_file = DATA_FILE
    try:
        passages = load_passages(selected_file)
    except FileNotFoundError:
        print(f"ERROR: could not find {selected_file}.")
        return
    except ValueError as error:
        print(f"ERROR: {selected_file} could not be read as a list of passages: {error}")
        return

    problems = check_fields(passages)
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        return
    print_banner()
    if "--official" in options:
        print("NOTE: searching official MUET source passages.")
    else:
        print("NOTE: this dataset contains SYNTHETIC demonstration data.")

    if "--show" in options:
        show_all_passages(passages)
        return

    if len(query_parts) > 0:
        query = " ".join(query_parts)
    else:
        query = input("Enter your search query: ")

    query_words = unique_tokens(tokenize(query))
    print(f"Query       : '{query}'")

    if len(query_words) == 0:
        print("Blank query: please type at least one word to search for.")
        return

    print(f"Query words : {', '.join(query_words)}")

    if "--index" in options:
        method = "index"
        print(f"Method      : {METHOD_NAMES[1]}")
    else:
        method = "linear"
        print(f"Method      : {METHOD_NAMES[0]}")

    if len(passages) == 0:
        print(NO_EVIDENCE_MESSAGE)
        print("(The passage collection is empty.)")
        return

    if "--compare" in options:
        candidates = get_candidates(method, passages, query_words)
        if len(candidates) == 0:
            print(NO_EVIDENCE_MESSAGE)
            return
        print_comparison(candidates, query_words)
        return

    results = run_search(method, passages, query_words)

    if len(results) == 0:
        print(NO_EVIDENCE_MESSAGE)
        return

    outdated_ids = get_outdated_passage_ids(passages)
    print(f"Found {len(results)} result(s) (at most {MAX_RESULTS} are shown):")
    for rank, match in enumerate(results, start=1):
        print_result(rank, match, len(query_words), outdated_ids)
    print("-" * 60)


def interactive_menu():
    """Show the main menu until the user chooses 0."""
    while True:
        print_banner()
        print(Fore.CYAN + Style.BRIGHT + "\n  MAIN MENU")
        print(Fore.WHITE + "  [1] Search documents")
        print(Fore.WHITE + "  [2] Search using inverted index")
        print(Fore.WHITE + "  [3] Compare ranking strategies")
        print(Fore.WHITE + "  [4] View all synthetic passages")
        print(Fore.WHITE + "  [5] Search official MUET documents")
        print(Fore.WHITE + "  [6] View official passages")
        print(Fore.WHITE + "  [0] Exit")
        print(Fore.CYAN + "-" * 60)

        choice = input(Fore.YELLOW + "  Enter your choice: ").strip()

        if choice == "0":
            print(Fore.GREEN + "\nThank you for using MUET DOCFIND!")
            break
        elif choice == "1":
            query = input("  Enter search query: ").strip()
            main(["--full", "--linear"] + query.split())
        elif choice == "2":
            query = input("  Enter search query: ").strip()
            main(["--full", "--index"] + query.split())
        elif choice == "3":
            query = input("  Enter search query: ").strip()
            main(["--full", "--compare"] + query.split())
        elif choice == "4":
            main(["--full", "--show"])
            input("\nPress Enter to return to the menu...")
        elif choice == "5":
            query = input("  Enter search query for official MUET documents: ").strip()
            main(["--official", "--index"] + query.split())
            input("\nPress Enter to return to the menu...")
        elif choice == "6":
            main(["--official", "--show"])
            input("\nPress Enter to return to the menu...")
        else:
            print("Invalid choice. Please select 0 to 6.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        main()

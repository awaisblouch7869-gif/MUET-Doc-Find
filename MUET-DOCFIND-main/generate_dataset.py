
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


OUTPUT_FILE = ROOT / "data/full_corpus.json"

SOURCE = (
    "SYNTHETIC - generated for a class project; "
    "not official university policy"
)

topics = [
    ("Data Structures", "Course Contents", [
        "arrays", "linked lists", "stacks", "queues",
        "hash tables", "binary trees", "graphs", "heaps",
        "linear search", "binary search", "bubble sort",
        "merge sort", "quick sort", "recursion",
        "time complexity", "space complexity",
        "insertion sort", "selection sort", "tree traversal",
        "breadth first search", "depth first search",
        "priority queues", "collision handling",
        "hash functions", "dynamic arrays", "circular queues",
        "doubly linked lists", "adjacency lists",
        "minimum spanning trees", "shortest paths"
    ]),
    ("Laboratory", "Laboratory Rules", [
        "save lab files", "submit assignments",
        "test program output", "document errors",
        "follow lab instructions", "organize source code",
        "check input values", "review test cases",
        "record observations", "back up project files",
        "use meaningful filenames", "compile before submission",
        "check expected output", "write test cases",
        "maintain a lab notebook", "report technical problems",
        "verify program results", "read error messages",
        "keep project folders organized", "test boundary values",
        "avoid duplicate files", "review source code",
        "document program steps", "check file permissions",
        "prepare sample inputs", "validate user input",
        "record execution time", "test invalid inputs",
        "save final versions", "review lab requirements"
    ]),
    ("Examination", "Examination Procedures", [
        "midterm examination", "final examination",
        "student identification", "exam timetable",
        "practice questions", "revision schedule",
        "written answers", "exam preparation",
        "course assessment", "sample paper",
        "multiple choice questions", "short answer questions",
        "long answer questions", "time management",
        "revision notes", "practice exercises",
        "exam instructions", "question paper format",
        "answer organization", "concept revision",
        "mock examination", "topic checklist",
        "formula review", "problem solving practice",
        "past paper practice", "study timetable",
        "answer checking", "exam readiness",
        "concept summaries", "practice test results"
    ]),
    ("Programming", "Programming Skills", [
        "Python functions", "object oriented programming",
        "variables and data types", "loops and conditions",
        "exception handling", "file operations",
        "classes and objects", "debugging code",
        "algorithm analysis", "unit testing",
        "string processing", "list operations",
        "tuple operations", "set operations",
        "dictionary operations", "reading text files",
        "writing JSON files", "input validation",
        "modular programming", "function parameters",
        "return values", "inheritance", "encapsulation",
        "polymorphism", "recursion practice",
        "sorting algorithms", "search algorithms",
        "code readability", "error handling",
        "software testing"
    ]),
    ("Library", "Library Services", [
        "book search", "library catalogue",
        "digital resources", "research references",
        "study space", "book return",
        "reading materials", "academic journals",
        "citation practice", "research planning",
        "book classification", "author search",
        "title search", "keyword search",
        "reference management", "academic databases",
        "online journals", "research keywords",
        "literature review", "source evaluation",
        "bibliography preparation", "library membership",
        "book availability", "subject catalogue",
        "digital archives", "research notes",
        "citation formats", "reading lists",
        "information retrieval", "document search"
    ]),
]

passages = []
passage_number = 1

for topic_number, (topic, category, concepts) in enumerate(topics, start=1):
    for concept_number, concept in enumerate(concepts, start=1):
        passages.append({
            "passage_id": f"P{passage_number:03d}",
            "document_id": f"D{((passage_number - 1) // 5) + 1:02d}",
            "title": f"{topic} Information (SYNTHETIC)",
            "category": category,
            "source": SOURCE,
            "version": "v2" if passage_number == 15 else "v1",
            "date": "2026-10-01",
            "text": (
                f"This synthetic example covers {concept}. "
                f"The topic is included to demonstrate document "
                f"retrieval, keyword matching, ranking, and evaluation. "
                f"Students can use {concept} for practice and review."
            ),
        })
        passage_number += 1

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text(
    json.dumps(passages, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Created {len(passages)} synthetic passages.")
print(f"Saved to: {OUTPUT_FILE}")


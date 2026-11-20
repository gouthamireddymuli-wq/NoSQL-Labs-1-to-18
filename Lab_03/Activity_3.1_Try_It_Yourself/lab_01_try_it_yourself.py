"""Activity 3.1 (Try It Yourself): Course Prerequisites Architecture & Implementation
Architectural decision & PyMongo implementation for tracking course prerequisites.
Demonstrates referenced vs embedded design, $lookup joins, recursive $graphLookup DAG traversal,
and student enrollment eligibility validation.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
for path in (BASE_DIR, PARENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from config.connection import get_db, banner, export_collection_to_json

# --- COURSE CATALOG WITH REFERENCED PREREQUISITES ---
COURSES_CATALOG = [
    {
        "code": "CS101",
        "title": "Introduction to Programming & Python",
        "instructor": "Dr. Ramesh Nair",
        "credits": 3,
        "prerequisites": [],  # Entry-level foundational course
        "description": "Fundamental programming paradigms, control flow, functions, and data structures."
    },
    {
        "code": "MATH101",
        "title": "Discrete Mathematics & Linear Algebra",
        "instructor": "Dr. Sunita Rao",
        "credits": 4,
        "prerequisites": [],  # Entry-level foundational course
        "description": "Vector spaces, matrices, eigenvalues, graph theory, and combinatorics."
    },
    {
        "code": "CS201",
        "title": "Data Structures & Algorithms",
        "instructor": "Dr. Anil Gupta",
        "credits": 4,
        "prerequisites": ["CS101"],
        "description": "Trees, heaps, graphs, hashing, sorting, dynamic programming, and complexity."
    },
    {
        "code": "CS301",
        "title": "Database Management Systems",
        "instructor": "Dr. Priya Sharma",
        "credits": 4,
        "prerequisites": ["CS201"],
        "description": "Relational algebra, normalization, transaction management, indexing, and NoSQL."
    },
    {
        "code": "CS401",
        "title": "Advanced Machine Learning",
        "instructor": "Dr. Anil Gupta",
        "credits": 4,
        "prerequisites": ["CS201", "MATH101"],
        "description": "Supervised, unsupervised, deep neural networks, attention mechanisms, and optimization."
    },
    {
        "code": "CS402",
        "title": "Distributed Cloud Systems",
        "instructor": "Dr. Meera Joshi",
        "credits": 4,
        "prerequisites": ["CS201", "CS301"],
        "description": "Consensus protocols, Paxos/Raft, distributed storage, replication, and CAP theorem."
    }
]

# Simulated Student Transcripts (completed courses with grades)
STUDENT_PROFILES = [
    {
        "student_id": "STU1001",
        "name": "Arjun Mehta",
        "completed_courses": [
            {"code": "CS101", "grade": "A"},
            {"code": "CS201", "grade": "A-"},
            {"code": "MATH101", "grade": "B+"}
        ]
    },
    {
        "student_id": "STU1002",
        "name": "Sneha Reddy",
        "completed_courses": [
            {"code": "CS101", "grade": "A"},
            {"code": "MATH101", "grade": "A"}
            # Missing CS201
        ]
    }
]


def print_architectural_justification():
    """Print the architectural justification for referencing vs embedding prerequisites."""
    print("=" * 72)
    print("ARCHITECTURAL DECISION & JUSTIFICATION: EMBED VS. REFERENCE")
    print("=" * 72)
    print("""
[Decision]: REFERENCED MODEL (Array of Course Codes / References)
------------------------------------------------------------------------
1. Why NOT Full Embedding:
   • Duplication & Update Anomalies:
     CS101 is a prerequisite for CS201, which is a prerequisite for CS301,
     CS401, CS402, etc. If CS101 were embedded inside every course, a change
     in syllabus, instructor, or credits would require updating dozens of
     duplicated sub-documents across multiple collections.
   • Bounded Document Size:
     Embedding prerequisite trees creates nested hierarchies. If a course
     has 5 prerequisites, and each has 3, an embedded tree balloons rapidly.
   • Risk of Circular/Cyclic Nesting:
     In academic curriculum modeling, courses represent a Directed Acyclic
     Graph (DAG). Full embedding cannot represent graph sharing without
     duplicating nodes or risking infinite recursive loops.

2. Why Referencing (Array of Foreign Keys):
   • Normalized Single Source of Truth: Each course exists exactly once in
     the 'courses' collection with full details.
   • Extremely Lightweight: Storing ['CS201', 'MATH101'] adds only tens of
     bytes per document.
   • Dynamic Graph Traversal via MongoDB $lookup & $graphLookup:
     Allows resolving immediate prerequisites via $lookup and recursive
     multilevel dependency chains via $graphLookup in a single pipeline.
   • Clean Validation: Enables straightforward verification of student
     prerequisites before permitting enrollment.
    """)


def main():
    banner("Activity 3.1 (Try It Yourself): Course Prerequisites")
    print_architectural_justification()

    db = get_db("nosql_labs")

    # Recreate collection
    col_name = "course_prerequisites"
    if col_name in db.list_collection_names():
        db.drop_collection(col_name)
    col = db[col_name]

    # Insert courses
    col.insert_many(COURSES_CATALOG)
    print(f"[OK] Seeded {len(COURSES_CATALOG)} courses with prerequisite references.\n")

    # --- PART 1: Query immediate prerequisites using $lookup ---
    print("=" * 72)
    print("PART 1: Resolving Immediate Prerequisites with $lookup")
    print("=" * 72)
    pipeline_lookup = [
        {"$match": {"prerequisites": {"$ne": []}}},
        {
            "$lookup": {
                "from": col_name,
                "localField": "prerequisites",
                "foreignField": "code",
                "as": "prerequisite_details"
            }
        },
        {
            "$project": {
                "_id": 0,
                "code": 1,
                "title": 1,
                "prerequisites": 1,
                "prereq_titles": "$prerequisite_details.title"
            }
        }
    ]
    resolved = list(col.aggregate(pipeline_lookup))
    for r in resolved:
        prereq_list = ", ".join(f"{c}" for c in r["prerequisites"])
        title_list = " | ".join(r["prereq_titles"])
        print(f"Course [{r['code']}] {r['title']}")
        print(f"  • Required Codes : [{prereq_list}]")
        print(f"  • Resolved Titles: {title_list}\n")

    # --- PART 2: Recursive DAG Traversal using $graphLookup ---
    print("=" * 72)
    print("PART 2: Transitive Dependency Tree Traversal with $graphLookup")
    print("=" * 72)
    target_course = "CS402"
    pipeline_graph = [
        {"$match": {"code": target_course}},
        {
            "$graphLookup": {
                "from": col_name,
                "startWith": "$prerequisites",
                "connectFromField": "prerequisites",
                "connectToField": "code",
                "as": "full_prerequisite_tree",
                "depthField": "dependency_depth"
            }
        },
        {
            "$project": {
                "_id": 0,
                "code": 1,
                "title": 1,
                "direct_prereqs": "$prerequisites",
                "transitive_prereqs": {
                    "$map": {
                        "input": "$full_prerequisite_tree",
                        "as": "item",
                        "in": {
                            "code": "$$item.code",
                            "title": "$$item.title",
                            "depth": "$$item.dependency_depth"
                        }
                    }
                }
            }
        }
    ]
    graph_res = list(col.aggregate(pipeline_graph))[0]
    print(f"Target Course: [{graph_res['code']}] {graph_res['title']}")
    print(f"  Direct Prerequisites: {graph_res['direct_prereqs']}")
    print(f"  All Recursive Dependencies (Transitive DAG):")
    sorted_tree = sorted(graph_res["transitive_prereqs"], key=lambda x: x["depth"])
    for node in sorted_tree:
        indent = "    " * (node["depth"] + 1)
        print(f"{indent}↳ [Depth {node['depth']}] [{node['code']}] {node['title']}")
    print()

    # --- PART 3: Student Enrollment Eligibility Validation ---
    print("=" * 72)
    print("PART 3: Automated Student Enrollment Eligibility Validation")
    print("=" * 72)
    target_enrollment_course = "CS401"  # Requires CS201 and MATH101
    course_doc = col.find_one({"code": target_enrollment_course})
    required_prereqs = set(course_doc["prerequisites"])

    print(f"Attempting Enrollment in [{course_doc['code']}] {course_doc['title']}")
    print(f"Mandatory Prerequisites: {sorted(list(required_prereqs))}\n")

    for student in STUDENT_PROFILES:
        completed_codes = {c["code"] for c in student["completed_courses"]}
        missing_prereqs = required_prereqs - completed_codes

        print(f"Student: {student['name']} ({student['student_id']})")
        print(f"  Completed Courses: {sorted(list(completed_codes))}")
        if not missing_prereqs:
            print(f"  [STATUS]: APPROVED - All prerequisites fulfilled! Enrolling in {target_enrollment_course}.\n")
        else:
            print(f"  [STATUS]: REJECTED - Missing prerequisites: {sorted(list(missing_prereqs))}!\n")

    # Step 4: Export collection state to JSON
    json_path = os.path.join(BASE_DIR, "course_prerequisites.json")
    export_collection_to_json("nosql_labs", col_name, json_path)

    banner("Activity 3.1 Try It Yourself Complete")


if __name__ == "__main__":
    main()

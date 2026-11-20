"""Lab 3.1 - Design an Embedded Document Schema
University Course Enrollment System with Embedded Student Roster and Schedule.
Includes JSON Schema validation, day queries, and instructor-student queries.
"""

import os
import sys
from pymongo.errors import WriteError

# Ensure parent directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
for path in (BASE_DIR, PARENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from config.connection import get_db, banner, export_collection_to_json

# --- 1. JSON Schema Validator for Courses Collection ---
COURSE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "code", "instructor", "schedule"],
        "properties": {
            "title": {
                "bsonType": "string",
                "description": "Course title is required and must be a string"
            },
            "code": {
                "bsonType": "string",
                "pattern": r"^[A-Z]{2,4}\d{3}$",
                "description": "Course code format: e.g. CS401, AIML101 (required)"
            },
            "instructor": {
                "bsonType": "string",
                "description": "Instructor name is required and must be a string"
            },
            "credits": {
                "bsonType": "int",
                "minimum": 1,
                "maximum": 6,
                "description": "Credits must be an integer between 1 and 6"
            },
            "schedule": {
                "bsonType": "object",
                "required": ["days", "times", "room"],
                "description": "Embedded schedule with days, times, and room",
                "properties": {
                    "days": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "List of meeting days (required)"
                    },
                    "times": {
                        "bsonType": "string",
                        "description": "Meeting time range (required)"
                    },
                    "room": {
                        "bsonType": "string",
                        "description": "Classroom or lecture hall (required)"
                    }
                }
            },
            "roster": {
                "bsonType": "array",
                "description": "Embedded roster of enrolled students",
                "items": {
                    "bsonType": "object",
                    "required": ["name", "ID"],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "Student full name (required)"
                        },
                        "ID": {
                            "bsonType": "string",
                            "description": "Student identification number (required)"
                        },
                        "grade": {
                            "bsonType": ["string", "null"],
                            "description": "Letter grade or null if in progress"
                        }
                    }
                }
            }
        }
    }
}

# --- 2. Realistic Course Data (4 courses with embedded roster and schedule) ---
SAMPLE_COURSES = [
    {
        "title": "Advanced Database Systems",
        "code": "CS401",
        "instructor": "Dr. Priya Sharma",
        "credits": 4,
        "schedule": {
            "days": ["Monday", "Wednesday"],
            "times": "10:00 - 11:30 AM",
            "room": "Lecture Hall 201"
        },
        "roster": [
            {"name": "Arjun Mehta", "ID": "STU1001", "grade": "A"},
            {"name": "Sneha Reddy", "ID": "STU1002", "grade": "B+"},
            {"name": "Rahul Kumar", "ID": "STU1003", "grade": "A-"},
            {"name": "Divya Patel", "ID": "STU1004", "grade": "B"}
        ]
    },
    {
        "title": "Machine Learning & Pattern Recognition",
        "code": "CS402",
        "instructor": "Dr. Anil Gupta",
        "credits": 4,
        "schedule": {
            "days": ["Tuesday", "Thursday"],
            "times": "02:00 - 03:30 PM",
            "room": "Science Block 305"
        },
        "roster": [
            {"name": "Arjun Mehta", "ID": "STU1001", "grade": None},
            {"name": "Kavya Nair", "ID": "STU1005", "grade": "A"},
            {"name": "Vikram Singh", "ID": "STU1006", "grade": "A+"}
        ]
    },
    {
        "title": "Natural Language Processing",
        "code": "CS403",
        "instructor": "Dr. Priya Sharma",
        "credits": 3,
        "schedule": {
            "days": ["Monday", "Wednesday", "Friday"],
            "times": "09:00 - 10:00 AM",
            "room": "Lab Block 102"
        },
        "roster": [
            {"name": "Sneha Reddy", "ID": "STU1002", "grade": "A"},
            {"name": "Priya Das", "ID": "STU1007", "grade": "A-"},
            {"name": "Arjun Mehta", "ID": "STU1001", "grade": None},
            {"name": "Neha Gupta", "ID": "STU1008", "grade": "B+"}
        ]
    },
    {
        "title": "Distributed Cloud Computing",
        "code": "CS404",
        "instructor": "Dr. Meera Joshi",
        "credits": 3,
        "schedule": {
            "days": ["Monday", "Thursday"],
            "times": "11:30 AM - 01:00 PM",
            "room": "Tech Tower 404"
        },
        "roster": [
            {"name": "Rahul Kumar", "ID": "STU1003", "grade": "A"},
            {"name": "Kavya Nair", "ID": "STU1005", "grade": "B+"},
            {"name": "Amit Verma", "ID": "STU1009", "grade": "A"}
        ]
    }
]


def main():
    banner("Activity 3.1: Embedded Document Schema Design & Validation")

    db = get_db("nosql_labs")

    # Step 1: Drop and recreate courses collection with JSON Schema validator
    if "courses" in db.list_collection_names():
        db.drop_collection("courses")
    db.create_collection("courses", validator=COURSE_VALIDATOR)
    col = db["courses"]
    print("[OK] Successfully created 'courses' collection with JSON Schema validation.\n")

    # Step 2: Insert Course Documents
    result = col.insert_many(SAMPLE_COURSES)
    print(f"[OK] Inserted {len(result.inserted_ids)} course documents successfully.\n")

    # Step 3: Query for all courses that meet on Monday
    print("=" * 65)
    print("QUERY 1: Courses that Meet on Monday (schedule.days: 'Monday')")
    print("=" * 65)
    monday_courses = list(col.find(
        {"schedule.days": "Monday"},
        {"_id": 0, "title": 1, "code": 1, "instructor": 1, "schedule": 1}
    ))
    for idx, c in enumerate(monday_courses, 1):
        sched = c["schedule"]
        days_str = ", ".join(sched["days"])
        print(f" {idx}. [{c['code']}] {c['title']}")
        print(f"    Instructor: {c['instructor']}")
        print(f"    Schedule  : {days_str} @ {sched['times']} in {sched['room']}")
    print(f"\n Total Monday courses found: {len(monday_courses)}\n")

    # Step 4: Query students enrolled in courses taught by Dr. Priya Sharma
    target_instructor = "Dr. Priya Sharma"
    print("=" * 65)
    print(f"QUERY 2: Students Enrolled in Courses Taught by '{target_instructor}'")
    print("=" * 65)

    # Aggregation pipeline to unwind roster and get unique enrolled students
    pipeline = [
        {"$match": {"instructor": target_instructor}},
        {"$unwind": "$roster"},
        {
            "$project": {
                "_id": 0,
                "course_code": "$code",
                "course_title": "$title",
                "student_name": "$roster.name",
                "student_id": "$roster.ID",
                "student_grade": "$roster.grade"
            }
        }
    ]
    student_records = list(col.aggregate(pipeline))
    for rec in student_records:
        grade_str = rec["student_grade"] if rec["student_grade"] else "In Progress"
        print(f"  • {rec['student_name']:<15} (ID: {rec['student_id']}) -> [{rec['course_code']}] Grade: {grade_str}")

    # Unique students count
    unique_students = {r["student_id"]: r["student_name"] for r in student_records}
    print(f"\n Total enrollments under {target_instructor}: {len(student_records)}")
    print(f" Distinct students count: {len(unique_students)} ({', '.join(unique_students.values())})\n")

    # Step 5: Test Schema Validation - Negative Test
    print("=" * 65)
    print("SCHEMA VALIDATION TEST: Negative Test (Invalid Document Rejection)")
    print("=" * 65)
    invalid_doc = {
        "title": "Invalid Quantum AI Course",
        # Missing required fields: 'code', 'instructor', 'schedule'
        "credits": 3
    }
    try:
        col.insert_one(invalid_doc)
        print("  [ERROR] Document insertion should have failed validation!")
    except WriteError as e:
        print("  [OK] MongoDB schema validator successfully REJECTED invalid document:")
        print(f"       WriteError code : {e.code}")
        print(f"       Details         : {e.details.get('errmsg', 'Document failed validation')[:100]}...\n")

    # Step 6: Export collection state to JSON
    json_path = os.path.join(BASE_DIR, "courses_embedded.json")
    export_collection_to_json("nosql_labs", "courses", json_path)

    banner("Activity 3.1 Execution Complete")


if __name__ == "__main__":
    main()

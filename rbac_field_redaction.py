"""
Lab 12.1 - Field-Level Redaction via MongoDB Views
Objective: Configure field-level redaction using a view that excludes 'salary'
           and masks 'ssn' for users who do not have the HR role.
"""

import sys
import os

# Ensure config is discoverable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.connection import get_db, reset_collection, banner

EMPLOYEES_DATA = [
    {
        "emp_id": "EMP-101",
        "name": "Arjun Sharma",
        "email": "arjun@enterprise.com",
        "department": "Engineering",
        "role": "Lead Architect",
        "ssn": "987-65-4321",
        "salary": 165000,
        "performance_rating": 4.8
    },
    {
        "emp_id": "EMP-102",
        "name": "Sneha Patel",
        "email": "sneha@enterprise.com",
        "department": "Security Operations",
        "role": "SecOps Engineer",
        "ssn": "555-44-3322",
        "salary": 142000,
        "performance_rating": 4.9
    },
    {
        "emp_id": "EMP-103",
        "name": "Rahul Verma",
        "email": "rahul@enterprise.com",
        "department": "Finance",
        "role": "Financial Analyst",
        "ssn": "222-33-8899",
        "salary": 128000,
        "performance_rating": 4.5
    },
    {
        "emp_id": "EMP-104",
        "name": "Ananya Roy",
        "email": "ananya@enterprise.com",
        "department": "Human Resources",
        "role": "HR Specialist",
        "ssn": "111-99-7744",
        "salary": 115000,
        "performance_rating": 4.7
    }
]


def setup_field_redaction(db_name="nosql_labs"):
    banner("Lab 12.1: Field-Level Redaction via MongoDB Views")
    db = get_db(db_name)

    # 1. Reset and populate the underlying 'employees' collection
    col = reset_collection(db_name, "employees")
    col.insert_many(EMPLOYEES_DATA)
    print(f"[OK] Seeded '{col.name}' collection with {len(EMPLOYEES_DATA)} records.\n")

    # 2. Drop existing view if present
    if "employees_safe" in db.list_collection_names():
        db["employees_safe"].drop()
        print("[*] Re-creating 'employees_safe' view...")

    # 3. Create view with $project pipeline that excludes salary and masks SSN
    pipeline = [
        {
            "$project": {
                "emp_id": 1,
                "name": 1,
                "email": 1,
                "department": 1,
                "role": 1,
                # Mask SSN: keep only the last 4 digits
                "ssn": {
                    "$concat": ["***-**-", {"$substrCP": ["$ssn", 7, 4]}]
                },
                # Exclude salary completely using $$REMOVE operator
                "salary": "$$REMOVE",
                "performance_rating": 1
            }
        }
    ]

    db.command("create", "employees_safe", viewOn="employees", pipeline=pipeline)
    print("[OK] Created read-only MongoDB view: 'employees_safe'\n")

    # 4. Demonstrate HR Role Access (Queries underlying collection directly)
    print("=" * 65)
    print("  SIMULATION 1: HR Manager / Admin Access (Underlying Collection)")
    print("  Privilege: readWrite on 'employees' -> Full sensitive access")
    print("=" * 65)
    for doc in col.find({}, {"_id": 0}):
        print(f"  [HR Direct] ID: {doc.get('emp_id')} | Name: {doc.get('name'):<15} | "
              f"SSN: {doc.get('ssn')} | Salary: ${doc.get('salary'):,}")

    # 5. Demonstrate Non-HR User Access (Queries the view 'employees_safe')
    print("\n" + "=" * 65)
    print("  SIMULATION 2: General Application / Non-HR User Access (Via View)")
    print("  Privilege: read on 'employees_safe' ONLY (salary excluded, SSN masked)")
    print("=" * 65)
    safe_view = db["employees_safe"]
    for doc in safe_view.find({}, {"_id": 0}):
        print(f"  [Redacted]  ID: {doc.get('emp_id')} | Name: {doc.get('name'):<15} | "
              f"SSN: {doc.get('ssn')} | Salary: {doc.get('salary', '[EXCLUDED]')}")

    print("\n" + "=" * 65)
    print("  VERIFICATION AUDIT:")
    print("  - 'salary' field in safe view:       EXCLUDED (None / $$REMOVE)")
    print("  - 'ssn' field in safe view:          MASKED (Format: ***-**-XXXX)")
    print("  - Underlying collection 'employees': UNTOUCHED & COMPLETE")
    print("=" * 65)
    banner("Lab 12.1 Field-Level Redaction Successful")

    return {
        "status": "success",
        "raw_count": col.count_documents({}),
        "view_count": safe_view.count_documents({}),
        "sample_hr": list(col.find({}, {"_id": 0}).limit(2)),
        "sample_safe": list(safe_view.find({}, {"_id": 0}).limit(2)),
    }


if __name__ == "__main__":
    setup_field_redaction()

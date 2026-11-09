import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("hospital.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def rows(query, params=()):
    with connect() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY, name TEXT NOT NULL, age INTEGER,
            gender TEXT, phone TEXT, disease TEXT, doctor TEXT, status TEXT
        );
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            department TEXT, phone TEXT, availability TEXT
        );
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            role TEXT, phone TEXT, shift TEXT
        );
        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY CHECK (id=1), total INTEGER NOT NULL,
            occupied INTEGER NOT NULL
        );
        INSERT OR IGNORE INTO beds (id,total,occupied) VALUES (1,100,0);
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patient TEXT, doctor TEXT,
            appt_date TEXT, appt_time TEXT, reason TEXT, status TEXT DEFAULT 'Booked'
        );
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patient TEXT, amount REAL,
            description TEXT, payment_status TEXT DEFAULT 'Pending'
        );
        """)

def add_patient(*args):
    with connect() as conn:
        conn.execute("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)", args)

def get_patients():
    return rows("SELECT * FROM patients ORDER BY name")

def update_patient(patient_id, status):
    with connect() as conn:
        conn.execute("UPDATE patients SET status=? WHERE patient_id=?", (status, patient_id))

def delete_patient(patient_id):
    with connect() as conn:
        conn.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))

def add_doctor(name, department, phone, availability):
    with connect() as conn:
        conn.execute("INSERT INTO doctors(name,department,phone,availability) VALUES(?,?,?,?)",
                     (name, department, phone, availability))

def get_doctors():
    return rows("SELECT * FROM doctors ORDER BY name")

def delete_doctor(record_id):
    with connect() as conn:
        conn.execute("DELETE FROM doctors WHERE id=?", (record_id,))

def add_staff(name, role, phone, shift):
    with connect() as conn:
        conn.execute("INSERT INTO staff(name,role,phone,shift) VALUES(?,?,?,?)",
                     (name, role, phone, shift))

def get_staff():
    return rows("SELECT * FROM staff ORDER BY name")

def delete_staff(record_id):
    with connect() as conn:
        conn.execute("DELETE FROM staff WHERE id=?", (record_id,))

def get_beds():
    r = rows("SELECT total,occupied FROM beds WHERE id=1")[0]
    return r["total"], r["occupied"]

def update_beds(total, occupied):
    if occupied > total:
        raise ValueError("Occupied beds cannot exceed total beds")
    with connect() as conn:
        conn.execute("UPDATE beds SET total=?,occupied=? WHERE id=1", (total, occupied))

def add_appointment(patient, doctor, appt_date, appt_time, reason):
    with connect() as conn:
        conn.execute("INSERT INTO appointments(patient,doctor,appt_date,appt_time,reason) VALUES(?,?,?,?,?)",
                     (patient, doctor, appt_date, appt_time, reason))

def get_appointments():
    return rows("SELECT * FROM appointments ORDER BY appt_date,appt_time")

def update_appointment_status(record_id, status):
    with connect() as conn:
        conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, record_id))

def add_bill(patient, amount, description):
    with connect() as conn:
        conn.execute("INSERT INTO bills(patient,amount,description) VALUES(?,?,?)",
                     (patient, amount, description))

def get_bills():
    return rows("SELECT * FROM bills ORDER BY id DESC")

def update_bill_status(record_id, status):
    with connect() as conn:
        conn.execute("UPDATE bills SET payment_status=? WHERE id=?", (status, record_id))

def get_dashboard_stats():
    with connect() as conn:
        cur = conn.cursor()
        patients = cur.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        admitted = cur.execute("SELECT COUNT(*) FROM patients WHERE status='Admitted'").fetchone()[0]
        discharged = cur.execute("SELECT COUNT(*) FROM patients WHERE status='Discharged'").fetchone()[0]
        doctors = cur.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        staff = cur.execute("SELECT COUNT(*) FROM staff").fetchone()[0]
        total, occupied = cur.execute("SELECT total,occupied FROM beds WHERE id=1").fetchone()
    return {
        "patients": patients, "admitted": admitted, "discharged": discharged,
        "doctors": doctors, "staff": staff, "total_beds": total,
        "occupied_beds": occupied, "available_beds": total - occupied
    }

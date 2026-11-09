import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import (
    init_db, add_patient, get_patients, update_patient, delete_patient,
    add_doctor, get_doctors, delete_doctor,
    add_staff, get_staff, delete_staff,
    get_beds, update_beds,
    add_appointment, get_appointments, update_appointment_status,
    add_bill, get_bills, update_bill_status,
    get_dashboard_stats
)

st.set_page_config(page_title="Hanvitha Speciality Hospital", page_icon="🏥", layout="wide")
init_db()

# Demo-only login. Change these before any private/local use.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "hospital123"

def login_screen():
    st.markdown("<h1 style='text-align:center;color:#176B87'>🏥 HANVITHA SPECIALITY HOSPITAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Hospital Management System • Admin Portal</p>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        with st.container(border=True):
            st.subheader("🔐 Admin Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
    st.caption("College project demonstration only. Do not enter real patient information.")

if not st.session_state.get("authenticated", False):
    login_screen()
    st.stop()

st.sidebar.markdown("## 🏥 Hanvitha Speciality Hospital")
st.sidebar.caption("Admin Management Portal")
page = st.sidebar.radio("Navigation", [
    "Dashboard", "Patients", "Doctors", "Staff", "Bed Management",
    "Appointments", "Billing"
])
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.title(page)

if page == "Dashboard":
    stats = get_dashboard_stats()
    cols = st.columns(4)
    labels = [
        ("Total Patients", stats["patients"]),
        ("Total Doctors", stats["doctors"]),
        ("Staff Members", stats["staff"]),
        ("Total Beds", stats["total_beds"]),
        ("Available Beds", stats["available_beds"]),
        ("Occupied Beds", stats["occupied_beds"]),
        ("Admitted Patients", stats["admitted"]),
        ("Discharged Patients", stats["discharged"]),
    ]
    for i, (label, value) in enumerate(labels):
        with cols[i % 4]:
            st.metric(label, value)
    st.divider()
    st.subheader("Hospital Overview")
    st.info("Use the sidebar to register patients, manage doctors and staff, track beds, appointments and bills.")
    st.caption("All records are stored locally in the SQLite database file: hospital.db")

elif page == "Patients":
    st.subheader("Register New Patient")
    with st.form("patient_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        pid = c1.text_input("Patient ID *")
        name = c2.text_input("Patient Name *")
        age = c3.number_input("Age", min_value=0, max_value=120, value=18)
        c4, c5, c6 = st.columns(3)
        gender = c4.selectbox("Gender", ["Not specified", "Female", "Male", "Other"])
        phone = c5.text_input("Phone")
        disease = c6.text_input("Disease / Reason for visit")
        doctor = st.text_input("Assigned Doctor")
        status = st.selectbox("Patient Status", ["Admitted", "Outpatient", "Discharged"])
        submitted = st.form_submit_button("Add Patient")
        if submitted:
            if not pid.strip() or not name.strip():
                st.error("Patient ID and Patient Name are required.")
            else:
                try:
                    add_patient(pid.strip(), name.strip(), int(age), gender, phone.strip(), disease.strip(), doctor.strip(), status)
                    st.success("Patient added successfully.")
                except Exception as e:
                    st.error(f"Could not add patient. Check that the Patient ID is unique. ({e})")

    st.divider()
    st.subheader("Patient Records")
    patients = get_patients()
    if patients:
        st.dataframe(pd.DataFrame(patients), use_container_width=True, hide_index=True)
        with st.expander("Update patient status"):
            ids = [p["patient_id"] for p in patients]
            selected = st.selectbox("Select Patient ID", ids)
            new_status = st.selectbox("New Status", ["Admitted", "Outpatient", "Discharged"], key="patient_status")
            if st.button("Update Status"):
                update_patient(selected, status=new_status)
                st.success("Patient status updated.")
                st.rerun()
        with st.expander("Delete patient record"):
            del_id = st.selectbox("Patient ID to delete", [p["patient_id"] for p in patients], key="del_patient")
            if st.button("Delete Patient"):
                delete_patient(del_id)
                st.success("Patient record deleted.")
                st.rerun()
    else:
        st.info("No patient records yet.")

elif page == "Doctors":
    st.subheader("Add Doctor")
    with st.form("doctor_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Doctor Name *")
        department = c2.text_input("Speciality / Department")
        phone = c3.text_input("Contact Number")
        availability = st.selectbox("Availability", ["Available", "Unavailable", "On Leave"])
        if st.form_submit_button("Add Doctor"):
            if name.strip():
                add_doctor(name.strip(), department.strip(), phone.strip(), availability)
                st.success("Doctor added.")
            else:
                st.error("Doctor name is required.")
    records = get_doctors()
    st.subheader("Doctor Directory")
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        choice = st.selectbox("Doctor ID to remove", [r["id"] for r in records])
        if st.button("Remove Doctor"):
            delete_doctor(choice)
            st.rerun()
    else:
        st.info("No doctors added yet.")

elif page == "Staff":
    st.subheader("Add Staff Member")
    with st.form("staff_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Staff Name *")
        role = c2.text_input("Designation / Role")
        phone = c3.text_input("Contact Number")
        shift = st.selectbox("Shift", ["Morning", "Evening", "Night", "General"])
        if st.form_submit_button("Add Staff"):
            if name.strip():
                add_staff(name.strip(), role.strip(), phone.strip(), shift)
                st.success("Staff member added.")
            else:
                st.error("Staff name is required.")
    records = get_staff()
    st.subheader("Staff Directory")
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        choice = st.selectbox("Staff ID to remove", [r["id"] for r in records])
        if st.button("Remove Staff"):
            delete_staff(choice)
            st.rerun()
    else:
        st.info("No staff members added yet.")

elif page == "Bed Management":
    total, occupied = get_beds()
    st.subheader("Bed Availability")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Beds", total)
    c2.metric("Occupied Beds", occupied)
    c3.metric("Available Beds", total - occupied)
    with st.form("bed_form"):
        new_total = st.number_input("Total number of beds", min_value=1, value=total)
        new_occupied = st.number_input("Currently occupied beds", min_value=0, max_value=int(new_total), value=min(occupied, int(new_total)))
        if st.form_submit_button("Save Bed Details"):
            update_beds(int(new_total), int(new_occupied))
            st.success("Bed details saved.")
            st.rerun()
    st.caption("Keep bed counts updated manually to match your demonstration records.")

elif page == "Appointments":
    st.subheader("Book Appointment")
    with st.form("appointment_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        patient = c1.text_input("Patient Name *")
        doctor = c2.text_input("Doctor Name")
        c3, c4 = st.columns(2)
        appt_date = c3.date_input("Appointment Date", value=date.today())
        appt_time = c4.time_input("Appointment Time")
        reason = st.text_input("Reason")
        if st.form_submit_button("Book Appointment"):
            if patient.strip():
                add_appointment(patient.strip(), doctor.strip(), str(appt_date), str(appt_time), reason.strip())
                st.success("Appointment booked.")
            else:
                st.error("Patient name is required.")
    records = get_appointments()
    st.subheader("Appointment List")
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        ids = [r["id"] for r in records]
        selected = st.selectbox("Appointment ID", ids)
        status = st.selectbox("Update status", ["Booked", "Completed", "Cancelled"])
        if st.button("Update Appointment"):
            update_appointment_status(selected, status)
            st.rerun()
    else:
        st.info("No appointments yet.")

elif page == "Billing":
    st.subheader("Create Patient Bill")
    with st.form("bill_form", clear_on_submit=True):
        patient = st.text_input("Patient Name *")
        amount = st.number_input("Bill Amount (₹)", min_value=0.0, step=100.0)
        description = st.text_input("Bill Description")
        if st.form_submit_button("Create Bill"):
            if patient.strip():
                add_bill(patient.strip(), float(amount), description.strip())
                st.success("Bill created.")
            else:
                st.error("Patient name is required.")
    records = get_bills()
    st.subheader("Billing Records")
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        ids = [r["id"] for r in records]
        selected = st.selectbox("Bill ID", ids)
        status = st.selectbox("Payment Status", ["Pending", "Paid"])
        if st.button("Update Payment Status"):
            update_bill_status(selected, status)
            st.rerun()
    else:
        st.info("No bills yet.")

st.divider()
st.caption("Hanvitha Speciality Hospital • Student demonstration project • Local database")

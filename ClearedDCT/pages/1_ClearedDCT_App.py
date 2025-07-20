import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

outbox_file = "outbox.json"
if not os.path.exists(outbox_file):
    with open(outbox_file, "w") as f:
        json.dump([], f)

st.markdown("""
    <style>
    .stApp { background-color: #e6f2ff; }
    h1, h2, h3, h4, h5, h6 { color: #003366; font-weight: bold; }
    .stButton>button { background-color: #4da6ff; color: white; font-weight: bold; font-size: 16px; }
    .stTextInput>div>input, .stTextArea>div>textarea { background-color: #ffffff; color: #000000; font-size: 16px; }
    .stSelectbox>div>div>div>div { font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

clouds_animation = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_pprxh53t.json")
st_lottie(clouds_animation, speed=1, height=150, key="clouds")

st.markdown("<h2 style='text-align: center;'>ClearedDCT Flight Plan & Message App</h2>", unsafe_allow_html=True)

def load_flight_plans():
    if os.path.exists("flight_plans.json"):
        with open("flight_plans.json", "r") as f:
            return json.load(f)
    return {}

def save_flight_plans(plans):
    with open("flight_plans.json", "w") as f:
        json.dump(plans, f)

def load_outbox():
    if os.path.exists("outbox.json"):
        with open("outbox.json", "r") as f:
            return json.load(f)
    return []

def save_outbox(outbox):
    with open("outbox.json", "w") as f:
        json.dump(outbox, f)

flight_plans = load_flight_plans()
outbox = load_outbox()

tabs = st.tabs(["✈️ Create Flight Plan", "📂 Load/Manage Flight Plans", "🛫 Generate Messages", "📤 Outbox"])

with tabs[0]:
    st.header("✈️ Create New Flight Plan")
    fp = {}
    fp["7"] = st.text_input("Aircraft Identification (Item 7, max 6)")
    fp["8"] = st.selectbox("Flight Rules (Item 8)", ["I", "V", "Y", "Z"])
    fp["8_type"] = st.selectbox("Type of Flight (Item 8)", ["S", "G", "N", "M", "X"])
    fp["9"] = st.text_input("Type of Aircraft (Item 9, max 4)")
    fp["9_wtc"] = st.selectbox("Wake Turbulence Category (Item 9)", ["L", "M", "H", "J"])
    fp["10"] = st.text_input("Equipment (Item 10, max 8)")
    fp["10_ssr"] = st.selectbox("SSR Equipment (Item 10)", ["A", "C", "S"])
    fp["13"] = st.text_input("Aerodrome of Departure (Item 13, max 4)")
    fp["13_eobt"] = st.text_input("EOBT (Item 13, HHMM)")
    fp["15_speed"] = st.text_input("Cruising Speed (Item 15)")
    fp["15_level"] = st.text_input("Level (Item 15)")
    fp["15_route"] = st.text_input("Route (Item 15)")
    fp["16_dest"] = st.text_input("Destination Aerodrome (Item 16, max 4)")
    fp["16_eet"] = st.text_input("EET (Item 16, HHMM)")
    fp["16_alt1"] = st.text_input("First Alternate Aerodrome (Item 16)")
    fp["16_alt2"] = st.text_input("Second Alternate Aerodrome (Item 16)")
    fp["18"] = st.text_area("Other Information (Item 18)")
    fp["19_endurance"] = st.text_input("Endurance (Item 19, HHMM)")
    fp["19_pob"] = st.text_input("Persons on Board (Item 19)")
    fp["19_color"] = st.text_input("Aircraft Color/Markings (Item 19)")
    fp["19_pilot"] = st.text_input("Pilot in Command (Item 19)")

    if st.button("Save Flight Plan ✈️"):
        if fp["7"]:
            flight_plans[fp["7"]] = fp
            save_flight_plans(flight_plans)
            st.success("✅ Flight Plan Saved.")
            st.rerun()
        else:
            st.error("Aircraft Identification (Item 7) is required.")

with tabs[1]:
    st.header("📂 Load, Edit, or Delete Flight Plans")
    if flight_plans:
        selected_fp_key = st.selectbox("Select Flight Plan to Load", list(flight_plans.keys()))
        if st.button("Edit Selected Flight Plan"):
            st.session_state["edit_fp_key"] = selected_fp_key
            st.rerun()
        if st.button("Delete Selected Flight Plan"):
            del flight_plans[selected_fp_key]
            save_flight_plans(flight_plans)
            st.success("✅ Flight Plan Deleted.")
            st.rerun()

        if "edit_fp_key" in st.session_state:
            st.subheader(f"Editing Flight Plan: {st.session_state['edit_fp_key']}")
            fp_edit = flight_plans[st.session_state["edit_fp_key"]]
            updated_fp = {}
            field_labels = {
                "7": "Aircraft Identification (Item 7)",
                "8": "Flight Rules (Item 8)",
                "8_type": "Type of Flight (Item 8)",
                "9": "Type of Aircraft (Item 9)",
                "9_wtc": "Wake Turbulence Category (Item 9)",
                "10": "Equipment (Item 10)",
                "10_ssr": "SSR Equipment (Item 10)",
                "13": "Aerodrome of Departure (Item 13)",
                "13_eobt": "EOBT (Item 13, HHMM)",
                "15_speed": "Cruising Speed (Item 15)",
                "15_level": "Level (Item 15)",
                "15_route": "Route (Item 15)",
                "16_dest": "Destination Aerodrome (Item 16)",
                "16_eet": "EET (Item 16, HHMM)",
                "16_alt1": "First Alternate Aerodrome (Item 16)",
                "16_alt2": "Second Alternate Aerodrome (Item 16)",
                "18": "Other Information (Item 18)",
                "19_endurance": "Endurance (Item 19, HHMM)",
                "19_pob": "Persons on Board (Item 19)",
                "19_color": "Aircraft Color/Markings (Item 19)",
                "19_pilot": "Pilot in Command (Item 19)"
            }

            for key in fp_edit:
                updated_fp[key] = st.text_input(f"{field_labels.get(key, key)}", fp_edit[key])

            if st.button("Save Changes"):
                new_key = updated_fp["7"]
                if new_key != st.session_state["edit_fp_key"]:
                    del flight_plans[st.session_state["edit_fp_key"]]
                flight_plans[new_key] = updated_fp
                save_flight_plans(flight_plans)
                st.success("✅ Changes Saved.")
                del st.session_state["edit_fp_key"]
                st.rerun()
    else:
        st.info("ℹ️ No flight plans saved yet.")

with tabs[2]:
    st.header("🛫 Generate ICAO Messages")
    if flight_plans:
        selected_fp = st.selectbox("Select Flight Plan for Message", list(flight_plans.keys()), key="msg")
        fp = flight_plans[selected_fp]
        msg_type = st.selectbox("Select Message Type", ["FPL", "DLA", "DEP", "ARR", "CNL", "CHG", "SVC", "ALR", "DET", "INC"])
        additional = ""
        if msg_type in ["DLA", "DEP", "ARR", "CHG", "SVC", "ALR", "DET", "INC"]:
            additional = st.text_input("Additional Info")

        if st.button("Generate Message 🛫"):
            if msg_type == "FPL":
                msg = f"(FPL-{fp['7']}-{fp['8']}{fp['8_type']} - {fp['9']}/{fp['9_wtc']}-{fp['10']}/{fp['10_ssr']} - {fp['13']}{fp['13_eobt']} - {fp['15_speed']}{fp['15_level']} {fp['15_route']} - {fp['16_dest']}{fp['16_eet']} {fp['16_alt1']} {fp['16_alt2']} - {fp['18']} - E/{fp['19_endurance']} - P/{fp['19_pob']} - AC/{fp['19_color']} - PIC/{fp['19_pilot']})"
            else:
                msg = f"{msg_type}-{fp['7']}-{fp['13']}-{fp['16_dest']}-{additional}".replace("--", "-").strip("-")
            outbox.append(msg)
            save_outbox(outbox)
            st.success(f"✅ Message Generated and Saved to Outbox: {msg}")
    else:
        st.info("ℹ️ Please create and save a flight plan first.")

with tabs[3]:
    st.header("📤 Outbox")
    if st.button("Clear Outbox 🗑️"):
        with open(outbox_file, "w") as f:
            json.dump([], f)
        st.success("✅ Outbox cleared.")
    sender_name = st.text_input("Sender Name:")
    message_originator = st.text_input("Message Originator:")
    lesson_number = st.text_input("Lesson Number:")
    if st.button("Export Outbox 📄"):
        with open(outbox_file, "r") as f:
            outbox_data = json.load(f)
        outbox_content = f"{sender_name}\n{message_originator}\n{lesson_number}\n\n"
        for message in outbox_data:
            outbox_content += message + "\n"
        with open("outbox_export.txt", "w") as f:
            f.write(outbox_content)
        st.success("✅ Outbox exported to outbox_export.txt")
    recipient_email = st.text_input("Recipient Email:")
    if st.button("Mail Outbox ✉️"):
        try:
            with open("outbox_export.txt", "r") as f:
                file_content = f.read()
            sender_email = "atsato1090@gmail.com"
            sender_password = "jcks ezmt rigp likb"
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = "ClearedDCT Exported Outbox"
            msg.attach(MIMEText(file_content, "plain"))
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            st.success("✅ Exported outbox emailed successfully.")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
    st.subheader("Current Outbox Content:")
    for msg in outbox:
        st.write(msg)

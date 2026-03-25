import streamlit as st
import heapq

# ---------- Patient Class ----------
class Patient:
    def __init__(self, pid, name, symptom, ptype, level=0):
        self.pid = pid
        self.name = name
        self.symptom = symptom
        self.ptype = ptype
        self.level = level

    def __str__(self):
        if self.ptype == "ฉุกเฉิน":
            return f"{self.name} (ฉุกเฉิน - ระดับ {self.level})"
        return f"{self.name} (ทั่วไป)"


# ---------- Queue System ----------
class HospitalQueue:
    def __init__(self):
        self.general = []
        self.emergency = []
        self.patients = {}
        self.counter = 1

    def add_patient(self, pid, name, symptom, ptype, level=0):
        patient = Patient(pid, name, symptom, ptype, level)
        self.patients[pid] = patient

        if ptype == "ฉุกเฉิน":
            heapq.heappush(self.emergency, (-level, self.counter, pid))
        else:
            self.general.append(pid)

        self.counter += 1

    def call_next(self):
        if self.emergency:
            _, _, pid = heapq.heappop(self.emergency)
        elif self.general:
            pid = self.general.pop(0)
        else:
            return None

        return self.patients.pop(pid)

    def delete(self, pid):
        if pid in self.patients:
            self.patients.pop(pid)

            if pid in self.general:
                self.general.remove(pid)

            self.emergency = [i for i in self.emergency if i[2] != pid]
            heapq.heapify(self.emergency)

    def reset(self):
        self.general = []
        self.emergency = []
        self.patients = {}
        self.counter = 1

    def show_all(self):
        return list(self.patients.values())

    def show_queue(self):
        result = []

        for lvl, _, pid in self.emergency:
            p = self.patients.get(pid)
            if p:
                result.append(f"🚨 {p.name} (ระดับ {-lvl})")

        for pid in self.general:
            p = self.patients.get(pid)
            if p:
                result.append(f"🙂 {p.name}")

        return result


# ---------- Streamlit ----------
st.set_page_config(page_title="Hospital Queue", page_icon="🏥")
st.title("🏥 Hospital Queue System")

if "hq" not in st.session_state:
    st.session_state.hq = HospitalQueue()

hq = st.session_state.hq


# ---------- Sidebar ----------
st.sidebar.header("➕ เพิ่มผู้ป่วย")

pid = st.sidebar.text_input("รหัสผู้ป่วย")
name = st.sidebar.text_input("ชื่อ")
symptom = st.sidebar.text_input("อาการ")

ptype = st.sidebar.selectbox("ประเภท", ["ทั่วไป", "ฉุกเฉิน"])

level = 0
if ptype == "ฉุกเฉิน":
    level = st.sidebar.slider("ระดับความรุนแรง", 1, 3)

if st.sidebar.button("เพิ่ม"):
    if pid and name:
        hq.add_patient(pid, name, symptom, ptype, level)
        st.success("เพิ่มเรียบร้อย")


st.sidebar.markdown("---")

del_pid = st.sidebar.text_input("ลบรหัสผู้ป่วย")
if st.sidebar.button("ลบ"):
    hq.delete(del_pid)
    st.warning("ลบแล้ว")


if st.sidebar.button("🔄 รีเซ็ตคิว"):
    hq.reset()
    st.error("รีเซ็ตแล้ว")


# ---------- Main ----------
st.header("📋 รายชื่อผู้ป่วย")

patients = hq.show_all()
if not patients:
    st.write("ไม่มีข้อมูล")
else:
    for p in patients:
        st.write(str(p))


st.markdown("---")

c1, c2 = st.columns(2)

# เรียกคิว
with c1:
    if st.button("📢 เรียกคิว"):
        patient = hq.call_next()
        if patient:
            if patient.ptype == "ฉุกเฉิน":
                st.success(f"กำลังเรียก: {patient.name} (ระดับ {patient.level})")
            else:
                st.success(f"กำลังเรียก: {patient.name}")
        else:
            st.warning("ไม่มีคิว")

# แสดงคิว
with c2:
    st.subheader("📌 คิวปัจจุบัน")
    queue = hq.show_queue()
    if not queue:
        st.write("ไม่มีคิว")
    else:
        for q in queue:
            st.write(q)

# จำนวน
st.markdown("---")
st.write(f"👥 จำนวนผู้ป่วย: {len(hq.patients)}")

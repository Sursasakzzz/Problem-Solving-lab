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
            return f"{self.name} (🚨 ระดับ {self.level})"
        return f"{self.name} ( ทั่วไป)"


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
                result.append(f" {p.name}")

        return result


# ---------- Streamlit ----------
st.set_page_config(page_title="Hospital Queue", page_icon="🏥")
st.title("🏥 Hospital Queue System")

# session fix (กันคิวหาย)
if "hq" not in st.session_state:
    st.session_state.hq = HospitalQueue()

hq = st.session_state.hq


# ---------- ฟอร์มเพิ่มผู้ป่วย ----------
st.subheader("➕ เพิ่มผู้ป่วย")

c1, c2 = st.columns(2)

with c1:
    pid = st.text_input("รหัสผู้ป่วย")
    name = st.text_input("ชื่อ")

with c2:
    symptom = st.text_input("อาการ")
    ptype = st.selectbox("ประเภท", ["ทั่วไป", "ฉุกเฉิน"])

level = 0
if ptype == "ฉุกเฉิน":
    level = st.slider("ระดับความรุนแรง", 1, 3)

if st.button("➕ เพิ่มผู้ป่วย"):
    if pid and name:
        hq.add_patient(pid, name, symptom, ptype, level)
        st.success("เพิ่มผู้ป่วยเรียบร้อย")

st.markdown("---")


# ---------- ปุ่มควบคุม ----------
c3, c4, c5 = st.columns(3)

with c3:
    if st.button("📢 เรียกคิว"):
        patient = hq.call_next()
        if patient:
            st.success(f"กำลังเรียก: {patient}")
        else:
            st.warning("ไม่มีคิว")

with c4:
    del_pid = st.text_input("ลบรหัสผู้ป่วย")
    if st.button("🗑️ ลบ"):
        hq.delete(del_pid)
        st.warning("ลบแล้ว")

with c5:
    if st.button("🔄 รีเซ็ต"):
        hq.reset()
        st.error("รีเซ็ตแล้ว")

st.markdown("---")


# ---------- แสดงผู้ป่วย (UI สวย) ----------
st.subheader("📋 รายชื่อผู้ป่วย")

patients = hq.show_all()

if not patients:
    st.info("ไม่มีข้อมูลผู้ป่วย")
else:
    for p in patients:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

            col1.markdown(f"**🆔 {p.pid}**")
            col2.markdown(f"**👤 {p.name}**")
            col3.markdown(f"🩺 {p.symptom}")

            if p.ptype == "ฉุกเฉิน":
                col4.error(f"🚨 ฉุกเฉิน (ระดับ {p.level})")
            else:
                col4.success(" ทั่วไป")

st.markdown("---")


# ---------- แสดงคิว ----------
c6, c7 = st.columns(2)

with c6:
    st.subheader("📌 คิวปัจจุบัน")
    queue = hq.show_queue()
    if not queue:
        st.write("ไม่มีคิว")
    else:
        for q in queue:
            st.write(q)

with c7:
    st.subheader("📊 สรุป")
    st.write(f"👥 จำนวนผู้ป่วยทั้งหมด: {len(hq.patients)}")
    st.write(f"🚨 ฉุกเฉิน: {len(hq.emergency)}")
    st.write(f" ทั่วไป: {len(hq.general)}")

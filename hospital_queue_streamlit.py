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

    def search(self, keyword):
        result = []
        for p in self.patients.values():
            if keyword.lower() in p.name.lower() or keyword in p.pid:
                result.append(p)
        return result

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


# ---------- INIT ----------
st.set_page_config(page_title="Hospital Queue", page_icon="🏥")

if "hq" not in st.session_state:
    st.session_state.hq = HospitalQueue()

if "page" not in st.session_state:
    st.session_state.page = "add"

hq = st.session_state.hq


# ---------- PAGE SWITCH ----------
def go_page(p):
    st.session_state.page = p


# ---------- PAGE 1: ADD ----------
if st.session_state.page == "add":
    st.title("🏥 เพิ่มผู้ป่วย")

    pid = st.text_input("รหัสผู้ป่วย")
    name = st.text_input("ชื่อ")
    symptom = st.text_input("อาการ")
    ptype = st.selectbox("ประเภท", ["ทั่วไป", "ฉุกเฉิน"])

    level = 0
    if ptype == "ฉุกเฉิน":
        level = st.slider("ระดับความรุนแรง", 1, 3)

    if st.button("➕ เพิ่ม"):
        if pid and name:
            hq.add_patient(pid, name, symptom, ptype, level)
            st.success("เพิ่มแล้ว")

    st.markdown("---")
    st.button("➡️ ไปหน้าจัดการคิว", on_click=go_page, args=("main",))


# ---------- PAGE 2: MAIN ----------
elif st.session_state.page == "main":
    st.title("📋 จัดการคิวผู้ป่วย")

    # 🔍 SEARCH
    keyword = st.text_input("🔍 ค้นหา (ชื่อหรือรหัส)")
    if keyword:
        results = hq.search(keyword)
    else:
        results = hq.show_all()

    st.subheader("📋 รายชื่อผู้ป่วย")

    if not results:
        st.info("ไม่พบข้อมูล")
    else:
        for p in results:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([1,2,2,2])
                c1.markdown(f"**{p.pid}**")
                c2.markdown(p.name)
                c3.markdown(p.symptom)

                if p.ptype == "ฉุกเฉิน":
                    c4.error(f"🚨 ระดับ {p.level}")
                else:
                    c4.success(" ปกติ")

    st.markdown("---")

    # ปุ่ม
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📢 เรียกคิว"):
            p = hq.call_next()
            if p:
                st.success(f"กำลังเรียก: {p}")
            else:
                st.warning("ไม่มีคิว")

    with c2:
        del_id = st.text_input("ลบรหัส")
        if st.button("🗑️ ลบ"):
            hq.delete(del_id)

    with c3:
        if st.button("🔄 รีเซ็ต"):
            hq.reset()

    st.markdown("---")

    # คิว
    st.subheader("📌 คิวปัจจุบัน")
    for q in hq.show_queue():
        st.write(q)

    st.markdown("---")
    st.button("⬅️ กลับหน้าเพิ่มผู้ป่วย", on_click=go_page, args=("add",))

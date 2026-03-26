import streamlit as st
import heapq


class Patient:
    def __init__(self, pid, name, symptom, ptype, level=0):
        self.pid = pid
        self.name = name
        self.symptom = symptom
        self.ptype = ptype
        self.level = level



class HospitalQueue:
    def __init__(self):
        self.general = []
        self.emergency = []
        self.patients = {}
        self.counter = 1

    def add_patient(self, pid, name, symptom, ptype, level=0):
        p = Patient(pid, name, symptom, ptype, level)
        self.patients[pid] = p

        if ptype == "ฉุกเฉิน":
            heapq.heappush(self.emergency, (-level, self.counter, pid))
        else:
            self.general.append(pid)

        self.counter += 1

    def update_patient(self, pid, name, symptom, ptype, level):
        if pid in self.patients:
            p = self.patients[pid]
            p.name = name
            p.symptom = symptom
            p.ptype = ptype
            p.level = level

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

    def search(self, keyword):
        return [
            p for p in self.patients.values()
            if keyword.lower() in p.name.lower() or keyword in p.pid
        ]

    def show_all(self):
        return list(self.patients.values())



st.set_page_config(page_title="Hospital Queue", page_icon="🏥")

if "hq" not in st.session_state:
    st.session_state.hq = HospitalQueue()

if "page" not in st.session_state:
    st.session_state.page = "add"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

hq = st.session_state.hq


def go_page(p):
    st.session_state.page = p


if st.session_state.page == "add":
    st.title("เพิ่มผู้ป่วย")

    pid = st.text_input("รหัสผู้ป่วย")
    name = st.text_input("ชื่อ")
    symptom = st.text_input("อาการ")
    ptype = st.selectbox("ประเภท", ["ทั่วไป", "ฉุกเฉิน"])

    level = 0
    if ptype == "ฉุกเฉิน":
        level = st.slider("ระดับความรุนแรง", 1, 3)

    if st.button("เพิ่มผู้ป่วย"):
        if pid and name:
            hq.add_patient(pid, name, symptom, ptype, level)
            st.success("เพิ่มเรียบร้อย")

    st.markdown("---")
    st.button("ไปหน้าจัดการคิว", on_click=go_page, args=("main",))



elif st.session_state.page == "main":
    st.title("จัดการคิวผู้ป่วย")

    keyword = st.text_input("ค้นหา")
    results = hq.search(keyword) if keyword else hq.show_all()

    st.subheader("รายชื่อผู้ป่วย")

    if not results:
        st.info("ไม่มีข้อมูล")
    else:
        for p in results:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([1,2,2,2,1])

                c1.write(f"รหัส: {p.pid}")
                c2.write(f"ชื่อ: {p.name}")
                c3.write(f"อาการ: {p.symptom}")

                if p.ptype == "ฉุกเฉิน":
                    c4.write(f"ฉุกเฉิน (ระดับ {p.level})")
                else:
                    c4.write("ทั่วไป")


                if c5.button("แก้ไข", key=p.pid):
                    st.session_state.edit_id = p.pid

    st.markdown("---")


    if st.session_state.edit_id:
        pid = st.session_state.edit_id
        p = hq.patients[pid]

        st.subheader("แก้ไขข้อมูลผู้ป่วย")

        new_name = st.text_input("ชื่อใหม่", p.name)
        new_symptom = st.text_input("อาการใหม่", p.symptom)
        new_type = st.selectbox("ประเภทใหม่", ["ทั่วไป", "ฉุกเฉิน"])

        new_level = p.level
        if new_type == "ฉุกเฉิน":
            new_level = st.slider("ระดับใหม่", 1, 3, p.level)

        if st.button("บันทึก"):
            hq.update_patient(pid, new_name, new_symptom, new_type, new_level)
            st.session_state.edit_id = None
            st.success("แก้ไขเรียบร้อย")

    st.markdown("---")


    c1, c2 = st.columns(2)

    with c1:
        if st.button("เรียกคิว"):
            p = hq.call_next()
            if p:
                st.success(f"กำลังเรียก: {p.name}")
            else:
                st.warning("ไม่มีคิว")

    with c2:
        del_id = st.text_input("ลบรหัสผู้ป่วย")
        if st.button("ลบ"):
            hq.delete(del_id)
            st.warning("ลบแล้ว")

    st.markdown("---")
    st.button("กลับหน้าเพิ่มผู้ป่วย", on_click=go_page, args=("add",))

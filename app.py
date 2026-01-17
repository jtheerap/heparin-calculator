import streamlit as st

def main():
    st.set_page_config(page_title="Heparin Calculator", page_icon="💉")

    st.title("💉 Heparin Adjustment Calculator")
    st.info("สำหรับคำนวณการปรับยา Heparin ตามค่า PTT (Nomogram)")

    # --- ส่วนที่ 1: ตั้งค่าเบื้องต้น (Setup) ---
    st.subheader("1. ข้อมูลการผสมยา (Concentration)")
    
    # เลือกความเข้มข้น (แก้ User Error ตรงนี้)
    conc_option = st.radio(
        "เลือกความเข้มข้นของยาที่ใช้ (Concentration):",
        (
            "Standard (100 units : 1 ml) [25,000u in 250ml]", 
            "Concentrate (500 units : 1 ml) [25,000u in 50ml]"
        )
    )
    
    # แปลงตัวเลือกเป็นตัวเลขเพื่อคำนวณ
    if "100" in conc_option:
        concentration = 100  # units/ml
    else:
        concentration = 500  # units/ml

    st.write(f"ℹ️ ความเข้มข้นที่ใช้คำนวณ: **{concentration} units/ml**")
    st.markdown("---")

    # --- ส่วนที่ 2: กรอกข้อมูลคนไข้ (Input) ---
    st.subheader("2. ข้อมูลคนไข้และค่า Lab")
    
    col1, col2 = st.columns(2)
    with col1:
        protocol_type = st.selectbox("เลือก Protocol", ["High Intensity (คิดตาม นน.)", "Standard/Low Intensity (Fix dose)"])
        current_rate_ml = st.number_input("Rate ปัจจุบันที่เครื่อง (ml/hr)", min_value=0.0, step=0.1, format="%.1f")
    
    with col2:
        weight = st.number_input("น้ำหนักคนไข้ (kg)", min_value=1.0, value=50.0, step=0.1)
        ptt_value = st.number_input("ค่า PTT ล่าสุด", min_value=0.0, step=1.0)

    # --- ส่วนที่ 3: Logic การคำนวณ (ปรับแก้ตัวเลข Protocol ตรงนี้ได้เลย) ---
    if st.button("🚀 คำนวณการปรับยา (Calculate)", type="primary"):
        
        advice_bolus = 0
        advice_rate_change_units = 0 # หน่วยเป็น units/hr หรือ units/kg/hr
        action_msg = ""
        color = "blue"

        # ==========================================
        # 🟢 ตัวอย่าง LOGIC (High Intensity)
        # ==========================================
        if "High" in protocol_type:
            # คำนวณ Dose ปัจจุบัน (units/kg/hr) เพื่อแสดงผล (Option)
            current_dose_units_hr = current_rate_ml * concentration
            
            if ptt_value < 35:
                # ตัวอย่าง: Bolus 80 u/kg, เพิ่ม Rate 4 u/kg/hr
                advice_bolus = 80 * weight
                advice_rate_change_units = 4 * weight 
                action_msg = "PTT ต่ำมาก (Sub-therapeutic)"
                color = "red"
                
            elif 35 <= ptt_value <= 49:
                # ตัวอย่าง: Bolus 40 u/kg, เพิ่ม Rate 2 u/kg/hr
                advice_bolus = 40 * weight
                advice_rate_change_units = 2 * weight
                action_msg = "PTT ค่อนข้างต่ำ"
                color = "orange"
                
            elif 50 <= ptt_value <= 70:
                # Target range
                action_msg = "✅ PTT อยู่ในเกณฑ์ (Therapeutic Goal)"
                color = "green"
                
            elif 71 <= ptt_value <= 90:
                # ตัวอย่าง: ลด Rate 2 u/kg/hr
                advice_rate_change_units = -2 * weight
                action_msg = "PTT เริ่มสูง"
                color = "orange"
                
            else: # > 90
                # ตัวอย่าง: หยุดยา 1 ชม. แล้วลด Rate 3 u/kg/hr
                advice_rate_change_units = -3 * weight
                action_msg = "🛑 PTT สูงเกินเกณฑ์! (Hold Infusion 60 min)"
                color = "red"

        # ==========================================
        # 🔵 ตัวอย่าง LOGIC (Standard / Low Intensity - Fix Dose)
        # ==========================================
        else:
            if ptt_value < 35:
                advice_bolus = 5000 # Fix unit
                advice_rate_change_units = 200 # Fix unit/hr (เช่น เพิ่ม 200 unit/hr)
                action_msg = "PTT ต่ำมาก"
                color = "red"
            # ... (ใส่ Logic ช่วงอื่นๆ ต่อตรงนี้) ...
            elif 35 <= ptt_value <= 70:
                 action_msg = "✅ Keep Rate เดิม"
                 color = "green"
            else:
                 advice_rate_change_units = -200
                 action_msg = "PTT สูง ลดระดับยา"
                 color = "orange"


        # --- ส่วนที่ 4: แปลงผลลัพธ์เป็น ml/hr ---
        
        # คำนวณ ml ที่ต้องปรับ
        change_ml_hr = advice_rate_change_units / concentration
        new_rate_ml = current_rate_ml + change_ml_hr
        
        # ป้องกัน Rate ติดลบ
        if new_rate_ml < 0: new_rate_ml = 0

        # --- ส่วนที่ 5: แสดงผลหน้าจอ ---
        st.markdown("---")
        if color == "red":
            st.error(f"### ผลการประเมิน: {action_msg}")
        elif color == "orange":
            st.warning(f"### ผลการประเมิน: {action_msg}")
        else:
            st.success(f"### ผลการประเมิน: {action_msg}")

        # แสดงกล่องผลลัพธ์ใหญ่ๆ
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.metric(label="💉 Bolus (ดึงยาจากขวด)", value=f"{int(advice_bolus):,} units", delta=f"{advice_bolus/concentration:.1f} ml")
            st.caption(f"(คิดเป็นปริมาตร **{advice_bolus/concentration:.1f} ml**)")
            
        with col_res2:
            st.metric(label="⚡ ปรับเครื่อง Infusion Pump เป็น", value=f"{new_rate_ml:.1f} ml/hr", delta=f"{change_ml_hr:+.1f} ml/hr")
            st.caption(f"(เดิม {current_rate_ml} -> ปรับ {'เพิ่ม' if change_ml_hr>0 else 'ลด'} {abs(change_ml_hr):.1f} ml/hr)")

if __name__ == "__main__":

    main()

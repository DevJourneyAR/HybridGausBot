import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# --- إعدادات واجهة التطبيق ---
st.set_page_config(page_title="Hybrid Gaus Bot", layout="wide")
st.title("🛡️ نظام التداول الإحصائي الذكي")
st.markdown("---")

# --- إدارة الأسرار (الأمان) ---
# يحاول الكود قراءة التوكن من إعدادات الموقع المشفرة
def get_config():
    token = st.sidebar.text_input("Telegram Token", type="password")
    chat_id = st.sidebar.text_input("Chat ID")
    return token, chat_id

# --- محرك توزيع غاوس (المنطق الرياضي) ---
def analyze_market(data):
    df = pd.DataFrame(data, columns=['price'])
    mean = df['price'].mean()
    std = df['price'].std()
    z_score = (df['price'].iloc[-1] - mean) / std if std != 0 else 0
    return z_score

# --- الشريط الجانبي ---
token, chat_id = get_config()
st.sidebar.info("تأكد من إدخال بيانات التلغرام لبدء استقبال التنبيهات.")

# --- لوحة التحكم ---
col1, col2 = st.columns([2, 1])

if st.button("🚀 تشغيل محرك المراقبة"):
    if not token or not chat_id:
        st.error("❌ خطأ: يرجى إدخال التوكن والـ Chat ID أولاً!")
    else:
        st.success("✅ البوت متصل الآن ويقوم بتحليل انحرافات الأسعار...")
        
        # إرسال رسالة ترحيب لتأكيد الربط
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": "✅ تم تشغيل تطبيق التداول بنجاح! جاري مراقبة السوق..."})

        # محاكاة حركة السعر (هنا نربط مع Hybrid لاحقاً)
        prices = [100.0]
        
        with col1:
            chart_placeholder = st.empty()
        with col2:
            metrics_placeholder = st.empty()

        for i in range(50):
            # توليد سعر عشوائي لمحاكاة التذبذب
            new_price = prices[-1] + np.random.normal(0, 1)
            prices.append(new_price)
            
            if len(prices) > 20:
                z = analyze_market(prices)
                
                # تحديث الرسم البياني
                chart_placeholder.line_chart(prices[-50:])
                
                # تحديث المؤشرات
                with metrics_placeholder.container():
                    st.metric("Z-Score (انحراف غاوس)", f"{z:.2f}")
                    if z < -2:
                        st.success("🟢 فرصة شراء محتملة!")
                    elif z > 2:
                        st.warning("🔴 فرصة جني أرباح!")

            time.sleep(1) # سرعة التحديث ثانية واحدة

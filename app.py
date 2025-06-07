import streamlit as st
import pandas as pd
import numpy as np
from persiantools.jdatetime import JalaliDate
import base64

st.set_page_config(page_title="دسته‌بندی مشتریان", layout="centered")

# استایل و تم
st.markdown("""
<style>
* {
    font-family: Tahoma, sans-serif !important;
}
html, body, [class*=\"css\"] {
    background-color: #3a3a3a;
    color: #ffffff;
}
.stButton > button {
    color: white !important;
    background-color: #2563eb !important;
}
.block-container {
    padding: 2rem;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# لوگو بالا
st.image("logo.png", width=100)

# تاریخ شمسی
today = JalaliDate.today()
st.markdown(f"تاریخ امروز: {today.strftime('%Y/%m/%d')}")

# خوش آمدگویی
if "شروع" not in st.session_state:
    st.session_state["شروع"] = False

if not st.session_state["شروع"]:
    st.markdown("""
    ## خوش آمدید به نرم‌افزار دسته‌بندی مشتریان

این نرم‌افزار بر پایه مدل استاندارد RFM طراحی شده است که سه شاخص کلیدی را در تحلیل مشتریان در نظر می‌گیرد:

- تازگی خرید (Recency)
- تعداد خرید (Frequency)
- مبلغ خرید (Monetary)

    این سامانه به شما کمک می‌کند تا مشتریان خود را بر اساس رفتار خرید و شاخص‌های کلیدی به گروه‌های مختلف دسته‌بندی کنید، از جمله:

    - مشتریان وفادار
    - مشتریان غیرفعال
    - مشتریان با ارزش بالا
    - مشتریان جدید
    - مشتریان پرریسک

    فایل اکسل شما باید شامل ستون‌های زیر باشد:
    - نام مشتری
    - تعداد خرید در ۳ ماه اخیر
    - مبلغ میانگین هر خرید
    - آخرین تاریخ خرید (مثلاً: 1402/11/25)
    - امتیاز وفاداری (بین ۰ تا ۱۰)

    برای دریافت فایل نمونه:
    """)

    with open("نمونه_داده_مشتری.xlsx", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="نمونه_داده_مشتری.xlsx" style="color:#93c5fd;">دانلود فایل نمونه اکسل</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown("توسعه‌یافته توسط شرکت <a href='https://inohub.ir' target='_blank'>اینوهاب</a>", unsafe_allow_html=True)
    if st.button("شروع تحلیل"):
        st.session_state["شروع"] = True
    st.stop()

st.title("دسته‌بندی مشتریان بر اساس شاخص‌های کلیدی")

uploaded_file = st.file_uploader("فایل اکسل مشتریان را بارگذاری کنید", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("فایل با موفقیت بارگذاری شد.")
    st.dataframe(df)

    today = JalaliDate.today().to_gregorian()

    def categorize_customer(row):
        try:
            last_purchase = pd.to_datetime(row['آخرین تاریخ خرید'], errors='coerce')
            recency_days = (today - last_purchase.date()).days if not pd.isna(last_purchase) else 999
        except:
            recency_days = 999
        frequency = row['تعداد خرید']
        amount = row['میانگین خرید']
        loyalty = row['امتیاز وفاداری']

        if recency_days <= 30 and frequency >= 3 and amount >= 1_000_000 and loyalty >= 8:
            return "مشتری وفادار و باارزش"
        elif recency_days > 180:
            return "مشتری غیرفعال"
        elif frequency <= 2 and recency_days <= 60:
            return "مشتری جدید"
        elif amount >= 2_000_000:
            return "مشتری پرخرج"
        elif loyalty <= 4:
            return "مشتری پرریسک"
        else:
            return "مشتری عادی"

    df["دسته‌بندی"] = df.apply(categorize_customer, axis=1)
    st.subheader("نتیجه دسته‌بندی مشتریان:")
    st.dataframe(df)

    st.subheader("تعداد مشتریان در هر گروه:")
    st.bar_chart(df["دسته‌بندی"].value_counts())

    st.markdown("---")
    st.markdown("تمام حقوق این نرم‌افزار متعلق به شرکت <a href='https://inohub.ir' target='_blank'>اینوهاب</a> است.", unsafe_allow_html=True)
    st.image("logo.png", width=100)

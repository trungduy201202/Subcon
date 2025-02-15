import streamlit as st
import plotly.express as px
import pandas as pd
import streamlit.components.v1 as components  # Sử dụng cho hiển thị HTML custom

st.set_page_config(page_title="Subcon Quality Tracking", layout="wide")

# Đọc dữ liệu từ 3 file CSV
df_upper = pd.read_csv("data/upper.csv")
df_upper["Category"] = "Upper"

df_bottom = pd.read_csv("data/bottom.csv")
df_bottom["Category"] = "Bottom"

df_osc = pd.read_csv("data/outsourcing.csv")
df_osc["Category"] = "OSC"

# Kết hợp dữ liệu từ cả 3 file
df_csv = pd.concat([df_upper, df_bottom, df_osc])

# Chuyển đổi cột ngày sang dạng datetime nếu cần
df_csv["Date"] = pd.to_datetime(df_csv["Date"])

# Sidebar Filters
st.sidebar.title("Filter Options")
st.sidebar.write("### Filter by Date")
start_date = st.sidebar.date_input("Start Date", min_value=df_csv["Date"].min(), value=df_csv["Date"].min())
end_date = st.sidebar.date_input("End Date", min_value=df_csv["Date"].min(), value=df_csv["Date"].max())

# Lọc dữ liệu theo khoảng ngày
filtered_data = df_csv[(df_csv["Date"] >= pd.to_datetime(start_date)) & (df_csv["Date"] <= pd.to_datetime(end_date))]

# Hiển thị 3 khung cho Upper, Bottom, OSC
st.title("Subcon Quality Tracking System")

categories = ["Upper", "Bottom", "OSC"]
cols = st.columns(3)
target_percent = 3  # Giả định target là 3%

# Từng loại production type
cols = st.columns([1, 2])  # Chia màn hình thành 2 cột không đều: 1 phần cho bảng số liệu, 2 phần cho biểu đồ

with cols[0]:  # Cột bên trái hiển thị bảng số liệu
    for i, category in enumerate(categories):
        input_qty = int(filtered_data[filtered_data["Category"] == category]["Input Qty"].sum())
        reject_qty = int(filtered_data[filtered_data["Category"] == category]["Reject Qty"].sum())
        reject_percent = round((reject_qty / input_qty) * 100, 2) if input_qty > 0 else 0
        
        st.markdown(f"""
            <div style='background-color: #f8f9fa; border: 1px solid #d1d8e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: center; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);'>
                <h5 style='color: #4b6584; font-size: 24px; margin-bottom: 10px; margin-left: 20px'>{category}</h5>
                <div style='display: flex; justify-content: space-around;'>
                    <div>
                        <strong style='font-size: 20px; color: #4b6584;'>{input_qty}</strong>
                        <br><span style='font-size: 13px; color: #7f8c8d;'>Input Qty</span>
                    </div>
                    <div>
                        <strong style='font-size: 20px; color: #4b6584;'>{reject_qty}</strong>
                        <br><span style='font-size: 13px; color: #7f8c8d;'>Reject Qty</span>
                    </div>
                    <div>
                        <strong style='font-size: 20px; color: red;'>{reject_percent:.2f}%</strong>
                        <br><span style='font-size: 13px; color: #7f8c8d;'>% Reject</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with cols[1]:  # Cột bên phải hiển thị biểu đồ
    chart_data = filtered_data.groupby("Category").agg({
        "Input Qty": "sum",
        "Reject Qty": "sum"
    }).reset_index()

    chart_data["% Reject"] = round((chart_data["Reject Qty"] / chart_data["Input Qty"]) * 100, 2)

    fig = px.bar(
        chart_data, 
        x="Category", 
        y="% Reject", 
        color="Category", 
        labels={"% Reject": "% Reject Rate"}, 
        title="Reject % by Production Type",
        text="% Reject",  # Thêm text vào từng cột
        category_orders={"Category": ["Upper", "Bottom", "OSC"]}  # Giữ thứ tự cố định
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",  # Hiển thị số với 2 chữ số thập phân
        textposition="inside"  # Hiển thị số liệu bên trong cột
    )

    fig.update_layout(
        title={
            "text": "Reject % by Production Type",
            "y": 0.95,  # Vị trí theo trục y (0.0 là đáy, 1.0 là đỉnh)
            "x": 0.48,   # Căn giữa theo trục x
            "xanchor": "center",
            "yanchor": "top"
        },
        uniformtext_minsize=10, 
        uniformtext_mode="hide"
    )

    st.plotly_chart(fig, use_container_width=True)




# Detail Supplier













# all_categories_content = """
# <style>
#     * {
#         font-family: 'Source Sans Pro', sans-serif;
#     }
#     h4 {
#         font-weight: bold;
#     }
#     p {
#         margin: 5px 0;
#     }
# </style>
# """

# all_categories_content += "<div style='display: flex;'>"

# for category in categories:
#     suppliers = df_csv[df_csv["Category"] == category]["Supplier"].unique()
    
#     # Khung lớn cho từng category
#     html_content = f"""
#     <div style='flex-basis: 30%; max-width: 30%; min-width: auto; border: 2px solid #ccc; border-radius: 15px; padding: 15px; margin: 10px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);'>
#         <h4 style='text-align: center; color: #4b6584; margin-bottom: 15px; font-size: 25px;'>{category.upper()}</h4>
#         <div style='display: flex; flex-wrap: wrap; justify-content: space-around; gap: 10px;'>
#     """
    
#     for supplier in suppliers:
#         supplier_data = df_csv[(df_csv["Category"] == category) & (df_csv["Supplier"] == supplier)]
#         input_qty = supplier_data["Input Qty"].sum()
#         reject_qty = supplier_data["Reject Qty"].sum()
#         actual = round((reject_qty / input_qty) * 100, 2) if input_qty > 0 else 0
#         color_background = "#006600" if actual <= 3 else "#CC0000"
        
#         # Card nhỏ
#         html_content += f"""
#         <div style='flex-basis: 100px; max-width: auto; height: auto; padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 10px; text-align: center; background-color: {color_background};'>
#             <h4 style='margin: 0; font-size: 14px; color: white;'>{supplier}</h4>
#             <p style='margin: 5px 0; font-size: 11px; font-weight: bold; color: white'>Target: 3%</p>
#             <p style='margin: 5px 0; font-size: 11px; font-weight: bold; color: white'>Actual: {actual}%</p>
#         </div>
#         """
    
#     html_content += "</div></div>"
#     all_categories_content += html_content

# all_categories_content += "</div>"

# # Hiển thị tất cả các khung lớn bên trong một flexbox
# components.html(all_categories_content, height=1000, scrolling=True)
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Danh sách các loại sản xuất với file CSV chung
production_type_files = {
    "Upper": "data/upper.csv",
    "Bottom": "data/bottom.csv",
    "Outsourcing": "data/outsourcing.csv"
}

# Sidebar - Bộ lọc
st.sidebar.header("🔍 Filter Options")

# Chọn loại sản xuất
selected_category = st.sidebar.selectbox("🛠 Select Production Type", ["Select a Category"] + list(production_type_files.keys()), index=0, key="category")

if selected_category == "Select a Category":
    st.warning("Please select a production type to view data.")
    st.stop()

# Đọc dữ liệu từ file CSV chung của Production Type
file_path = production_type_files[selected_category]

try:
    # Đọc dữ liệu từ file CSV
    df_csv = pd.read_csv(file_path, encoding="utf-8")

    # Chuẩn hóa dữ liệu
    df_csv.fillna(0, inplace=True)
    df_csv.columns = df_csv.columns.str.strip()

    # Chuyển đổi kiểu dữ liệu số
    numeric_columns = ["YEAR", "WEEK", "MONTH", "RANDOM INSPECTION QTY", "REJECT QTY"]
    for col in numeric_columns:
        df_csv[col] = pd.to_numeric(df_csv[col], errors='coerce').fillna(0).astype(int)

    # Xác định cột defect (bỏ qua các cột thông tin chung)
    exclude_columns = ["SUBCON", "YEAR", "WEEK", "MONTH", "DATE", "MODEL", "PGSC", "PO",
                       "INPUT QTY", "RANDOM INSPECTION QTY", "PASS QTY", "REJECT QTY", "% REJECT", "RESULT", "REMARK"]
    defect_columns = [col for col in df_csv.columns if col not in exclude_columns]


    # Xác định danh sách SUBCON từ dữ liệu
    subcon_list = sorted(df_csv["SUBCON"].unique())
    selected_subcon = st.sidebar.selectbox("🏭 Select Subcon", ["All"] + subcon_list, index=0, key="subcon")

    # Nếu chưa chọn Subcon thì dừng chương trình
    if selected_subcon == "All":
        st.warning("Please select a Subcon to continue.")
        st.stop()

    # Bộ lọc Năm
    year_options = sorted(df_csv["YEAR"].unique())
    selected_year = st.sidebar.selectbox("📅 Select Year", ["All"] + [str(y) for y in year_options], key="year")
    
    # Nếu chưa chọn Year thì dừng chương trình
    if selected_year == "All":
        st.warning("Please select a Year to continue.")
        st.stop()


    # Bộ lọc Tuần
    week_options = sorted(df_csv["WEEK"].unique())
    selected_week = st.sidebar.selectbox("📅 Select Week", ["All"] + [str(w) for w in week_options], key="week")

    # Lọc dữ liệu theo các bộ lọc đã chọn
    df_filtered = df_csv.copy()

    if selected_subcon != "All":
        df_filtered = df_filtered[df_filtered["SUBCON"] == selected_subcon]

    if selected_year != "All":
        df_filtered = df_filtered[df_filtered["YEAR"] == int(selected_year)]

    if selected_week != "All":
        df_filtered = df_filtered[df_filtered["WEEK"] == int(selected_week)]

    # Hiển thị tiêu đề
    st.markdown(f"<h1 style='text-align: center;'>📌 {selected_category} - Subcon Tracking</h1>", unsafe_allow_html=True)

    # --- 1️⃣ Monthly Defect Trend ---
    st.subheader("1️⃣ Monthly Defect Trend")

    # Lọc dữ liệu theo Production Type, Subcon và Year
    df_filtered = df_csv[df_csv["YEAR"] == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_filtered = df_filtered[df_filtered["SUBCON"] == selected_subcon]

    # Tính tổng số lượng kiểm tra & reject theo tháng
    df_monthly = df_filtered.groupby("MONTH").agg({
        "REJECT QTY": "sum",
        "RANDOM INSPECTION QTY": "sum"
    }).reset_index()

    # Tính tỷ lệ lỗi (REJECT QTY / RANDOM INSPECTION QTY) * 100
    df_monthly["Defect Rate (%)"] = (df_monthly["REJECT QTY"] / df_monthly["RANDOM INSPECTION QTY"]) * 100

    # Xử lý lỗi chia cho 0 (nếu RANDOM INSPECTION QTY = 0, gán 0%)
    df_monthly["Defect Rate (%)"] = df_monthly["Defect Rate (%)"].fillna(0)

    # Làm tròn số liệu và chuyển thành dạng chuỗi có ký hiệu `%`
    df_monthly["Defect Rate (%)"] = df_monthly["Defect Rate (%)"].round(2)  # Làm tròn đến 2 chữ số thập phân
    df_monthly["Defect Rate Text"] = df_monthly["Defect Rate (%)"].astype(str) + "%"  # Thêm ký hiệu %

    # Vẽ biểu đồ
    fig_monthly = px.bar(
        df_monthly, 
        x="MONTH", 
        y="Defect Rate (%)", 
        text="Defect Rate Text",  # Hiển thị phần trăm trực tiếp trên cột
        color_discrete_sequence=["#1f77b4"],  # Màu cố định cho tất cả các cột
        title=f"Monthly Defect Rate ({selected_subcon})"
    )

    # Cập nhật trục y để hiển thị %
    fig_monthly.update_yaxes(title_text="Defect Rate (%)")

    # Chỉnh hover tooltip
    fig_monthly.update_traces(
        hovertemplate="<b>Month: %{x}</b><br>Defect Rate: %{y:.2f}%<extra></extra>"
    )

    fig_monthly.update_xaxes(
        title_text="MONTH",
        tickmode="linear",  # Hiển thị tất cả các giá trị số
        tickvals=list(range(1, 13)),  # Đảm bảo hiện từ tháng 1 đến tháng 12
        tickformat="d",  # Định dạng số nguyên
        tickangle=0  # Giữ thẳng hàng dễ đọc
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

    # --- 2️⃣ Weekly Defect Trend ---
    st.subheader("2️⃣ Weekly Defect Trend")

    # Lọc dữ liệu theo Production Type, Subcon, và Year
    df_filtered = df_csv[df_csv["YEAR"] == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_filtered = df_filtered[df_filtered["SUBCON"] == selected_subcon]

    # Tính tổng số lượng kiểm tra & reject theo tuần
    df_weekly = df_filtered.groupby("WEEK").agg({
        "REJECT QTY": "sum",
        "RANDOM INSPECTION QTY": "sum"
    }).reset_index()

    # Tính toán Defect Rate (%) cho từng tuần
    df_weekly["Defect Rate (%)"] = (df_weekly["REJECT QTY"] / df_weekly["RANDOM INSPECTION QTY"]) * 100
    df_weekly["Defect Rate (%)"] = df_weekly["Defect Rate (%)"].fillna(0).round(2)
    df_weekly["Defect Rate Text"] = df_weekly["Defect Rate (%)"].astype(str) + "%"

    # Nếu chọn "All" tuần → vẽ Line Chart
    if selected_week == "All":
        fig_weekly = px.line(
            df_weekly, x="WEEK", y="Defect Rate (%)",
            markers=True, title=f"Weekly Defect Trend ({selected_subcon})"
        )
        fig_weekly.update_traces(
            hovertemplate="<b>Week: %{x}</b><br>Defect Rate: %{y:.2f}%<extra></extra>"
        )
    else:
        # Lọc dữ liệu chỉ cho tuần đã chọn
        df_week_selected = df_weekly[df_weekly["WEEK"] == int(selected_week)]

        # Vẽ Bar Chart cho tuần được chọn
        fig_weekly = px.bar(
            df_week_selected, x="WEEK", y="Defect Rate (%)",
            text="Defect Rate Text", 
            title=f"Defect Rate for Week {selected_week} ({selected_subcon})"
        )

        # **Chỉ hiển thị đúng số tuần đã chọn**
        fig_weekly.update_xaxes(
            tickmode="array",
            tickvals=[int(selected_week)],  # Chỉ hiển thị đúng tuần đã chọn
            ticktext=[f"{selected_week}"]
        )

        fig_weekly.update_traces(
            hovertemplate="<b>Week: %{x}</b><br>Defect Rate: %{y:.2f}%<extra></extra>"
        )

    # Cập nhật trục y hiển thị %
    fig_weekly.update_yaxes(title_text="Defect Rate (%)")

    st.plotly_chart(fig_weekly, use_container_width=True)

    # --- 3️⃣ Biểu đồ Top 3 Model có defect cao nhất ---
    st.subheader("3️⃣ Top 3 Defective Models")

    # Lọc dữ liệu theo Production Type, Subcon, và Year
    df_top_models = df_csv[df_csv["YEAR"] == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_top_models = df_top_models[df_top_models["SUBCON"] == selected_subcon]

    # Nếu chọn tuần cụ thể, lọc theo tuần
    if selected_week != "All":
        df_top_models = df_top_models[df_top_models["WEEK"] == int(selected_week)]

    # Tính tỷ lệ defect cho từng model
    df_top_models = df_top_models.groupby("MODEL").agg({
        "REJECT QTY": "sum",
        "RANDOM INSPECTION QTY": "sum"
    }).reset_index()

    # Tính toán defect rate (%)
    df_top_models["Defect Rate (%)"] = (df_top_models["REJECT QTY"] / df_top_models["RANDOM INSPECTION QTY"]) * 100
    df_top_models["Defect Rate (%)"] = df_top_models["Defect Rate (%)"].fillna(0).round(2)
    df_top_models["Defect Rate Text"] = df_top_models["Defect Rate (%)"].astype(str) + "%"

    # Chọn Top 3 Model có defect rate cao nhất
    df_top_models = df_top_models.sort_values("Defect Rate (%)", ascending=False).head(3)

    # Kiểm tra nếu có dữ liệu hay không
    if df_top_models.empty:
        st.warning("⚠️ Không có dữ liệu defect cho Model trong bộ lọc này.")
    else:
        # Vẽ biểu đồ
        fig_models = px.bar(
            df_top_models, 
            x="MODEL", 
            y="Defect Rate (%)", 
            text="Defect Rate Text", 
            color="MODEL",
            title=f"Top 3 Models with Highest Defect Rate ({selected_subcon} - {'Week ' + selected_week if selected_week != 'All' else 'All Weeks'})"
        )

        # Cập nhật trục y để hiển thị %
        fig_models.update_yaxes(title_text="Defect Rate (%)")

        # Chỉnh hover tooltip
        fig_models.update_traces(
            hovertemplate="<b>Model: %{x}</b><br>Defect Rate: %{y:.2f}%<extra></extra>"
        )

        st.plotly_chart(fig_models, use_container_width=True)


    # --- 4️⃣ Biểu đồ Pareto Chart - Defect Analysis ---
    st.subheader("4️⃣ Pareto Chart - Defect Analysis")

    # Lọc dữ liệu theo Year
    df_defect = df_csv[df_csv["YEAR"] == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_defect = df_defect[df_defect["SUBCON"] == selected_subcon]

    # Nếu chọn tuần cụ thể, lọc theo tuần
    if selected_week != "All":
        df_defect = df_defect[df_defect["WEEK"] == int(selected_week)]

    # Tổng hợp số lượng của từng defect type
    df_defect_types = df_defect[defect_columns].sum().reset_index()
    df_defect_types.columns = ["Defect Type", "Defect Count"]

    # Đảm bảo kiểu dữ liệu số
    df_defect_types["Defect Count"] = pd.to_numeric(df_defect_types["Defect Count"], errors='coerce').fillna(0).astype(int)

    # Sắp xếp lỗi theo số lượng từ cao đến thấp
    df_defect_types = df_defect_types[df_defect_types["Defect Count"] > 0].sort_values("Defect Count", ascending=False)

    # Kiểm tra nếu không có defect nào
    if df_defect_types.empty:
        st.warning("⚠️ Không có dữ liệu defect nào cho bộ lọc này.")
    else:
        # Đảm bảo cột "Defect Type" là chuỗi
        df_defect_types["Defect Type"] = df_defect_types["Defect Type"].astype(str)

        # Tính toán tỷ lệ lũy kế (Cumulative %)
        df_defect_types["Cumulative %"] = df_defect_types["Defect Count"].cumsum() / float(df_defect_types["Defect Count"].sum()) * 100

        # Vẽ biểu đồ Pareto
        fig_pareto = go.Figure()

        # Cột Defect Count (trục y bên trái)
        fig_pareto.add_trace(go.Bar(
            x=df_defect_types["Defect Type"], 
            y=df_defect_types["Defect Count"], 
            name="Defect Count",
            marker=dict(color="royalblue"),
            hovertemplate="<b>Defect Type: %{x}</b><br>Defect Count: %{y}<extra></extra>"
        ))

        # Đường Cumulative % (trục y bên phải)
        fig_pareto.add_trace(go.Scatter(
            x=df_defect_types["Defect Type"], 
            y=df_defect_types["Cumulative %"],
            mode="lines+markers",
            name="Cumulative Percentage",
            yaxis="y2",
            hovertemplate="<b>Defect Type: %{x}</b><br>Cumulative %: %{y:.2f}%<extra></extra>"
        ))

        # Cấu hình trục
        fig_pareto.update_layout(
            title=f"Pareto Chart - Defect Types ({selected_subcon} - {'Week ' + selected_week if selected_week != 'All' else 'All Weeks'})",
            xaxis=dict(title="Defect Type"),
            yaxis=dict(title="Defect Count", side="left"),
            yaxis2=dict(
                title="Cumulative Percentage (%)",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(x=1.1, y=1),
        )

        st.plotly_chart(fig_pareto, use_container_width=True)


    # --- 5️⃣ Biểu đồ Pie Chart - Defect Distribution by Defect Type ---
    st.subheader("5️⃣ Defect Distribution by Defect Type")

    # Lọc dữ liệu theo năm
    df_defect = df_csv[df_csv["YEAR"] == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_defect = df_defect[df_defect["SUBCON"] == selected_subcon]

    # Nếu chọn tuần cụ thể, lọc theo tuần
    if selected_week != "All":
        df_defect = df_defect[df_defect["WEEK"] == int(selected_week)]

    # Tổng hợp số lượng của từng defect type
    df_defect_types = df_defect[defect_columns].sum().reset_index()
    df_defect_types.columns = ["Defect Type", "Defect Count"]

    # Kiểm tra nếu không có defect nào
    if df_defect_types["Defect Count"].sum() == 0:
        st.warning("⚠️ Không có dữ liệu defect nào cho bộ lọc này.")
    else:
        # Tính tổng số lượng lỗi
        total_defects = df_defect_types["Defect Count"].sum()

        # Tính tỷ lệ % lỗi
        df_defect_types["Defect Percentage"] = (df_defect_types["Defect Count"] / total_defects) * 100

        # Xử lý lỗi chia cho 0 (nếu không có lỗi nào, đặt giá trị 0)
        df_defect_types["Defect Percentage"] = df_defect_types["Defect Percentage"].fillna(0)

        # Loại bỏ các lỗi có tỷ lệ 0%
        df_defect_types = df_defect_types[df_defect_types["Defect Percentage"] > 0]

        # Làm tròn số liệu
        df_defect_types["Defect Percentage"] = df_defect_types["Defect Percentage"].round(2)

        # Vẽ biểu đồ Pie Chart
        fig_pie = px.pie(
            df_defect_types, 
            names="Defect Type", 
            values="Defect Percentage",
            title=f"Defect Distribution for Subcon: {selected_subcon}",
            hole=0.3,  # Tạo dạng Doughnut Chart
        )

        # Cập nhật tooltip
        fig_pie.update_traces(
            hovertemplate="<b>Defect Type: %{label}</b><br>Defect Count: %{value:.2f}%<extra></extra>"
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6️⃣ Biểu đồ Heatmap Defect Distribution by Model ---
    st.subheader("6️⃣ Defect Distribution Heatmap by Model")

    # Lọc dữ liệu theo năm
    df_heatmap = df_csv[df_csv["YEAR"].astype(int) == int(selected_year)]

    # Nếu subcon không phải "All", lọc theo subcon cụ thể
    if selected_subcon != "All":
        df_heatmap = df_heatmap[df_heatmap["SUBCON"] == selected_subcon]

    # Nếu chọn tuần cụ thể, lọc theo tuần
    if selected_week != "All":
        df_heatmap = df_heatmap[df_heatmap["WEEK"].astype(int) == int(selected_week)]

    # Kiểm tra nếu không có dữ liệu
    if df_heatmap.empty or len(defect_columns) == 0:
        st.warning("⚠️ Không có dữ liệu defect nào cho bộ lọc này.")
    else:
        # Chuyển đổi tất cả các cột defect về dạng số
        df_heatmap[defect_columns] = df_heatmap[defect_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

        # Đảm bảo MODEL luôn là chuỗi
        df_heatmap["MODEL"] = df_heatmap["MODEL"].astype(str)

        # Tổng số lỗi của từng Model theo loại lỗi
        df_defect_counts = df_heatmap.groupby("MODEL")[defect_columns].sum().reset_index()

        # Tổng số lượng kiểm của từng Model
        df_total_inspection = df_heatmap.groupby("MODEL")["RANDOM INSPECTION QTY"].sum().reset_index()

        # Chuyển đổi dữ liệu về dạng số để tránh lỗi chia cho chuỗi
        df_total_inspection["RANDOM INSPECTION QTY"] = df_total_inspection["RANDOM INSPECTION QTY"].astype(float)

        # Chuyển đổi dữ liệu sang dạng cột để vẽ heatmap
        df_heatmap_melted = df_defect_counts.melt(id_vars=["MODEL"], var_name="Defect Type", value_name="Defect Count")

        # **🛠️ Khắc phục lỗi `MODEL` đã tồn tại khi `merge`**
        df_total_inspection = df_total_inspection.rename(columns={"MODEL": "MODEL_TEMP"})  # Đổi tên cột tạm thời
        df_heatmap_melted = df_heatmap_melted.merge(df_total_inspection, left_on="MODEL", right_on="MODEL_TEMP", how="left")
        df_heatmap_melted.drop(columns=["MODEL_TEMP"], inplace=True)  # Xóa cột tạm

        # Chuyển đổi tất cả các giá trị sang số
        df_heatmap_melted["Defect Count"] = df_heatmap_melted["Defect Count"].astype(float)
        df_heatmap_melted["RANDOM INSPECTION QTY"] = df_heatmap_melted["RANDOM INSPECTION QTY"].astype(float)

        # Kiểm tra nếu RANDOM INSPECTION QTY = 0 thì đặt tỷ lệ lỗi = 0
        df_heatmap_melted["Defect Rate (%)"] = df_heatmap_melted.apply(
            lambda row: (row["Defect Count"] / row["RANDOM INSPECTION QTY"]) * 100 if row["RANDOM INSPECTION QTY"] > 0 else 0,
            axis=1
        ).round(2)

        # Loại bỏ các lỗi có giá trị 0 để không hiển thị trên heatmap
        df_heatmap_melted = df_heatmap_melted[df_heatmap_melted["Defect Rate (%)"] > 0]

        if df_heatmap_melted.empty:
            st.warning("⚠️ Không có dữ liệu đủ lớn để hiển thị heatmap.")
        else:
            # Vẽ Heatmap với màu đỏ cam, điều chỉnh kích thước rộng hơn
            fig_heatmap = px.imshow(
                df_heatmap_melted.pivot(index="Defect Type", columns="MODEL", values="Defect Rate (%)"),
                labels=dict(x="Model", y="Defect Type", color="Defect Rate (%)"),
                title=f"Defect Distribution Heatmap by Model ({selected_subcon})",
                color_continuous_scale="Oranges",
                width=1400,  # Tăng chiều rộng
                height=900   # Tăng chiều cao
            )

            # Cập nhật tooltip để hiển thị chính xác số liệu
            fig_heatmap.update_traces(
                hovertemplate="<b>Model: %{x}</b><br>Defect Type: %{y}<br>Defect Rate: %{z:.2f}%<extra></extra>"
            )

            # Điều chỉnh font chữ để dễ đọc hơn
            fig_heatmap.update_layout(
                xaxis=dict(tickangle=45, title_font=dict(size=14), tickfont=dict(size=12)),  # Xoay label model, tăng font
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),  # Tăng font của defect type
                margin=dict(l=100, r=100, t=80, b=100)  # Giữ khoảng cách để không bị cắt
            )

            st.plotly_chart(fig_heatmap, use_container_width=False)  # Tắt "use_container_width" để giữ kích thước cố định

except FileNotFoundError:
    st.error(f"⚠️ Không tìm thấy dữ liệu của {selected_subcon}!")
except Exception as e:
    st.error(f"⚠️ Lỗi hệ thống! {e}")

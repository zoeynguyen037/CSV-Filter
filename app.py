import streamlit as st
import pandas as pd
import io

# ─────────────────────────────────────────────
# PRESETS — thêm usecase mới vào đây
# ─────────────────────────────────────────────
PRESETS = {
    "#acked (LinkedIn)": [
        "profile_url",
        "full_name",
        "first_name",
        "headline",
        "location_name",
        "industry",
        "summary",
        "current_company",
        "current_company_position",
        "organization_url_1",
        "organization_2",
        "organization_url_2",
        "organization_title_2",
        "organization_location_2",
        "organization_3",
        "organization_url_3",
        "organization_title_3",
        "organization_location_3",
    ],
    # Thêm usecase mới ở đây, ví dụ:
    # "Apollo Outreach": ["First Name", "Last Name", "Email", "Company", "Title"],
}

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="CSV Column Filter", page_icon="✂️", layout="centered")

st.title("✂️ CSV Column Filter")
st.caption("Upload file CSV, chọn preset hoặc tự chọn cột, rồi export.")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded_file:
    # Đọc file — thử separator ";" trước, fallback về ","
    try:
        df = pd.read_csv(uploaded_file, sep=";")
        if df.shape[1] == 1:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=",")
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=",")

    all_columns = list(df.columns)

    st.success(f"Đọc xong: **{len(df)} dòng**, **{len(all_columns)} cột**")

    st.divider()

    # Chọn preset
    preset_options = list(PRESETS.keys()) + ["Custom (tự chọn)"]
    selected_preset = st.selectbox("Chọn preset:", preset_options)

    if selected_preset == "Custom (tự chọn)":
        selected_columns = st.multiselect(
            "Chọn cột muốn giữ lại:",
            options=all_columns,
        )
    else:
        preset_cols = PRESETS[selected_preset]
        # Chỉ giữ những cột có thật trong file (tránh lỗi nếu file thiếu cột)
        valid_cols = [c for c in preset_cols if c in all_columns]
        missing_cols = [c for c in preset_cols if c not in all_columns]

        if missing_cols:
            st.warning(f"Những cột sau không có trong file: `{', '.join(missing_cols)}`")

        selected_columns = valid_cols
        st.info(f"Sẽ giữ lại **{len(selected_columns)} cột** theo preset **{selected_preset}**")

    st.divider()

    if selected_columns:
        df_filtered = df[selected_columns]

        st.subheader("Preview (5 dòng đầu)")
        st.dataframe(df_filtered.head(5), use_container_width=True)

        # Export
        output = io.StringIO()
        df_filtered.to_csv(output, index=False)
        csv_bytes = output.getvalue().encode("utf-8")

        original_name = uploaded_file.name.replace(".csv", "")
        export_name = f"{original_name}_filtered.csv"

        st.download_button(
            label=f"⬇️ Tải file ({len(df_filtered)} dòng × {len(selected_columns)} cột)",
            data=csv_bytes,
            file_name=export_name,
            mime="text/csv",
        )
    else:
        st.warning("Chưa chọn cột nào.")

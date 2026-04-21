"""
pages/6_settings.py — Upload sales data / manual entry
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dummy_data

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_File/style.css", "CSS_File/settings.css"):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>Upload Data</h1>
<p class='page-header-sub'>Import sales data to power your AI recommendations</p>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# ── Left Column: Upload + Manual Entry ───────────────────────────────────────
with col_left:

    # File Upload
    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">Upload Sales File</div>
        <div class="upload-dropzone">
            <div class="upload-dropzone-icon">📁</div>
            <div class="upload-dropzone-title">Drop file here or click to upload</div>
            <div class="upload-dropzone-sub">AI auto-detects columns and cleans messy data</div>
            <div class="upload-format-tags">
                <span class="upload-format-tag">Excel .xlsx</span>
                <span class="upload-format-tag">CSV</span>
                <span class="upload-format-tag">WhatsApp export</span>
                <span class="upload-format-tag">PDF invoice</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload sales file",
        type=["xlsx", "csv", "pdf", "txt"],
        label_visibility="collapsed",
    )
    if uploaded:
        st.success(f"✓ **{uploaded.name}** uploaded — AI is processing your data…")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # Manual Entry
    st.markdown("""
    <div class="settings-card" style="margin-top:0;">
        <div class="settings-card-title">Manual Entry</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("manual_entry", clear_on_submit=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            product_name = st.text_input("Product name", placeholder="e.g. Nasi Lemak")
        with r1c2:
            units_sold = st.number_input("Units sold", min_value=0, value=0)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            sell_price = st.number_input("Selling price (RM)", min_value=0.0, value=0.0, step=0.10)
        with r2c2:
            cost_price = st.number_input("Cost to make (RM)", min_value=0.0, value=0.0, step=0.10)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            units_wasted = st.number_input("Units wasted", min_value=0, value=0)
        with r3c2:
            entry_date = st.date_input("Date")

        submitted = st.form_submit_button(
            "Add Entry & Train AI", use_container_width=True, type="primary"
        )
        if submitted and product_name:
            st.success(f"✓ Entry for **{product_name}** saved — AI model updated.")

# ── Right Column: AI Process + Data Status ────────────────────────────────────
with col_right:

    # How AI processes data
    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">How AI Processes Your Data</div>
        <div class="ai-process-grid">
            <div class="ai-process-step">
                <div class="ai-process-icon">🔍</div>
                <div class="ai-process-title">Parse &amp; detect</div>
                <div class="ai-process-desc">Reads any format, handles Malaysian date formats</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">🧹</div>
                <div class="ai-process-title">Clean data</div>
                <div class="ai-process-desc">Removes duplicates, corrects typos</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">🧠</div>
                <div class="ai-process-title">Find patterns</div>
                <div class="ai-process-desc">Detects demand trends and seasonal shifts</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">💡</div>
                <div class="ai-process-title">Generate recs</div>
                <div class="ai-process-desc">Creates actionable RM-estimated advice</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current data status
    status = dummy_data.data_status
    rows_html = "".join(
        f"""<div class="data-status-row">
                <span class="data-status-label">{label}</span>
                <span class="data-status-value{'  good' if 'confidence' in label.lower() else ''}">{value}</span>
            </div>"""
        for label, value in status.items()
    )

    st.markdown(f"""
    <div class="settings-card">
        <div class="settings-card-title">Current Data Status</div>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)

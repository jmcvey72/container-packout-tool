import streamlit as st
import pandas as pd

# ---------------------
# Basic Setup
# ---------------------
st.set_page_config(page_title="Container Packout Optimizer", layout="wide")
st.title("📦 VP Racing - Container Packout Optimizer")

st.markdown("""
Upload your product shipment list (CSV) with the following columns:

- SKU  
- Length_in  
- Width_in  
- Height_in  
- Weight_lb  
- Qty  
- IsFuel (`Yes` or `No`)  
- Stackable (`Yes` or `No`)  
""")

# ---------------------
# Upload CSV File
# ---------------------
uploaded_file = st.file_uploader("Upload your product CSV file", type=["csv"])

# ---------------------
# Container Dimensions
# ---------------------
container_options = {
    "20ft Standard": {"length": 233, "width": 92, "height": 94, "max_weight": 48000},  # inches, lbs
    "40ft Standard": {"length": 472, "width": 92, "height": 94, "max_weight": 59500},
    "40ft High Cube": {"length": 472, "width": 92, "height": 105, "max_weight": 59500},
}

container_type = st.selectbox("Select container type", list(container_options.keys()))
container = container_options[container_type]

# Calculate container volume in cubic inches
container_volume = container["length"] * container["width"] * container["height"]

# ---------------------
# Process CSV
# ---------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean and calculate volume
    df["Volume_in3"] = df["Length_in"] * df["Width_in"] * df["Height_in"]
    df["Total_Volume"] = df["Volume_in3"] * df["Qty"]
    df["IsFuel"] = df["IsFuel"].str.lower().eq("yes")
    df["Stackable"] = df["Stackable"].str.lower().eq("yes")

    # Sort by volume descending (largest items first)
    df = df.sort_values(by="Volume_in3", ascending=False)

    # Running totals
    total_volume = df["Total_Volume"].sum()
    total_weight = (df["Weight_lb"] * df["Qty"]).sum()

    # Estimate containers
    estimated_containers_by_volume = total_volume / container_volume
    estimated_containers_by_weight = total_weight / container["max_weight"]
    estimated_containers = max(estimated_containers_by_volume, estimated_containers_by_weight)
    rounded_up = int(estimated_containers) + (1 if estimated_containers % 1 > 0 else 0)

    # ---------------------
    # Results
    # ---------------------
    st.subheader("📊 Packing Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Shipment Volume", f"{total_volume:,.0f} in³")
        st.metric("Container Volume", f"{container_volume:,.0f} in³")

    with col2:
        st.metric("Total Shipment Weight", f"{total_weight:,.0f} lbs")
        st.metric("Max Weight per Container", f"{container['max_weight']:,} lbs")

    st.markdown(f"### 🧠 Estimated Containers Needed: `{rounded_up}`")

    # Show table
    st.markdown("### 📦 Product Breakdown")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

else:
    st.info("👆 Upload a CSV to begin.")


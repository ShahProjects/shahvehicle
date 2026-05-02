import streamlit as st
import pandas as pd

data = pd.read_csv("cars_bikes.csv")

st.set_page_config(page_title="Vehicle Hub", layout="wide")

st.title("SHAH Vehicle Hub (Pro Version)")

# ---------------- CSS ----------------
st.markdown("""
<style>
.card-title {
    font-size: 18px;
    font-weight: 600;
}
.price {
    font-size: 22px;
    font-weight: bold;
    color: #ff4b4b;
}
.badge {
    padding: 4px 8px;
    border-radius: 8px;
    background-color: #f0f2f6;
    font-size: 12px;
    margin-right: 5px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "selected_vehicle" not in st.session_state:
    st.session_state.selected_vehicle = None

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "compare_list" not in st.session_state:
    st.session_state.compare_list = []

# ---------------- DETAIL PAGE ----------------
if st.session_state.selected_vehicle:

    v = st.session_state.selected_vehicle

    if st.button("⬅ Back"):
        st.session_state.selected_vehicle = None
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.image(v["image"], use_container_width=True)

    with col2:
        st.subheader(v["name"])
        st.write("💰 Price:", f"PKR {v['price']:,}")
        st.write("🏢 Company:", v["company"])
        st.write("⚙ Engine:", v["engine"])
        st.write("⛽ Mileage:", v["mileage"])

        if st.button("⭐ Add to Favorites"):
            st.session_state.favorites.append(v)

        if st.button("⚖ Add to Compare"):
            if v["name"] not in [x["name"] for x in st.session_state.compare_list]:
                if len(st.session_state.compare_list) < 3:
                    st.session_state.compare_list.append(v)
                    st.success("Added to compare")
                else:
                    st.warning("Max 3 vehicles")
            else:
                st.info("Already added")

# ---------------- MAIN PAGE ----------------
else:

    st.sidebar.header("🔎 Filters")

    search = st.sidebar.text_input("Search")
    type_filter = st.sidebar.selectbox("Type", ["All", "car", "bike"])

    min_p, max_p = int(data["price"].min()), int(data["price"].max())
    price_range = st.sidebar.slider("Price", min_p, max_p, (min_p, max_p))

    # FILTER
    filtered = data.copy()

    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]

    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]

    filtered = filtered[
        (filtered["price"] >= price_range[0]) &
        (filtered["price"] <= price_range[1])
    ]

    # PAGINATION
    page_size = 9
    total_pages = max(1, (len(filtered) // page_size) + 1)

    page = st.number_input("Page", 1, total_pages, 1)

    start = (page - 1) * page_size
    end = start + page_size

    page_data = filtered.iloc[start:end]

    # ---------------- GRID ----------------
    cols = st.columns(3)

    for i, (idx, row) in enumerate(page_data.iterrows()):
        col = cols[i % 3]

        with col:
            img = row["image"] if pd.notna(row["image"]) else "images/default.jpg"

            with st.container(border=True):

                st.image(img, use_container_width=True)

                st.markdown(f"<div class='card-title'>{row['name']}</div>", unsafe_allow_html=True)

                st.markdown(f"""
                <span class='badge'>{row['company']}</span>
                <span class='badge'>{row['engine']}</span>
                <span class='badge'>{row['mileage']} km/l</span>
                """, unsafe_allow_html=True)

                st.markdown(f"<div class='price'>PKR {row['price']:,}</div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("👁 View", key=f"v_{idx}"):
                        st.session_state.selected_vehicle = row.to_dict()
                        st.rerun()

                with c2:
                    if st.button("⚖ Compare", key=f"c_{idx}"):

                        if row["name"] not in [v["name"] for v in st.session_state.compare_list]:

                            if len(st.session_state.compare_list) < 3:
                                st.session_state.compare_list.append(row.to_dict())
                                st.success("Added to compare")
                            else:
                                st.warning("Only 3 vehicles allowed")
                        else:
                            st.info("Already added")

    # ---------------- COMPARE SECTION (OUTSIDE LOOP) ----------------
    if st.session_state.compare_list:
        st.markdown("## ⚖ Compare Vehicles")

        compare_df = pd.DataFrame(st.session_state.compare_list)

        st.dataframe(
            compare_df[["name", "price", "company", "engine", "mileage"]],
            use_container_width=True
        )

        if st.button("Clear Compare"):
            st.session_state.compare_list = []
            st.rerun()

    # ---------------- FAVORITES ----------------
    if st.session_state.favorites:
        st.markdown("## ⭐ Favorites")

        fav_df = pd.DataFrame(st.session_state.favorites)
        st.dataframe(fav_df[["name", "price", "company"]])
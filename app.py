# ==============================================================
# 🎨 Interactive Poster Generator (Streamlit version)
# Original Colab code adapted for web deployment — no logic changes
# ==============================================================

import random, math, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import pandas as pd
import streamlit as st

# ---------------------------
# Blob shape function
# ---------------------------
def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii  = r * (1 + wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y


# ---------------------------
# Palette handling
# ---------------------------
PALETTE_FILE = "palette.csv"

# Initialize palette.csv if not exists
if not os.path.exists(PALETTE_FILE):
    df_init = pd.DataFrame([
        {"name":"sky", "r":0.4, "g":0.7, "b":1.0},
        {"name":"sun", "r":1.0, "g":0.8, "b":0.2},
        {"name":"forest", "r":0.2, "g":0.6, "b":0.3}
    ])
    df_init.to_csv(PALETTE_FILE, index=False)

def read_palette():
    return pd.read_csv(PALETTE_FILE)

def add_color(name, r, g, b):
    df = read_palette()
    df = pd.concat([df, pd.DataFrame([{"name":name,"r":r,"g":g,"b":b}])], ignore_index=True)
    df.to_csv(PALETTE_FILE, index=False)
    print(f"Added {name}")

def update_color(name, r=None, g=None, b=None):
    df = read_palette()
    if name in df["name"].values:
        idx = df.index[df["name"]==name][0]
        if r is not None: df.at[idx,"r"] = r
        if g is not None: df.at[idx,"g"] = g
        if b is not None: df.at[idx,"b"] = b
        df.to_csv(PALETTE_FILE, index=False)
        print(f"Updated {name}")
    else:
        print(f"{name} not found")

def delete_color(name):
    df = read_palette()
    df = df[df["name"]!=name]
    df.to_csv(PALETTE_FILE, index=False)
    print(f"Deleted {name}")

def load_csv_palette():
    df = read_palette()
    return [(row.r, row.g, row.b) for row in df.itertuples()]

palette_csv = load_csv_palette()

# ---------------------------
# Show palette preview
# ---------------------------
def show_palette(palette):
    fig, ax = plt.subplots(figsize=(6,2))
    for i, c in enumerate(palette):
        ax.fill_between([i, i+1], 0, 1, color=c)
        ax.text(i+0.5, -0.1, f"{i+1}", ha="center", va="top")
    ax.axis("off")
    st.pyplot(fig)


# ---------------------------
# Palette generation modes
# ---------------------------
def make_palette(k=6, mode="pastel", base_h=0.60):
    cols = []
    if mode == "csv":
        return load_csv_palette()

    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0);  v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h;         s = random.uniform(0.2,0.6);   v = random.uniform(0.5,1.0)
        else: # random
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols


# ---------------------------
# Poster drawing function
# ---------------------------
def draw_poster(n_layers=8, wobble=0.15, palette_mode="pastel", seed=0):
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    ax.set_facecolor((0.97,0.97,0.97))

    palette = make_palette(6, mode=palette_mode)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx,cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode}",
            transform=ax.transAxes, fontsize=12, weight="bold")
    st.pyplot(fig)


# ---------------------------
# Streamlit App UI
# ---------------------------
st.title("🎨 Interactive Poster Generator")

st.sidebar.header("Poster Settings")
n_layers = st.sidebar.slider("Layers", 3, 20, 8)
wobble = st.sidebar.slider("Wobble", 0.01, 9.0, 0.15)
palette_mode = st.sidebar.selectbox("Palette Mode", ["pastel","vivid","mono","random","csv"])
seed = st.sidebar.slider("Seed", 0, 9999, 0)

if st.button("Generate Poster"):
    draw_poster(n_layers=n_layers, wobble=wobble, palette_mode=palette_mode, seed=seed)

st.sidebar.header("Current Palette (CSV)")
if st.sidebar.button("Show Palette Preview"):
    show_palette(palette_csv)
# ==============================================================
# 🎨 Palette Manager (CSV CRUD)
# ==============================================================

st.sidebar.header("🎨 Palette Manager")

# --- READ ---
if st.sidebar.checkbox("Show Current Palette Data"):
    st.write("### Current Palette Data")
    df_palette = read_palette()
    st.dataframe(df_palette)

# --- CREATE ---
st.write("### ➕ Add New Color")
new_name = st.text_input("Color Name")
col1, col2, col3 = st.columns(3)
with col1:
    r_new = st.number_input("R (0-1)", 0.0, 1.0, 0.5, 0.01)
with col2:
    g_new = st.number_input("G (0-1)", 0.0, 1.0, 0.5, 0.01)
with col3:
    b_new = st.number_input("B (0-1)", 0.0, 1.0, 0.5, 0.01)

if st.button("Add Color to Palette"):
    if new_name.strip():
        add_color(new_name.strip(), r_new, g_new, b_new)
        st.success(f"✅ Added '{new_name}' to palette.")
    else:
        st.warning("Please enter a valid color name.")

# --- UPDATE ---
st.write("### ✏️ Update Existing Color")
df = read_palette()
if len(df) > 0:
    color_to_update = st.selectbox("Select color to update", df["name"].tolist())
    col1, col2, col3 = st.columns(3)
    with col1:
        r_upd = st.number_input("New R (0-1)", 0.0, 1.0, float(df[df["name"]==color_to_update]["r"].iloc[0]), 0.01)
    with col2:
        g_upd = st.number_input("New G (0-1)", 0.0, 1.0, float(df[df["name"]==color_to_update]["g"].iloc[0]), 0.01)
    with col3:
        b_upd = st.number_input("New B (0-1)", 0.0, 1.0, float(df[df["name"]==color_to_update]["b"].iloc[0]), 0.01)

    if st.button("Update Color"):
        update_color(color_to_update, r_upd, g_upd, b_upd)
        st.success(f"✅ Updated '{color_to_update}' successfully!")

# --- DELETE ---
st.write("### ❌ Delete a Color")
if len(df) > 0:
    color_to_delete = st.selectbox("Select color to delete", df["name"].tolist(), key="delete_color")
    if st.button("Delete Selected Color"):
        delete_color(color_to_delete)
        st.error(f"🗑️ Deleted '{color_to_delete}' from palette.")


st.caption("Built from original Colab notebook — powered by Streamlit 🎈")

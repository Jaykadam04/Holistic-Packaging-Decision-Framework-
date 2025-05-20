import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load data
df = pd.read_csv("packaging_types.csv")

# Normalize helper
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

# Score calculator
def calculate_scores(cost_w, durability_w, env_w, reuse_w):
    df_norm = df.copy()
    df_norm['Cost_Norm'] = normalize(-df['Cost'])
    df_norm['Durability_Norm'] = normalize(df['Durability'])
    df_norm['Environmental_Impact_Norm'] = normalize(-df['Environmental_Impact'])
    df_norm['Reusability_Norm'] = normalize(df['Reusability'])

    df_norm['Score'] = (df_norm['Cost_Norm'] * cost_w +
                        df_norm['Durability_Norm'] * durability_w +
                        df_norm['Environmental_Impact_Norm'] * env_w +
                        df_norm['Reusability_Norm'] * reuse_w)
    return df_norm.sort_values(by='Score', ascending=False)

# Chart functions
def plot_horizontal_bar(df_sorted):
    top_df = df_sorted.head(7)
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.barh(top_df['Packaging_Type'], top_df['Score'], color='green')
    ax.set_xlabel('Score')
    ax.set_title('Top Packaging Recommendations')
    ax.invert_yaxis()
    return fig

def plot_stacked_chart(df_sorted):
    top_df = df_sorted.head(7)
    fig, ax = plt.subplots(figsize=(16, 7))
    bottom = [0]*len(top_df)
    labels = ['Cost_Norm', 'Durability_Norm', 'Environmental_Impact_Norm', 'Reusability_Norm']
    colors = ['#f77', '#7cf', '#8f8', '#fc8']

    for i, label in enumerate(labels):
        ax.bar(top_df['Packaging_Type'], top_df[label], bottom=bottom, label=label, color=colors[i])
        bottom = [x + y for x, y in zip(bottom, top_df[label])]

    ax.set_title("Stacked Comparison of Parameters")
    ax.set_ylabel("Normalized Contribution")
    ax.legend()
    return fig

def plot_bubble_chart(df_sorted):
    top_df = df_sorted.head(10)
    fig, ax = plt.subplots(figsize=(16, 7))
    sizes = top_df['Reusability'] * 1000
    scatter = ax.scatter(top_df['Environmental_Impact'], top_df['Cost'], s=sizes,
                         alpha=0.6, c=top_df['Score'], cmap='viridis')
    ax.set_title("Bubble Chart (Cost vs Environmental Impact)")
    ax.set_xlabel("Environmental Impact (Lower is Better)")
    ax.set_ylabel("Cost (Lower is Better)")
    for i, txt in enumerate(top_df['Packaging_Type']):
        ax.annotate(txt, (top_df['Environmental_Impact'].iloc[i], top_df['Cost'].iloc[i]), fontsize=8)
    fig.colorbar(scatter, label="Score")
    return fig

def plot_line_chart(df_sorted):
    top_df = df_sorted.head(10)
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(top_df['Packaging_Type'], top_df['Cost_Norm'], marker='o', label="Cost")
    ax.plot(top_df['Packaging_Type'], top_df['Durability_Norm'], marker='s', label="Durability")
    ax.plot(top_df['Packaging_Type'], top_df['Environmental_Impact_Norm'], marker='^', label="Environmental Impact")
    ax.plot(top_df['Packaging_Type'], top_df['Reusability_Norm'], marker='x', label="Reusability")
    ax.set_title("Line Chart of Normalized Parameters")
    ax.set_ylabel("Normalized Value")
    ax.legend()
    return fig

# Global variable to keep track of current chart
current_chart_type = 'bar'

# Chart Updater
def update_chart(chart_type=None):
    global current_chart_type
    if chart_type:
        current_chart_type = chart_type

    cost = cost_scale.get()
    durability = durability_scale.get()
    env = env_scale.get()
    reuse = reuse_scale.get()

    df_sorted = calculate_scores(cost, durability, env, reuse)

    for widget in chart_frame.winfo_children():
        widget.destroy()

    if current_chart_type == 'bar':
        fig = plot_horizontal_bar(df_sorted)
    elif current_chart_type == 'stacked':
        fig = plot_stacked_chart(df_sorted)
    elif current_chart_type == 'bubble':
        fig = plot_bubble_chart(df_sorted)
    elif current_chart_type == 'line':
        fig = plot_line_chart(df_sorted)
    else:
        return

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

# Info Popups
def show_info():
    messagebox.showinfo("About Parameters", """
1. 💰 Cost: Packaging cost. Lower is better.
2. 💪 Durability: Strength to protect contents. Higher is better.
3. 🌍 Environmental Impact: Harm to environment. Lower is better.
4. 🔁 Reusability: Can it be reused again? Higher is better.
All are normalized between 0 and 1 to compare fairly.
    """)

def show_formula():
    messagebox.showinfo("Score Formula", """
SCORE = (Normalized Cost × Weight1)
      + (Normalized Durability × Weight2)
      + (Normalized Environmental Impact × Weight3)
      + (Normalized Reusability × Weight4)

Note:
- Cost & Environmental Impact are negated before normalization because lower is better.
- All values are scaled to [0,1] range using Min-Max normalization.
    """)

# Table
def show_table():
    cost = cost_scale.get()
    durability = durability_scale.get()
    env = env_scale.get()
    reuse = reuse_scale.get()
    df_scored = calculate_scores(cost, durability, env, reuse)

    table_win = tk.Toplevel(root)
    table_win.title("📋 Normalized Values & Scores")
    table_win.geometry("1200x400")

    table = ttk.Treeview(table_win, columns=list(df_scored.columns), show='headings')
    for col in df_scored.columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor='center')
    for _, row in df_scored.iterrows():
        table.insert('', 'end', values=list(row))
    table.pack(expand=True, fill='both')

# GUI Setup
root = tk.Tk()
root.title("📦 Smart Packaging Recommender System")
root.geometry("1200x850")
root.config(bg="#f2f2f2")

# Title
ttk.Label(root, text="Smart Packaging Type Recommender", font=("Helvetica", 18, "bold"), background="#f2f2f2").pack(pady=10)

# Sliders Frame
sliders_frame = tk.Frame(root, bg="#f2f2f2")
sliders_frame.pack(pady=10)

# def create_slider(label, row):
#     ttk.Label(sliders_frame, text=label, font=("Helvetica", 12), background="#f2f2f2").grid(row=row, column=0, sticky="w", padx=10)
#     scale = tk.Scale(sliders_frame, from_=0.0, to=1.0, resolution=0.1,
#                      orient=tk.HORIZONTAL, length=300, command=lambda x: update_chart())
#     scale.set(0.25)
#     scale.grid(row=row, column=1, padx=10)
#     return scale
def create_slider(label, row):
    # Label styling
    ttk.Label(sliders_frame, text=label, font=("Segoe UI", 12, "bold"), background="#f2f2f2", foreground="#333333") \
        .grid(row=row, column=0, sticky="w", padx=12, pady=8)

    # Scale widget with modern look
    scale = tk.Scale(sliders_frame,
                     from_=0.0, to=1.0, resolution=0.1,
                     orient=tk.HORIZONTAL, length=320,
                     sliderlength=18, width=12,
                     troughcolor="#d0e9c6", bg="#f2f2f2",
                     fg="#333333", highlightthickness=0,
                     activebackground="#4caf50", command=lambda x: update_chart())

    scale.set(0.25)
    scale.grid(row=row, column=1, padx=10, pady=5)

    return scale


cost_scale = create_slider("💰 Cost (Low is Good)", 0)
durability_scale = create_slider("💪 Durability", 1)
env_scale = create_slider("🌍 Environmental Impact (Low is Good)", 2)
reuse_scale = create_slider("🔁 Reusability", 3)

# Buttons Frame
btn_frame = tk.Frame(root, bg="#f2f2f2")
btn_frame.pack(pady=10)

buttons = [
    ("📊 Bar Chart", 'bar'),
    ("🧱 Stacked Chart", 'stacked'),
    ("🫧 Bubble Chart", 'bubble'),
    ("📈 Line Chart", 'line')
]

for idx, (text, chart_type) in enumerate(buttons):
    ttk.Button(btn_frame, text=text, command=lambda ct=chart_type: update_chart(ct)).grid(row=0, column=idx, padx=5)

ttk.Button(btn_frame, text="ℹ️ Info", command=show_info).grid(row=0, column=4, padx=5)
ttk.Button(btn_frame, text="📐 Formula", command=show_formula).grid(row=0, column=5, padx=5)
ttk.Button(btn_frame, text="📋 Show Table", command=show_table).grid(row=0, column=6, padx=5)

# Chart Frame
chart_frame = tk.Frame(root)
chart_frame.pack(pady=20, fill=tk.BOTH, expand=True)

# Start App
update_chart('bar')
root.mainloop()

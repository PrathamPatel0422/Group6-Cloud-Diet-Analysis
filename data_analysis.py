import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------
# Settings / Paths
# ----------------------------
DATA_PATH = os.path.join("data", "All_Diets.csv")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== Cloud-Native Nutritional Insights: Dataset Analysis ===")

# ----------------------------
# 1) Load dataset
# ----------------------------
df = pd.read_csv(DATA_PATH)
print(f"\nLoaded dataset: {DATA_PATH}")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# ----------------------------
# 2) Data cleaning: fill missing numeric values with mean
# ----------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
missing_before = df[numeric_cols].isna().sum().sum()

for col in numeric_cols:
    if df[col].isna().any():
        df[col] = df[col].fillna(df[col].mean())

missing_after = df[numeric_cols].isna().sum().sum()
print(f"\nMissing numeric values before: {missing_before}")
print(f"Missing numeric values after : {missing_after}")

# ----------------------------
# Helper: safely detect column names
# ----------------------------
def pick_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

diet_col = pick_col(["Diet_type", "Diet Type", "diet_type", "diet"])
recipe_col = pick_col(["Recipe_name", "Recipe Name", "recipe_name", "Recipe"])
cuisine_col = pick_col(["Cuisine_type", "Cuisine Type", "cuisine_type", "Cuisine"])

protein_col = pick_col(["Protein(g)", "Protein", "protein"])
carbs_col = pick_col(["Carbs(g)", "Carbs", "carbs", "Carbohydrates(g)", "Carbohydrates"])
fat_col = pick_col(["Fat(g)", "Fat", "fat"])

required = [diet_col, recipe_col, cuisine_col, protein_col, carbs_col, fat_col]
if any(x is None for x in required):
    print("\nERROR: Could not detect one or more required columns.")
    print("Detected columns:", df.columns.tolist())
    raise SystemExit(1)

print("\nDetected columns:")
print(f" Diet type  : {diet_col}")
print(f" Recipe name: {recipe_col}")
print(f" Cuisine    : {cuisine_col}")
print(f" Protein    : {protein_col}")
print(f" Carbs      : {carbs_col}")
print(f" Fat        : {fat_col}")

# ----------------------------
# 3) Average macros per diet type
# ----------------------------
avg_macros = (
    df.groupby(diet_col)[[protein_col, carbs_col, fat_col]]
      .mean()
      .sort_values(by=protein_col, ascending=False)
)

print("\n=== Average Macros per Diet Type ===")
print(avg_macros.round(2))

# ----------------------------
# 4) Top 5 protein-rich recipes per diet type
# ----------------------------
print("\n=== Top 5 Protein Recipes per Diet Type ===")
top5_by_diet = (
    df.sort_values(by=protein_col, ascending=False)
      .groupby(diet_col)
      .head(5)[[diet_col, recipe_col, cuisine_col, protein_col, carbs_col, fat_col]]
)

for diet, block in top5_by_diet.groupby(diet_col):
    print(f"\n--- {diet} ---")
    print(block[[recipe_col, cuisine_col, protein_col, carbs_col, fat_col]].to_string(index=False))

# ----------------------------
# 5) Diet type with highest average protein
# ----------------------------
highest_protein_diet = avg_macros[protein_col].idxmax()
highest_protein_value = avg_macros.loc[highest_protein_diet, protein_col]
print("\n=== Diet Type with Highest Average Protein ===")
print(f"{highest_protein_diet} (avg protein = {highest_protein_value:.2f})")

# ----------------------------
# 6) Most common cuisines per diet type
# ----------------------------
print("\n=== Most Common Cuisines per Diet Type ===")
common_cuisines = (
    df.groupby([diet_col, cuisine_col])
      .size()
      .reset_index(name="count")
      .sort_values(["count"], ascending=False)
)

top_cuisine_per_diet = common_cuisines.groupby(diet_col).head(3)
for diet, block in top_cuisine_per_diet.groupby(diet_col):
    print(f"\n--- {diet} ---")
    print(block[[cuisine_col, "count"]].to_string(index=False))

# ----------------------------
# 7) New metrics (ratios)
# ----------------------------
safe_carbs = df[carbs_col].replace(0, pd.NA)
safe_fat = df[fat_col].replace(0, pd.NA)

df["Protein_to_Carbs_ratio"] = df[protein_col] / safe_carbs
df["Carbs_to_Fat_ratio"] = df[carbs_col] / safe_fat

print("\n=== New Metrics Created ===")
print(df[["Protein_to_Carbs_ratio", "Carbs_to_Fat_ratio"]].describe().round(2))

# ----------------------------
# 8) Visualizations (save to output/)
# ----------------------------

# Bar chart: average macros per diet
plt.figure()
avg_macros_plot = avg_macros.reset_index().melt(
    id_vars=diet_col,
    value_vars=[protein_col, carbs_col, fat_col],
    var_name="Macro",
    value_name="Average"
)
sns.barplot(data=avg_macros_plot, x=diet_col, y="Average", hue="Macro")
plt.title("Average Macros per Diet Type")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
bar_path = os.path.join(OUTPUT_DIR, "avg_macros_per_diet.png")
plt.savefig(bar_path)
plt.close()
print(f"\nSaved chart: {bar_path}")

# Heatmap: average macros by diet
plt.figure()
sns.heatmap(avg_macros, annot=True, fmt=".2f", cmap="viridis")
plt.title("Heatmap: Average Macros by Diet Type")
plt.tight_layout()
heatmap_path = os.path.join(OUTPUT_DIR, "macro_heatmap.png")
plt.savefig(heatmap_path)
plt.close()
print(f"Saved chart: {heatmap_path}")

# Scatter/strip plot: top 5 protein recipes across cuisines
plt.figure()
scatter_df = top5_by_diet.copy()
scatter_df["_Cuisine"] = scatter_df[cuisine_col].astype(str)
sns.stripplot(data=scatter_df, x="_Cuisine", y=protein_col, hue=diet_col, dodge=True)
plt.title("Top Protein Recipes Across Cuisines (Top 5 per Diet)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
scatter_path = os.path.join(OUTPUT_DIR, "top_protein_recipes_scatter.png")
plt.savefig(scatter_path)
plt.close()
print(f"Saved chart: {scatter_path}")

print("\n=== DONE ===")
print("Outputs saved in:", os.path.abspath(OUTPUT_DIR))

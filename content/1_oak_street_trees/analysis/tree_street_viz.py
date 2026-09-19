"""A playful chart of Syracuse trees whose names match their addresses.

Run: python tree_street_viz.py
Requires: pip install pandas plotly
"""

from pathlib import Path
import re

import pandas as pd
import plotly.graph_objects as go


HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / "Syracuse_Tree_Data_7832308158023752279.csv")

# This first-pass rule uses the name before the comma. It does not resolve
# aliases such as "Basswood / Linden" or differently ordered common names.
df["tree_name"] = (
    df["SPP_COM"].fillna("").str.split(",").str[0].str.strip().str.lower()
)
streets = df["STREET"].fillna("").str.lower()

df["substring_match"] = [
    bool(tree) and tree in street
    for tree, street in zip(df["tree_name"], streets)
]
df["whole_word_match"] = [
    bool(tree) and bool(re.search(r"\b" + re.escape(tree) + r"\b", street))
    for tree, street in zip(df["tree_name"], streets)
]


def summarize(match_column):
    selected = df.loc[df[match_column]]
    counts = selected.groupby("STREET").size().sort_values()
    details = []
    for street in counts.index:
        species = selected.loc[selected["STREET"].eq(street), "SPP_COM"]
        details.append("<br>".join(
            f"{name}: {count}" for name, count in species.value_counts().items()
        ))
    return counts, details


strict, strict_details = summarize("whole_word_match")
loose, loose_details = summarize("substring_match")

strict_title = (
    "Trees that understood the assignment"
    f"<br><sup>{strict.sum()} trees whose common name is a whole word in their street name</sup>"
)
loose_title = (
    "Close enough. We’ll allow it."
    f"<br><sup>{loose.sum()} trees when Oakwood, Maplehurst, and friends also count</sup>"
)

fig = go.Figure(go.Bar(
    x=strict.values,
    y=strict.index,
    orientation="h",
    marker_color="#20745B",
    text=strict.values,
    textposition="outside",
    cliponaxis=False,
    customdata=strict_details,
    hovertemplate="<b>%{y}</b><br>%{x} matching trees<br><br>%{customdata}<extra></extra>",
))

fig.update_layout(
    title=dict(text=strict_title, x=0.03, font_size=24),
    template="plotly_white",
    height=560,
    margin=dict(l=130, r=55, t=150, b=100),
    font=dict(family="Arial, sans-serif", size=14, color="#223A30"),
    paper_bgcolor="#FAF8F1",
    plot_bgcolor="#FAF8F1",
    xaxis=dict(title="Matching trees (count)", rangemode="tozero", dtick=1,
               range=[0, int(strict.max()) * 1.2], fixedrange=True),
    yaxis=dict(title=None, automargin=True, fixedrange=True),
    bargap=0.35,
    updatemenus=[dict(
        type="buttons", direction="right", x=0, y=1.19, xanchor="left",
        buttons=[
            dict(label="Understood the assignment", method="update", args=[
                dict(x=[strict.values.tolist()], y=[strict.index.tolist()],
                     text=[strict.values.tolist()], customdata=[strict_details]),
                dict(title=dict(text=strict_title, x=0.03), height=560,
                     **{"xaxis.range": [0, int(strict.max()) * 1.2]}),
            ]),
            dict(label="Close enough", method="update", args=[
                dict(x=[loose.values.tolist()], y=[loose.index.tolist()],
                     text=[loose.values.tolist()], customdata=[loose_details]),
                dict(title=dict(text=loose_title, x=0.03), height=800,
                     **{"xaxis.range": [0, int(loose.max()) * 1.2]}),
            ]),
        ],
    )],
    annotations=[dict(
        text="Source: supplied Syracuse tree inventory · Name before comma; aliases not normalized.<br>"
             "Counts of matching inventory records, not the percentage of trees on each street.",
        x=0, y=-0.23, xref="paper", yref="paper", showarrow=False,
        xanchor="left", align="left", font_size=11,
    )],
)

# Embed Plotly so the chart works offline. Hover reveals the species breakdown.
fig.write_html(HERE / "trees-understood-the-assignment.html", include_plotlyjs=True,
               config={"displayModeBar": False, "responsive": True})
df.loc[df["substring_match"]].to_csv(HERE / "tree_street_matches.csv", index=False)

print(f"Whole-word matches: {strict.sum()} across {len(strict)} streets")
print(f"Substring matches: {loose.sum()} across {len(loose)} streets")
print(f"Chart: {HERE / 'trees-understood-the-assignment.html'}")

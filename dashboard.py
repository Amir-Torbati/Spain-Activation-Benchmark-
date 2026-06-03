from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATABASE_PATH = Path(__file__).with_name("database.csv")
EXCEL_GREEN = "#217346"
EXCEL_DARK_GREEN = "#0F5B35"
EXCEL_MID_GREEN = "#70AD47"
EXCEL_LIGHT_GREEN = "#E2F0D9"
EXCEL_PALE_GREEN = "#F4FBF6"
GRID_GREEN = "#C6E0B4"
TEXT_DARK = "#1F2933"
TEXT_MUTED = "#5B6770"
AMBER = "#C28A0E"
PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

REQUIRED_COLUMNS = [
    "hour",
    "activated_up",
    "activated_dn",
    "reserve_up",
    "reserve_dn",
    "act_pct_up",
    "act_pct_dn",
    "price_up_eur_mwh",
    "price_dn_eur_mwh",
    "spot_eur_mwh",
]


st.set_page_config(
    page_title="Activation Benchmark",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --excel-green: {EXCEL_GREEN};
            --excel-dark-green: {EXCEL_DARK_GREEN};
            --excel-mid-green: {EXCEL_MID_GREEN};
            --excel-light-green: {EXCEL_LIGHT_GREEN};
            --excel-pale-green: {EXCEL_PALE_GREEN};
            --text-dark: {TEXT_DARK};
            --text-muted: {TEXT_MUTED};
        }}

        .stApp {{
            background: linear-gradient(180deg, #F7FBF8 0%, #FFFFFF 260px);
            color: var(--text-dark);
        }}

        [data-testid="stSidebar"] {{
            background: #F4FBF6;
            border-right: 1px solid #D9EAD3;
        }}

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: var(--excel-dark-green);
        }}

        .dashboard-header {{
            background: linear-gradient(135deg, #0F5B35 0%, #217346 60%, #70AD47 100%);
            color: white;
            padding: 24px 28px;
            border-radius: 8px;
            margin-bottom: 18px;
            box-shadow: 0 10px 24px rgba(15, 91, 53, 0.16);
        }}

        .dashboard-header h1 {{
            color: white;
            margin: 0 0 6px 0;
            font-size: 2rem;
            letter-spacing: 0;
        }}

        .dashboard-header p {{
            color: #EAF5E8;
            margin: 0;
            font-size: 1rem;
        }}

        .basis-card {{
            background: #FFFFFF;
            border: 1px solid #C6E0B4;
            border-left: 6px solid var(--excel-green);
            border-radius: 6px;
            padding: 14px 16px;
            margin: 4px 0 16px 0;
        }}

        .basis-card strong {{
            color: var(--excel-dark-green);
        }}

        .section-label {{
            color: var(--excel-dark-green);
            font-size: 1.05rem;
            font-weight: 800;
            margin: 8px 0 4px 0;
        }}

        .small-muted {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .download-note {{
            background: #F4FBF6;
            border: 1px solid #D9EAD3;
            border-radius: 6px;
            color: var(--text-muted);
            font-size: 0.9rem;
            margin: 4px 0 10px 0;
            padding: 10px 12px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 10px;
            margin: 6px 0 22px 0;
        }}

        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid #D9EAD3;
            border-left: 5px solid var(--excel-green);
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(15, 91, 53, 0.08);
            min-width: 0;
            padding: 8px 10px;
        }}

        .kpi-label {{
            color: var(--text-muted);
            font-size: 0.68rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 5px;
            white-space: nowrap;
        }}

        .kpi-value {{
            color: var(--excel-dark-green);
            font-size: 0.95rem;
            font-weight: 750;
            line-height: 1.15;
            overflow-wrap: anywhere;
        }}

        .kpi-extra {{
            color: var(--excel-green);
            font-size: 0.62rem;
            line-height: 1.1;
            margin-top: 5px;
            min-height: 0.75rem;
        }}

        .marker-strip {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 8px;
            margin: -4px 0 18px 0;
        }}

        .marker-card {{
            background: #F4FBF6;
            border: 1px solid #D9EAD3;
            border-radius: 6px;
            min-width: 0;
            padding: 8px 10px;
        }}

        .marker-label {{
            color: var(--text-muted);
            font-size: 0.7rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 4px;
        }}

        .marker-value {{
            color: var(--excel-dark-green);
            font-size: 0.95rem;
            font-weight: 750;
            line-height: 1.1;
        }}

        @media (max-width: 1100px) {{
            .kpi-grid,
            .marker-strip {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 720px) {{
            .kpi-grid,
            .marker-strip {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid #D9EAD3;
            border-radius: 6px;
        }}

        .stDownloadButton button {{
            background: var(--excel-green);
            color: white;
            border: 1px solid var(--excel-green);
            border-radius: 6px;
        }}

        .stDownloadButton button:hover {{
            background: var(--excel-dark-green);
            color: white;
            border: 1px solid var(--excel-dark-green);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_database(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"database.csv is missing required columns: {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS].copy()
    df["hour"] = pd.to_datetime(df["hour"], errors="coerce")

    numeric_cols = [col for col in REQUIRED_COLUMNS if col != "hour"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["hour", *numeric_cols])
    df = df.sort_values("hour").reset_index(drop=True)
    df["date"] = df["hour"].dt.date
    df["hour_of_day"] = df["hour"].dt.hour
    df["day_type"] = np.where(df["hour"].dt.dayofweek >= 5, "Weekend", "Weekday")
    df["month"] = df["hour"].dt.strftime("%Y-%m")
    df["act_fraction_up"] = df["act_pct_up"] / 100
    df["act_fraction_dn"] = df["act_pct_dn"] / 100
    return df


def percentile(series: pd.Series, q: float) -> float:
    clean = series.dropna()
    if clean.empty:
        return float("nan")
    return float(clean.quantile(q))


def metric_value(value: float, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.3f}{suffix}"


def pct_value(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.3f}%"


def percent_delta(series: pd.Series) -> float:
    return percentile(series, 0.90) - percentile(series, 0.50)


def render_kpi_grid(df: pd.DataFrame) -> None:
    cards = [
        ("Up P50", pct_value(percentile(df["act_pct_up"], 0.50)), f"P90-P50 {percent_delta(df['act_pct_up']):.3f} pp"),
        ("Up P90", pct_value(percentile(df["act_pct_up"], 0.90)), "Stress assumption"),
        ("Down P50", pct_value(percentile(df["act_pct_dn"], 0.50)), f"P90-P50 {percent_delta(df['act_pct_dn']):.3f} pp"),
        ("Down P90", pct_value(percentile(df["act_pct_dn"], 0.90)), "Stress assumption"),
        ("Avg spot", f"{df['spot_eur_mwh'].mean():,.2f}", "EUR/MWh"),
        ("Rows", f"{len(df):,}", "Filtered hours"),
    ]
    html = ['<div class="kpi-grid">']
    for label, value, extra in cards:
        html.append(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div><div class="kpi-extra">{extra}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_cdf_marker_strip(df: pd.DataFrame, directions: list[str]) -> None:
    direction_config = {
        "Up": "act_pct_up",
        "Down": "act_pct_dn",
    }
    cards = []
    for direction in directions:
        col = direction_config[direction]
        cards.extend(
            [
                (f"{direction} P50", pct_value(percentile(df[col], 0.50))),
                (f"{direction} P90", pct_value(percentile(df[col], 0.90))),
                (f"{direction} average", pct_value(df[col].mean())),
            ]
        )

    html = ['<div class="marker-strip">']
    for label, value in cards:
        html.append(
            f'<div class="marker-card"><div class="marker-label">{label}</div>'
            f'<div class="marker-value">{value}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def plotly_layout(height: int) -> dict[str, object]:
    return {
        "height": height,
        "margin": {"l": 24, "r": 24, "t": 34, "b": 24},
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "font": {"color": TEXT_DARK, "family": "Arial, sans-serif"},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        "hovermode": "x unified",
    }


def build_cdf_figure(df: pd.DataFrame, directions: list[str]) -> go.Figure:
    fig = go.Figure()
    config = {
        "Up": {"col": "act_pct_up", "color": EXCEL_GREEN},
        "Down": {"col": "act_pct_dn", "color": EXCEL_MID_GREEN},
    }
    markers = []
    axis_values = []

    for direction in directions:
        col = config[direction]["col"]
        values = np.sort(df[col].dropna().to_numpy())
        if values.size == 0:
            continue

        axis_values.extend(values.tolist())
        y = np.arange(1, values.size + 1) / values.size
        p50 = np.quantile(values, 0.50)
        p90 = np.quantile(values, 0.90)
        mean = np.mean(values)
        color = config[direction]["color"]

        fig.add_trace(
            go.Scatter(
                x=values,
                y=y,
                mode="lines",
                name=f"{direction} CDF",
                line={"color": color, "width": 3},
                hovertemplate=f"{direction}<br>Activation: %{{x:.3f}}%<br>CDF: %{{y:.1%}}<extra></extra>",
            )
        )
        fig.add_vline(
            x=p50,
            line_width=2,
            line_dash="dash",
            line_color=color,
        )
        fig.add_vline(
            x=p90,
            line_width=2,
            line_dash="dot",
            line_color=color,
        )
        fig.add_vline(
            x=mean,
            line_width=1,
            line_dash="solid",
            line_color="#9CA3AF",
        )
        markers.extend(
            [
                {"x": p50, "text": f"{direction} P50<br>{p50:.2f}%", "color": color},
                {"x": p90, "text": f"{direction} P90<br>{p90:.2f}%", "color": color},
                {"x": mean, "text": f"{direction} avg<br>{mean:.2f}%", "color": "#64748B"},
            ]
        )

    if markers and axis_values:
        x_span = max(axis_values) - min(axis_values)
        min_gap = max(x_span * 0.07, 0.9)
        lane_y = [0.95, 0.86, 0.77, 0.68, 0.59]
        lane_last_x = [-float("inf")] * len(lane_y)

        for marker in sorted(markers, key=lambda item: item["x"]):
            lane_idx = next(
                (idx for idx, last_x in enumerate(lane_last_x) if marker["x"] - last_x >= min_gap),
                int(np.argmin(lane_last_x)),
            )
            lane_last_x[lane_idx] = marker["x"]
            fig.add_annotation(
                x=marker["x"],
                y=lane_y[lane_idx],
                xref="x",
                yref="paper",
                text=marker["text"],
                showarrow=False,
                align="center",
                xanchor="center",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.90)",
                bordercolor=marker["color"],
                borderpad=3,
                borderwidth=1,
                font={"size": 10, "color": TEXT_DARK},
            )

    fig.update_layout(
        **plotly_layout(600),
        xaxis_title="Activation portion of reserve capacity (%)",
        yaxis_title="Cumulative probability",
        yaxis_tickformat=".0%",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    return fig


def build_timeseries_figure(df: pd.DataFrame, directions: list[str]) -> go.Figure:
    fig = go.Figure()
    if "Up" in directions:
        fig.add_trace(
            go.Scatter(
                x=df["hour"],
                y=df["act_pct_up"],
                mode="lines",
                name="Up",
                line={"color": EXCEL_GREEN, "width": 1.5},
            )
        )
    if "Down" in directions:
        fig.add_trace(
            go.Scatter(
                x=df["hour"],
                y=df["act_pct_dn"],
                mode="lines",
                name="Down",
                line={"color": EXCEL_MID_GREEN, "width": 1.5},
            )
        )

    fig.update_layout(
        **plotly_layout(360),
        xaxis_title="Hour",
        yaxis_title="Activation portion (%)",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    return fig


def build_hourly_model_table(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("hour_of_day")
    table = pd.DataFrame(
        {
            "samples": grouped.size(),
            "up_p50_pct": grouped["act_pct_up"].quantile(0.50),
            "up_p75_pct": grouped["act_pct_up"].quantile(0.75),
            "up_p90_pct": grouped["act_pct_up"].quantile(0.90),
            "dn_p50_pct": grouped["act_pct_dn"].quantile(0.50),
            "dn_p75_pct": grouped["act_pct_dn"].quantile(0.75),
            "dn_p90_pct": grouped["act_pct_dn"].quantile(0.90),
        }
    ).reset_index()

    for col in [c for c in table.columns if c.endswith("_pct")]:
        fraction_col = col.replace("_pct", "_fraction")
        table[fraction_col] = table[col] / 100

    return table.round(6)


def build_hourly_profile_figure(hourly_table: pd.DataFrame, directions: list[str]) -> go.Figure:
    fig = go.Figure()
    if "Up" in directions:
        fig.add_trace(
            go.Scatter(
                x=hourly_table["hour_of_day"],
                y=hourly_table["up_p50_pct"],
                mode="lines+markers",
                name="Up P50",
                line={"color": EXCEL_GREEN, "width": 3},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=hourly_table["hour_of_day"],
                y=hourly_table["up_p90_pct"],
                mode="lines+markers",
                name="Up P90",
                line={"color": EXCEL_GREEN, "width": 2, "dash": "dot"},
            )
        )
    if "Down" in directions:
        fig.add_trace(
            go.Scatter(
                x=hourly_table["hour_of_day"],
                y=hourly_table["dn_p50_pct"],
                mode="lines+markers",
                name="Down P50",
                line={"color": EXCEL_MID_GREEN, "width": 3},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=hourly_table["hour_of_day"],
                y=hourly_table["dn_p90_pct"],
                mode="lines+markers",
                name="Down P90",
                line={"color": EXCEL_MID_GREEN, "width": 2, "dash": "dot"},
            )
        )

    fig.update_layout(
        **plotly_layout(380),
        xaxis_title="Hour of day",
        yaxis_title="Activation portion (%)",
    )
    fig.update_xaxes(tickmode="linear", dtick=1, showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_GREEN, zeroline=False)
    return fig


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for direction, pct_col, activated_col, reserve_col, price_col in [
        ("Up", "act_pct_up", "activated_up", "reserve_up", "price_up_eur_mwh"),
        ("Down", "act_pct_dn", "activated_dn", "reserve_dn", "price_dn_eur_mwh"),
    ]:
        rows.append(
            {
                "direction": direction,
                "p50_pct": percentile(df[pct_col], 0.50),
                "p75_pct": percentile(df[pct_col], 0.75),
                "p90_pct": percentile(df[pct_col], 0.90),
                "p95_pct": percentile(df[pct_col], 0.95),
                "max_pct": df[pct_col].max(),
                "average_pct": df[pct_col].mean(),
                "avg_activated_mw": df[activated_col].mean(),
                "avg_reserve_mw": df[reserve_col].mean(),
                "avg_price_eur_mwh": df[price_col].mean(),
            }
        )
    return pd.DataFrame(rows).round(4)


def filter_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    min_date = df["date"].min()
    max_date = df["date"].max()

    with st.sidebar:
        st.header("Filter window")
        st.caption(f"Database: {len(df):,} hourly records")
        selected_dates = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        hour_range = st.slider("Hour of day", 0, 23, (0, 23))
        day_types = st.multiselect("Day type", ["Weekday", "Weekend"], default=["Weekday", "Weekend"])
        directions = st.multiselect("Direction", ["Up", "Down"], default=["Up", "Down"])

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    filtered = df[
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["hour_of_day"] >= hour_range[0])
        & (df["hour_of_day"] <= hour_range[1])
        & (df["day_type"].isin(day_types))
    ].copy()

    return filtered, directions


def main() -> None:
    apply_theme()

    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Activation Benchmark</h1>
            <p>BESS reserve activation assumptions calibrated from historical activation portions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not DATABASE_PATH.exists():
        st.error("database.csv was not found in the project folder.")
        st.stop()

    df = load_database(DATABASE_PATH)
    filtered, directions = filter_data(df)

    if filtered.empty or not directions:
        st.warning("No data is available for the selected filters.")
        st.stop()

    date_min = filtered["hour"].min().strftime("%Y-%m-%d %H:%M")
    date_max = filtered["hour"].max().strftime("%Y-%m-%d %H:%M")
    hourly_table = build_hourly_model_table(filtered)

    st.markdown(
        f"""
        <div class="basis-card">
            <strong>Model basis:</strong> activation assumptions use the historical distribution,
            especially P50 for base case and P90 for stress case. Averages are shown only as reference.
            <br><span class="small-muted">{len(filtered):,} hourly records | {date_min} to {date_max}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpi_grid(filtered)

    distribution_tab, hourly_tab, details_tab = st.tabs(
        ["Distribution benchmark", "Hourly model assumptions", "Detail checks"]
    )

    with distribution_tab:
        st.markdown('<div class="section-label">CDF distribution with P50, P90, and average</div>', unsafe_allow_html=True)
        st.plotly_chart(build_cdf_figure(filtered, directions), width="stretch", config=PLOT_CONFIG)
        render_cdf_marker_strip(filtered, directions)

        st.markdown('<div class="section-label">Scenario percentiles</div>', unsafe_allow_html=True)
        st.dataframe(
            build_summary_table(filtered),
            width="stretch",
            hide_index=True,
            column_config={
                "direction": "Direction",
                "p50_pct": st.column_config.NumberColumn("P50 %", format="%.3f"),
                "p75_pct": st.column_config.NumberColumn("P75 %", format="%.3f"),
                "p90_pct": st.column_config.NumberColumn("P90 %", format="%.3f"),
                "p95_pct": st.column_config.NumberColumn("P95 %", format="%.3f"),
                "max_pct": st.column_config.NumberColumn("Max %", format="%.3f"),
                "average_pct": st.column_config.NumberColumn("Average %", format="%.3f"),
                "avg_activated_mw": st.column_config.NumberColumn("Avg activated MW", format="%.1f"),
                "avg_reserve_mw": st.column_config.NumberColumn("Avg reserve MW", format="%.1f"),
                "avg_price_eur_mwh": st.column_config.NumberColumn("Avg price EUR/MWh", format="%.2f"),
            },
        )
        st.markdown(
            """
            <div class="basis-card">
                <strong>Use in model:</strong> choose P50/P75/P90 fractions from the hourly table.
                The average can be useful for reports, but it is not the robust assumption target.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with hourly_tab:
        st.markdown('<div class="section-label">Hourly percentile profile</div>', unsafe_allow_html=True)
        st.plotly_chart(build_hourly_profile_figure(hourly_table, directions), width="stretch", config=PLOT_CONFIG)

        st.markdown('<div class="section-label">Exportable model assumption table</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="download-note">
                The download uses the current filters and exports 24 hourly rows with P50/P75/P90 activation
                assumptions. Use the fraction columns in the optimization model.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            hourly_table,
            width="stretch",
            hide_index=True,
            column_config={
                "hour_of_day": st.column_config.NumberColumn("Hour", format="%d"),
                "samples": st.column_config.NumberColumn("Samples", format="%d"),
                "up_p50_pct": st.column_config.NumberColumn("Up P50 %", format="%.3f"),
                "up_p75_pct": st.column_config.NumberColumn("Up P75 %", format="%.3f"),
                "up_p90_pct": st.column_config.NumberColumn("Up P90 %", format="%.3f"),
                "dn_p50_pct": st.column_config.NumberColumn("Down P50 %", format="%.3f"),
                "dn_p75_pct": st.column_config.NumberColumn("Down P75 %", format="%.3f"),
                "dn_p90_pct": st.column_config.NumberColumn("Down P90 %", format="%.3f"),
                "up_p50_fraction": st.column_config.NumberColumn("Up P50 fraction", format="%.5f"),
                "up_p75_fraction": st.column_config.NumberColumn("Up P75 fraction", format="%.5f"),
                "up_p90_fraction": st.column_config.NumberColumn("Up P90 fraction", format="%.5f"),
                "dn_p50_fraction": st.column_config.NumberColumn("Down P50 fraction", format="%.5f"),
                "dn_p75_fraction": st.column_config.NumberColumn("Down P75 fraction", format="%.5f"),
                "dn_p90_fraction": st.column_config.NumberColumn("Down P90 fraction", format="%.5f"),
            },
        )
        st.download_button(
            "Download model assumptions",
            hourly_table.to_csv(index=False).encode("utf-8"),
            file_name="activation_model_assumptions.csv",
            mime="text/csv",
        )

    with details_tab:
        st.markdown('<div class="section-label">Hourly activation time series</div>', unsafe_allow_html=True)
        st.plotly_chart(build_timeseries_figure(filtered, directions), width="stretch", config=PLOT_CONFIG)

        with st.expander("Database preview"):
            st.dataframe(filtered.tail(200), width="stretch", hide_index=True)


if __name__ == "__main__":
    main()

# Activation Benchmark

This project stores activation data in `database.csv` and exposes a Streamlit dashboard for BESS optimization assumptions.

## Update the database

When a new API export is added to the folder, append it into the database with:

```powershell
python update_database.py new_activation_file.csv
```

The update script validates the schema, appends new hours, replaces duplicated hours with the latest uploaded values, sorts by `hour`, and writes the result back to `database.csv`.

## Run the dashboard

```powershell
streamlit run dashboard.py
```

The dashboard includes:

- Date range, hour, weekday/weekend, and direction filters
- CDF distribution plot for up/down activation
- P50 and P90 markers
- Scenario percentile summary
- Hourly model assumption table with percent and fraction values

Use the fraction columns for the optimization model. For example, `up_p90_fraction = 0.05084` means 5.084 percent of reserve capacity.

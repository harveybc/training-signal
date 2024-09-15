import pandas as pd
import time
from app.data_handler import load_csv, write_csv
from app.config_handler import save_debug_info, remote_log
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def process_data(data, plugin, config):
    """
    Processes the data using the specified plugin.
    """
    print("Processing data using plugin...")

    # Keep the date column separate
    if 'date' in data.columns:
        date_column = data['date']
    else:
        date_column = data.index

    # Debugging: Show the data columns before processing
    print(f"Data columns before processing: {data.columns}")

    # Select OHLC columns by name explicitly (or the expected columns)
    ohlc_columns = ['c1', 'c2', 'c3', 'c4']  # These are placeholders for OHLC
    if all(col in data.columns for col in ohlc_columns):
        numeric_data = data[ohlc_columns]
    else:
        raise KeyError(f"Missing expected OHLC columns: {ohlc_columns}")

    # Ensure input data is numeric
    numeric_data = numeric_data.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Use the plugin to process the numeric data (e.g., feature extraction)
    processed_data = plugin.process(numeric_data)

    # Debugging message to confirm the shape of the processed data
    print(f"Processed data shape: {processed_data.shape}")

    return processed_data


def analyze_and_plot_columns(processed_data):
    """
    Analyze each column for variability, normality, and apply normalization/log transformation if needed.
    Generate a distribution plot for each column.
    """

    print("Analyzing variability and normality of each column...")

    # Prepare for multiple subplots
    num_columns = len(processed_data.columns)
    num_rows = int(np.ceil(num_columns / 3))
    fig, axes = plt.subplots(num_rows, 3, figsize=(15, 5 * num_rows))
    axes = axes.flatten()

    for idx, column in enumerate(processed_data.columns):
        data_column = processed_data[column]

        # Variability check: Calculate the standard deviation and mean
        variability = data_column.std()
        print(f"Variability for {column}: {variability}")

        # Normality check: Shapiro-Wilk test or D'Agostino test
        stat, p_value = stats.normaltest(data_column)
        is_normal = p_value > 0.05

        # If not normal and skewed, apply log transformation
        if not is_normal and stats.skew(data_column) > 0.5:
            print(f"Applying log transformation to {column}")
            data_column = np.log1p(data_column)

        # After transformation, check again if the column should use z-score or min-max normalization
        if is_normal:
            print(f"{column} seems to be normally distributed. Applying z-score normalization.")
            normalized_column = stats.zscore(data_column)
        else:
            print(f"{column} is not normally distributed. Applying min-max normalization.")
            normalized_column = (data_column - data_column.min()) / (data_column.max() - data_column.min())

        # Plot the column data after any transformations
        sns.histplot(normalized_column, kde=True, ax=axes[idx])
        axes[idx].set_title(f"Distribution of {column}")

        # Update the processed data with normalized values
        processed_data[column] = normalized_column

    plt.tight_layout()
    plt.show()

    return processed_data


def run_feature_engineering_pipeline(config, plugin):
    """
    Runs the feature-engineering pipeline using the plugin and performs additional analysis.
    """
    start_time = time.time()

    # Load the data
    print(f"Loading data from {config['input_file']}...")
    data = load_csv(config['input_file'])
    print(f"Data loaded with shape: {data.shape}")

    # Process the data
    processed_data = process_data(data, plugin, config)

    # Analyze and plot if distribution_plot is enabled
    if config.get('distribution_plot', False):
        processed_data = analyze_and_plot_columns(processed_data)

    # Save the processed data to the output file if specified
    if config['output_file']:
        processed_data.to_csv(config['output_file'], index=False)
        print(f"Processed data saved to {config['output_file']}.")

    # Save final configuration and debug information
    end_time = time.time()
    execution_time = end_time - start_time
    debug_info = {
        'execution_time': float(execution_time)
    }

    # Save debug info if specified
    if config.get('save_log'):
        save_debug_info(debug_info, config['save_log'])
        print(f"Debug info saved to {config['save_log']}.")

    # Remote log debug info and config if specified
    if config.get('remote_log'):
        remote_log(config, debug_info, config['remote_log'], config['username'], config['password'])
        print(f"Debug info saved to {config['remote_log']}.")

    print(f"Execution time: {execution_time} seconds")


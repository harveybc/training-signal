import pandas as pd
import time
from app.data_handler import load_csv, write_csv
from app.config_handler import save_debug_info, remote_log
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import normaltest, shapiro, skew, kurtosis, anderson
import numpy as np
import warnings
# Suppress the specific UserWarning from scipy.stats about p-values for large datasets
warnings.filterwarnings("ignore", message="p-value may not be accurate for N > 5000.")


def process_data(data, plugin, config):
    """
    Processes the data using the specified plugin and performs additional analysis
    if distribution_plot or correlation_analysis are set to True.
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
    
    # Analyze variability and normality
    transformed_data = analyze_variability_and_normality(processed_data)


    return transformed_data




def analyze_variability_and_normality(data):
    """
    Analyzes each column's variability, normality, and skewness.
    Applies log transformation, z-score normalization, or min-max normalization.
    Returns transformed data with modified column names.
    """
    print("Analyzing variability and normality of each column...")

    transformed_data = data.copy()
    transformed_columns = {}  # To store transformed column names and their data
    num_columns = len(data.columns)
    num_rows = (num_columns + 3) // 4  # Adjust to show 4 columns of plots
    fig, axes = plt.subplots(num_rows, 4, figsize=(20, num_rows * 5))
    axes = axes.flatten()

    plot_index = 0

    for column in transformed_data.columns:
        # Handle missing values by filling with mean for analysis (silent operation)
        if transformed_data[column].isna().sum() > 0:
            transformed_data[column] = transformed_data[column].fillna(transformed_data[column].mean())

        # Variability (standard deviation)
        variability = np.std(transformed_data[column])

        # Normality test using D'Agostino's K^2 and Shapiro-Wilk
        dagostino_result = normaltest(transformed_data[column])
        shapiro_result = shapiro(transformed_data[column])

        # p-values
        p_value_normaltest = dagostino_result.pvalue
        p_value_shapiro = shapiro_result.pvalue

        # Skewness and Kurtosis
        column_skewness = skew(transformed_data[column])
        column_kurtosis = kurtosis(transformed_data[column])

        # Log transformation criteria (for skewed columns)
        if abs(column_skewness) > 0.5:
            print(f"Applying log transformation to {column} due to high skewness.")
            log_transformed_column = np.log1p(transformed_data[column].abs())  # Log-transformation
            transformed_columns[f"Log_{column}"] = log_transformed_column
            column = f"Log_{column}"  # Refer to the log-transformed column
            column_skewness = skew(log_transformed_column)
            column_kurtosis = kurtosis(log_transformed_column)

        # Apply z-score normalization or min-max normalization
        if abs(column_skewness) <= 0.5 and -1.0 <= column_kurtosis <= 6.0 and "EMA" not in column:
            print(f"{column} is almost normally distributed because skewness is {column_skewness:.5f} in [-0.5, 0.5] and kurtosis is {column_kurtosis:.5f} in [-1, 6]. Applying z-score normalization.")
            standardized_column = (transformed_data[column] - transformed_data[column].mean()) / transformed_data[column].std()
            transformed_columns[f"Standardized_{column}"] = standardized_column
        else:
            print(f"{column} is not normally distributed because D'Agostino p-value is {p_value_normaltest:.5f} <= 0.05 or Shapiro-Wilk p-value is {p_value_shapiro:.5f} <= 0.05, and skewness is {column_skewness:.5f}, kurtosis is {column_kurtosis:.5f}. Applying min-max normalization.")
            normalized_column = (transformed_data[column] - transformed_data[column].min()) / (transformed_data[column].max() - transformed_data[column].min())
            transformed_columns[f"Normalized_{column}"] = normalized_column

        # Plotting the transformed distribution
        final_column_name = f"Standardized_{column}" if f"Standardized_{column}" in transformed_columns else f"Normalized_{column}"
        sns.histplot(transformed_columns[final_column_name], kde=True, ax=axes[plot_index])
        axes[plot_index].set_title(f"{final_column_name} (Transformed)", fontsize=10)
        plot_index += 1

    # Adjust layout and vertical separation
    plt.tight_layout(h_pad=10, pad=3)  # Added padding to prevent overlap
    plt.show()

    # Convert the transformed columns dictionary back into a DataFrame and return it
    transformed_data = pd.DataFrame(transformed_columns)
    
    return transformed_data







def run_feature_engineering_pipeline(config, plugin):
    """
    Runs the feature-engineering pipeline using the plugin.
    """
    start_time = time.time()

    # Load the data
    print(f"Loading data from {config['input_file']}...")
    data = load_csv(config['input_file'])
    print(f"Data loaded with shape: {data.shape}")

    # Process the data
    processed_data = process_data(data, plugin, config)

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

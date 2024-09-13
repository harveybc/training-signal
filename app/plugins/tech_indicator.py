import pandas_ta as ta
import pandas as pd

class Plugin:
    """
    A feature-engineering plugin using technical indicators.
    """

    # Plugin parameters including short, mid, and long-term period configurations
    plugin_params = {
        'short_term_period': 14,
        'mid_term_period': 50,
        'long_term_period': 200,
        'indicators': ['rsi', 'macd', 'ema', 'stoch', 'adx', 'atr', 'cci', 'bbands', 'williams', 'momentum', 'roc'],
        'ohlc_order': 'ohlc'  # Default column order: Open, High, Low, Close
    }

    # Debug variables to track important parameters and results
    plugin_debug_vars = ['short_term_period', 'mid_term_period', 'long_term_period', 'output_columns', 'ohlc_order']

    def __init__(self):
        self.params = self.plugin_params.copy()

    def set_params(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.params:
                self.params[key] = value

    def get_debug_info(self):
        return {var: self.params.get(var, None) for var in self.plugin_debug_vars}



    def adjust_ohlc(self, data):
        """
        Adjust the OHLC columns based on the ohlc_order parameter.
        This method renames 'c1', 'c2', 'c3', and 'c4' to 'Open', 'High', 'Low', and 'Close'
        according to the OHLC order provided, and then ensures the correct columns are selected.

        Parameters:
        data (pd.DataFrame): Input DataFrame with the columns ['c1', 'c2', 'c3', 'c4', ...]

        Returns:
        pd.DataFrame: DataFrame with the OHLC columns renamed and ordered.
        """
        print("Starting adjust_ohlc method...")
        
        # Step 1: Define the renaming order based on OHLC parameter
        print(f"Received OHLC order: {self.params['ohlc_order']}")
        if self.params['ohlc_order'] == 'ohlc':
            ordered_columns = ['Open', 'High', 'Low', 'Close']
        elif self.params['ohlc_order'] == 'olhc':
            ordered_columns = ['Open', 'Low', 'High', 'Close']
        else:
            print("Invalid OHLC order specified. Raising ValueError.")
            raise ValueError("Invalid OHLC order specified")
        
        # Step 2: Define the renaming map
        rename_map = {
            'c1': ordered_columns[0],
            'c2': ordered_columns[1],
            'c3': ordered_columns[2],
            'c4': ordered_columns[3]
        }
        
        # Debugging: Print renaming map before applying
        print(f"Renaming columns map: {rename_map}")
        
        # Step 3: Rename columns and store the result
        try:
            data_renamed = data.rename(columns=rename_map)
        except Exception as e:
            print(f"Error during renaming columns: {e}")
            raise

        # Debugging: Print first few rows of the renamed data
        print("First 5 rows of renamed data:")
        print(data_renamed.head())
        
        # Step 4: Check if all renamed columns are in the dataset
        print(f"Checking if the renamed columns exist in the DataFrame...")
        print(f"Expected columns after renaming: {ordered_columns}")
        missing_columns = [col for col in ordered_columns if col not in data_renamed.columns]
        
        if missing_columns:
            print(f"Error: Missing columns after renaming - {missing_columns}")
            raise KeyError(f"Missing columns after renaming: {missing_columns}")
        
        # Debugging: Confirm all expected columns are present
        print(f"All expected columns found: {ordered_columns}")

        # Step 5: Return data with columns ordered according to the OHLC order
        try:
            result = data_renamed[ordered_columns]
        except KeyError as e:
            print(f"KeyError when selecting ordered columns: {e}")
            print(f"Available columns: {data_renamed.columns}")
            raise
        
        # Debugging: Print the shape of the final DataFrame and column names
        print(f"Final data shape: {result.shape}")
        print(f"Final column names: {result.columns}")

        return result







    def process(self, data):
        """
        Process the input data by calculating the specified technical indicators using their default parameters.
        
        Parameters:
        data (pd.DataFrame): Input time-series data with renamed 'Open', 'High', 'Low', 'Close', etc.
        
        Returns:
        pd.DataFrame: DataFrame with the calculated technical indicators.
        """
        print(f"Calculating technical indicators using default parameters...")

        # Adjust the OHLC order of the columns
        data = self.adjust_ohlc(data)

        # Debug: Print the first 50 rows of the data to verify input
        print(f"First 50 rows of data:\n{data.head(50)}")

        # Initialize a dictionary to hold all technical indicators
        technical_indicators = {}

        # Calculate each indicator using default parameters
        for indicator in self.params['indicators']:
            if indicator == 'rsi':
                rsi = ta.rsi(data['Close'])  # Using default length of 14
                if rsi is not None:
                    technical_indicators['RSI'] = rsi
                    print(f"RSI calculated with shape: {rsi.shape}")
            
            elif indicator == 'macd':
                macd = ta.macd(data['Close'])  # Using default fast, slow, and signal periods
                if 'MACD_12_26_9' in macd.columns:
                    technical_indicators['MACD'] = macd['MACD_12_26_9']
                if 'MACDs_12_26_9' in macd.columns:
                    technical_indicators['MACD_signal'] = macd['MACDs_12_26_9']
                print(f"MACD columns returned: {macd.columns}")
            
            elif indicator == 'ema':
                ema = ta.ema(data['Close'])  # Using default length of 20
                if ema is not None:
                    technical_indicators['EMA'] = ema
                    print(f"EMA calculated with shape: {ema.shape}")
            
            elif indicator == 'stoch':
                stoch = ta.stoch(data['High'], data['Low'], data['Close'])  # Default %K and %D values
                if 'STOCHk_14_3_3' in stoch.columns:
                    technical_indicators['StochK'] = stoch['STOCHk_14_3_3']
                if 'STOCHd_14_3_3' in stoch.columns:
                    technical_indicators['StochD'] = stoch['STOCHd_14_3_3']
                print(f"Stochastic columns returned: {stoch.columns}")
            
            elif indicator == 'adx':
                adx = ta.adx(data['High'], data['Low'], data['Close'])  # Using default length of 14
                if 'ADX_14' in adx.columns:
                    technical_indicators['ADX'] = adx['ADX_14']
                print(f"ADX columns returned: {adx.columns}")
            
            elif indicator == 'atr':
                atr = ta.atr(data['High'], data['Low'], data['Close'])  # Default length of 14
                if atr is not None:
                    technical_indicators['ATR'] = atr
                    print(f"ATR calculated with shape: {atr.shape}")
            
            elif indicator == 'cci':
                cci = ta.cci(data['High'], data['Low'], data['Close'])  # Default length of 20
                if cci is not None:
                    technical_indicators['CCI'] = cci
                    print(f"CCI calculated with shape: {cci.shape}")
            
            elif indicator == 'bbands':
                bbands = ta.bbands(data['Close'])  # Default length of 20
                if 'BBU_20_2.0' in bbands.columns and 'BBL_20_2.0' in bbands.columns:
                    technical_indicators['BB_Upper'] = bbands['BBU_20_2.0']
                    technical_indicators['BB_Lower'] = bbands['BBL_20_2.0']
                    print(f"BB_Upper and BB_Lower calculated.")
            
            elif indicator == 'williams':
                williams = ta.willr(data['High'], data['Low'], data['Close'])  # Default length of 14
                if williams is not None:
                    technical_indicators['WilliamsR'] = williams
                    print(f"WilliamsR calculated with shape: {williams.shape}")
            
            elif indicator == 'momentum':
                momentum = ta.mom(data['Close'])  # Default length of 10
                if momentum is not None:
                    technical_indicators['Momentum'] = momentum
                    print(f"Momentum calculated with shape: {momentum.shape}")
            
            elif indicator == 'roc':
                roc = ta.roc(data['Close'])  # Default length of 10
                if roc is not None:
                    technical_indicators['ROC'] = roc
                    print(f"ROC calculated with shape: {roc.shape}")
            
            # Ichimoku has been removed as per your request
            
        # Create a DataFrame from the calculated technical indicators
        indicator_df = pd.DataFrame(technical_indicators)

        # Update debug info with the names of the output columns
        self.params['output_columns'] = list(indicator_df.columns)
        print(f"Calculated technical indicators: {self.params['output_columns']}")

        return indicator_df







    def add_debug_info(self, debug_info):
        plugin_debug_info = self.get_debug_info()
        debug_info.update(plugin_debug_info)

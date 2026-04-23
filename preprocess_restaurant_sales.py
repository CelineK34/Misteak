import pandas as pd

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
if __name__ == "__main__":
    data = load_data("C:\\Users\\User\\Documents\\misteak\\Misteak\\restaurant_sales_data.csv")
    df= data

    #Check for missing values
    print("Missing values in each column:")
    print(df.isna().sum())

    #check for duplicates
    print("Number of duplicate rows:", df.duplicated().sum())

    #convert date column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
    print("Data types after conversion:")
    print(df.dtypes)

    #ensure bool columns are of boolean type
    bool_columns = ['has_promotion', 'special_event']
    for col in bool_columns:
        df[col] = df[col].astype(bool)

    #ensure string columns are stripped of whitespace and in title case
    string_columns = ['restaurant_type', 'menu_item_name', 'meal_type','key_ingredients_tags','weather_condition']
    for col in string_columns:
        df[col] = df[col].str.strip().str.title()

    #ensure float columns are of float type
    float_columns = ['typical_ingredient_cost', 'observed_market_price','actual_selling_price']
    for col in float_columns:
        df[col] = df[col].astype(float)

    #ensure quantity_sold is of integer type
    df['quantity_sold'] = df['quantity_sold'].astype(int)

    print("\nShape:", df.shape)
    print("Data range:",df['date'].min(), "to", df['date'].max())
    print("Missing values in each column:",df.isna().sum())

    #handle zero demand
    zero_qty = df[df['quantity_sold'] == 0]
    print("\nRows with zero quantity sold:", zero_qty.shape[0])

    #remove outliers
    before=df.shape[0]
    for col in float_columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        print(f"\nOutliers in {col}: {outliers.shape[0]}")
        df = df[((df[col] >= lower_bound) & (df[col] <= upper_bound)) |
            (df['quantity_sold'] == 0)]
    print(f"\nRemoved {before - df.shape[0]} outliers.")
    print("\nShape after outlier removal:", df.shape)

    # Cost should never be higher than selling price (selling at a loss)
    invalid_cost = df[df['typical_ingredient_cost'] > df['actual_selling_price']]
    print("Cost > Selling Price:", invalid_cost.shape[0])

    # Selling price should never be 0 or negative
    invalid_price = df[df['actual_selling_price'] <= 0]
    print("Zero/negative selling price:", invalid_price.shape[0])

    # Market price should never be 0 or negative
    invalid_market = df[df['observed_market_price'] <= 0]
    print("Zero/negative market price:", invalid_market.shape[0])

    # Quantity sold should never be negative
    invalid_qty = df[df['quantity_sold'] < 0]
    print("Negative quantity:", invalid_qty.shape[0])

    # restaurant_id should never be negative or zero
    invalid_id = df[df['restaurant_id'] <= 0]
    print("Invalid restaurant ID:", invalid_id.shape[0])

    # Check for unexpected restaurant types
    valid_restaurant_types = ['Food Stall', 'Casual Dining', 'Fine Dining', 'Cafe', 'Kopitiam']
    invalid_types = df[~df['restaurant_type'].isin(valid_restaurant_types)]
    print("Invalid restaurant types:", invalid_types['restaurant_type'].unique())

    # Check for unexpected meal types
    valid_meal_types = ['Breakfast', 'Lunch', 'Dinner']
    invalid_meals = df[~df['meal_type'].isin(valid_meal_types)]
    print("Invalid meal types:", invalid_meals['meal_type'].unique())

    # Check for unexpected weather values
    valid_weather = ['Sunny', 'Rainy', 'Cloudy']
    invalid_weather = df[~df['weather_condition'].isin(valid_weather)]
    print("Invalid weather:", invalid_weather['weather_condition'].unique())

    # Future dates (data shouldn't have dates beyond today)
    future_dates = df[df['date'] > pd.Timestamp.today()]
    print("Future dates:", future_dates.shape[0])

    # Dates that are too old (before 2020 for example)
    too_old = df[df['date'] < pd.Timestamp('2020-01-01')]
    print("Suspiciously old dates:", too_old.shape[0])

    # Quick summary — look for suspicious min/max values
    print(df[['typical_ingredient_cost', 'observed_market_price', 
            'actual_selling_price', 'quantity_sold']].describe())
    
    # Market price should be in a realistic range vs selling price
    # e.g. not 10x higher or lower
    suspicious = df[
        (df['observed_market_price'] > df['actual_selling_price'] * 5) |
        (df['observed_market_price'] < df['actual_selling_price'] * 0.1)
    ]
    print("Suspicious market vs selling price rows:", suspicious.shape[0])

    print(f"\nShape after: {df.shape[0]}")

    #feature engineering
    df['profit_margin'] = df['actual_selling_price'] - df['typical_ingredient_cost']
    df['is_promotion'] = df['has_promotion'].astype(int)
    df['is_special_event'] = df['special_event'].astype(int)
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)
    df['price_to_cost_ratio'] = df['actual_selling_price'] / df['typical_ingredient_cost']
    df['price_to_market_ratio'] = df['actual_selling_price'] / df['observed_market_price']
    df['revenue'] = df['actual_selling_price'] * df['quantity_sold']
    df=pd.get_dummies(df, columns=['restaurant_type', 'meal_type', 'weather_condition'], drop_first=True)

    df.to_csv("C:\\Users\\User\\Documents\\misteak\\Misteak\\preprocessed_restaurant_sales_data.csv", index=False)

    print("\nFeature engineering complete. Shape:", df.shape)
    print(df.head(3).to_string())
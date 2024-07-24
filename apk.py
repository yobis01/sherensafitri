import streamlit as st 
import joblib
import matplotlib.pyplot as plt
import pandas as pd

# Load models
arima_model = joblib.load('arima_model.pkl')
hw_model = joblib.load('holtwinters_model.pkl')

# Function to make predictions
def make_prediction(model, start_date, end_date):
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date)

    # Make predictions
    forecast = model.predict(start=date_range[0], end=date_range[-1])
    return forecast

st.title('Stock Forecasting App')

# Interface for user input
start_date = st.date_input('Select start date for prediction:')
end_date = st.date_input('Select end date for prediction:')

# Button to trigger prediction for ARIMA
if st.button('Predict ARIMA'):
    # Make predictions for ARIMA
    arima_forecast = make_prediction(arima_model, start_date, end_date)

    # Display ARIMA predictions
    st.write("ARIMA Forecast:")
    st.write(arima_forecast)

    # Plot ARIMA forecast
    plt.figure(figsize=(10, 6))
    plt.plot(arima_forecast, label='ARIMA Forecast')
    plt.title('ARIMA Stock Forecast')
    plt.xlabel('Steps')
    plt.ylabel('Forecasted Values')
    plt.legend()
    st.pyplot(plt)

# Button to trigger prediction for Holt-Winters
if st.button('Predict Holt-Winters'):
    # Make predictions for Holt-Winters
    hw_forecast = make_prediction(hw_model, start_date, end_date)

    # Display Holt-Winters predictions
    st.write("Holt-Winters Forecast:")
    st.write(hw_forecast)

    # Plot Holt-Winters forecast
    plt.figure(figsize=(10, 6))
    plt.plot(hw_forecast, label='Holt-Winters Forecast')
    plt.title('Holt-Winters Stock Forecast')
    plt.xlabel('Steps')
    plt.ylabel('Forecasted Values')
    plt.legend()
    st.pyplot(plt)

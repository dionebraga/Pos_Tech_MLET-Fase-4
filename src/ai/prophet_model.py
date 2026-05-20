from prophet import Prophet

def create_prophet_forecast(df):

    prophet_df = df.reset_index()[["Date","Close"]]

    prophet_df.columns = ["ds","y"]

    model = Prophet()

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=30)

    forecast = model.predict(future)

    return forecast
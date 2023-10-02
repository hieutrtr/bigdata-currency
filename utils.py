import plotly.graph_objects as go
import pandas as pd
import statsmodels.api as sm
import numpy as np
from pandas import DataFrame
from statsmodels.tsa.arima.model import ARIMA


def format_timeseries_data(nested_data):
    formatted_data = {}
    for date, currency_data in nested_data.items():
        for currency, value in currency_data.items():
            if currency not in formatted_data:
                formatted_data[currency] = {}
            formatted_data[currency][date] = value
    return formatted_data


def filter_timeseries_df_data_by_period(data: DataFrame, period):
    period_index = None
    if period == "Week":
        period_index = 7
    elif period == "1 Month":
        period_index = 30
    elif period == "3 Months":
        period_index = 90
    elif period == "6 Months":
        period_index = 180
    else:
        period_index = 365
    return data.tail(period_index)


def filter_timeseries_data_by_period(data, period):
    dates = list(data.keys())
    period_index = None
    if period == "Week":
        period_index = 7
    elif period == "1 Month":
        period_index = 30
    elif period == "3 Months":
        period_index = 90
    elif period == "6 Months":
        period_index = 180
    else:
        period_index = 365
    period_index = min(len(dates), period_index)
    dates = dates[-period_index:]
    filtered_data = {}
    for date in dates:
        filtered_data[date] = data[date]
    return filtered_data


def draw_multi_line_charts(st, data: DataFrame):
    data = data.set_index("Date")
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=data.index, y=data.iloc[:, 0], mode='lines+markers', name=data.columns[0],
                   yaxis='y1', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>'),
    )
    if len(data.columns) > 1:
        fig.add_trace(
            go.Scatter(x=data.index, y=data.iloc[:, 1], mode='lines+markers', name=data.columns[1],
                       yaxis='y2', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>')
        )

    fig.update_layout(
        xaxis_title='Date',
        hoverlabel=dict(
            bgcolor='white',  # Background color of hover label
            bordercolor='gray',  # Border color of hover label
            font=dict(color='black')  # Text color of hover label
        ),
        yaxis=dict(
            title=data.columns[0],
        ),

    )
    if len(data.columns) > 1:
        fig.update_layout(
            yaxis2=dict(
                title=data.columns[1],
                overlaying="y",
                side="right",
            )
        )
    return fig

    # # Regression
    # X = sm.add_constant(np.arange(len(df)))  # Independent variable (time)
    # y = df['Value']  # Dependent variable (Value)
    # model = sm.OLS(y, X).fit()
    # predicted_values = model.predict(X)
    # fig.add_trace(go.Scatter(x=df.index, y=predicted_values, mode='lines', name='Regression Model', line=dict(dash='dot')))

    # # Auto Regression
    # lag_order = 2  # Order of the autoregressive model (adjust as needed)
    # model = sm.tsa.AutoReg(df['Value'], lags=lag_order)
    # model_fit = model.fit()
    # n_forecast = 10  # Number of periods to forecast into the future
    # forecast_values = model_fit.predict(start=len(df), end=len(df) + n_forecast - 1)
    # forecast_dates = pd.date_range(start=df.index.max() + pd.DateOffset(days=1), periods=n_forecast, freq='D')
    # fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_values, mode='lines', name='Forecast', line=dict(dash='dot')))


def draw_multi_vertical_bar_charts(st, data: DataFrame):
    data = data.set_index("Date")
    fig = go.Figure()

    fig.add_trace(
        go.Bar(x=data.index, y=data.iloc[:, 0], name=data.columns[0], offsetgroup=1,
               yaxis='y1', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>'),
    )
    order = (20, 2, 3)  # Example order, you may need to tune this
    model = ARIMA(data.iloc[:, 0], order=order)
    result = model.fit()
    # Generate forecasts
    forecast_steps = len(data) // 4  # Adjust as needed
    forecast = result.get_prediction(start=order[1], end=len(data)+forecast_steps)
    fig.add_trace(
        go.Scatter(x=forecast.predicted_mean.index, y=forecast.predicted_mean, mode='lines', name="ARIMA "+data.columns[0],
                   yaxis='y1', hovertemplate='Date: %{x|%Y-%m-%d}<br>ARIMA Value: %{y:.2f}<extra></extra>'),
    )
    if len(data.columns) > 1:
        fig.add_trace(
            go.Bar(x=data.index, y=data.iloc[:, 1], name=data.columns[1], offsetgroup=2,
                   yaxis='y2', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>')
        )
        model = ARIMA(data.iloc[:, 1], order=order)
        result = model.fit()
        # Generate forecasts
        forecast_steps = len(data) // 4  # Adjust as needed
        forecast = result.get_prediction(start=order[1], end=len(data)+forecast_steps)
        fig.add_trace(
            go.Scatter(x=forecast.predicted_mean.index, y=forecast.predicted_mean, mode='lines', name="ARIMA "+data.columns[1],
                       yaxis='y2', hovertemplate='Date: %{x|%Y-%m-%d}<br>ARIMA Value: %{y:.2f}<extra></extra>'),
        )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Date',
        hoverlabel=dict(
            bgcolor='white',  # Background color of hover label
            bordercolor='gray',  # Border color of hover label
            font=dict(color='black')  # Text color of hover label
        ),
        yaxis=dict(
            title=data.columns[0],
            type='log'
        )
    )
    if len(data.columns) > 1:
        fig.update_layout(
            yaxis2=dict(
                title=data.columns[1],
                type='log',
                overlaying="y",
                side="right",)
        )
    return fig


def draw_multi_area_charts(st, data: DataFrame):
    data = data.set_index("Date")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=data.index, y=data.iloc[:, 0], mode='lines', name=data.columns[0],
                   fill='tozeroy',  # Set fill to 'tozeroy' for area below the line
                   yaxis='y1', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>'),
    )

    if len(data.columns) > 1:
        fig.add_trace(
            go.Scatter(x=data.index, y=data.iloc[:, 1], mode='lines', name=data.columns[1],
                       fill='tozeroy',
                       yaxis='y2', hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>')
        )

    fig.update_layout(
        xaxis_title='Date',
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='gray',
            font=dict(color='black')
        ),
        yaxis=dict(
            title=data.columns[0],
            type='log',
        ),
    )
    if len(data.columns) > 1:
        fig.update_layout(
            yaxis2=dict(
                title=data.columns[1],
                overlaying="y",
                side="right",
                type="log",
            )
        )
    return fig


def draw_multi_heatmap_charts(data: DataFrame):
    data = data.set_index("Date")

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(z=data.values.T, x=data.index, y=data.columns, colorscale='Viridis',
                   hovertemplate='Date: %{x|%Y-%m-%d}<br>%{y}: %{z:.2f}<extra></extra>')
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Variables',
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='gray',
            font=dict(color='black')
        ),
    )

    return fig

def draw_multi_horizontal_bar_charts(st, data: DataFrame):
    chart_figs = []

    # for currency, currency_data in data.items():
    for currency in data.columns:
        if currency == "Date":
            continue

        # Convert the data dictionary to a DataFrame
        df = data[["Date", currency]]
        df = df.set_index("Date")
        df.columns = ["Value"]
        # df.index = pd.to_datetime(df.index)

        # Create a Plotly line chart
        fig = go.Figure()

        fig.add_trace(go.Bar(x=df['Value'], y=df.index,
                      name=currency, orientation='h', hovertemplate='Date: %{y|%Y-%m-%d}<br>Value: %{x:.2f}<extra></extra>'))
        # Customize the chart layout
        fig.update_layout(
            title=f'Horizontal Bar Chart for {currency}',
            xaxis_title='Value',
            yaxis_title='Date',
            xaxis_type='log',
            hoverlabel=dict(
                bgcolor='white',  # Background color of hover label
                bordercolor='gray',  # Border color of hover label
                font=dict(color='black')  # Text color of hover label
            )
        )
        chart_figs.append(fig)

    for fig in chart_figs:
        return fig

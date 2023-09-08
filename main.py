import logging
logging.basicConfig(level=logging.INFO)

import math
import datetime as dt
import numpy as np
import yfinance as yf
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice

import bokeh
print(bokeh.__version__)

# Function to load financial data
def load_financial_data(ticker1, ticker2, start_date, end_date):
    df1 = yf.download(ticker1, start_date, end_date)
    df2 = yf.download(ticker2, start_date, end_date)
    return df1, df2

# Function to update the plot
def update_plot(data, selected_indicators, sync_x_range=None):
    df = data  # Use the loaded financial data DataFrame

    gain = df.Close > df.Open
    loss = df.Open > df.Close
    bar_width = 12 * 60 * 60 * 1000  # Half a day in milliseconds

    if sync_x_range is not None:
        plot = figure(x_axis_type="datetime", width=1000, x_range=sync_x_range)
    else:
        plot = figure(x_axis_type="datetime", width=1000)

    plot.xaxis.major_label_orientation = math.pi / 4
    plot.grid.grid_line_alpha = 0.3

    plot.segment(df.index, df.High, df.index, df.Low, color="black")
    plot.vbar(df.index[gain], bar_width, df.Open[gain], df.Close[gain], fill_color="#00ff00", line_color="#00ff00")
    plot.vbar(df.index[loss], bar_width, df.Open[loss], df.Close[loss], fill_color="#ff0000", line_color="#ff0000")

    for indicator in selected_indicators:
        if indicator == "30 Day SMA":
            df['SMA30'] = df['Close'].rolling(30).mean()
            plot.line(df.index, df.SMA30, color="purple", legend_label="30 Day SMA")
        elif indicator == "100 Day SMA":
            df['SMA100'] = df['Close'].rolling(100).mean()
            plot.line(df.index, df.SMA100, color="blue", legend_label="100 Day SMA")
        elif indicator == "Linear Regression Line":
            slope, intercept = np.polyfit(range(len(df.index.values)), df.Close.values, 1)
            y_predicted = [slope * i + intercept for i in range(len(df.index.values))]
            plot.segment(df.index[0], y_predicted[0], df.index[-1], y_predicted[-1], legend_label="Linear Regression", color="red")

    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"

    return plot


# Function to handle button click event
def on_load_button_click():
    main_stock = main_stock_input.value
    comparison_stock = comparison_stock_input.value
    start_date = start_date_picker.value
    end_date = end_date_picker.value
    selected_indicators = indicator_choice.value

    # Load financial data for main stock and comparison stock using yfinance
    main_stock_data = yf.download(main_stock, start=start_date, end=end_date)
    comparison_stock_data = yf.download(comparison_stock, start=start_date, end=end_date)

    # Update the main stock plot and comparison stock plot with the loaded data
    main_stock_plot = update_plot(main_stock_data, selected_indicators)
    comparison_stock_plot = update_plot(comparison_stock_data, selected_indicators, sync_x_range=main_stock_plot.x_range)

    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(row(main_stock_plot, comparison_stock_plot))


# Create Bokeh widgets
main_stock_input = TextInput(title="Main Stock")
comparison_stock_input = TextInput(title="Comparison Stock")
start_date_picker = DatePicker(title='Start Date', value="2020-01-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
end_date_picker = DatePicker(title='End Date', value="2020-02-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
indicator_choice = MultiChoice(options=["100 Day SMA", "30 Day SMA", "Linear Regression Line"])

load_button = Button(label="Load Data", button_type="success")
load_button.on_click(on_load_button_click)

# Create the layout
layout = column(main_stock_input, comparison_stock_input, start_date_picker, end_date_picker, indicator_choice, load_button)

# Clear Bokeh document and add the layout
curdoc().clear()
curdoc().add_root(layout)

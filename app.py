import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


goole_form_url = "https://forms.gle/nN8VEgWxShLBxHtb9"


st.title("Weekday Equity Report")
st.write("Weekday Equity Reports give you a glimpse of how equities behave on weekdays! "
         "Analysis is completely based on past data. "
         "No information on this website must be construed as investment advice.")
st.write("[SUBCRIBE NOW](%s) to access reports of all NSE500 companies. This is just a trial version."
          % goole_form_url)







paid_options = ["ADANITRANS", "NYKAA", "MUTHOOTFIN", "LICI", "IRCTC", "ADANIENT", "ITC", "HDFCBANK", "ADANIPORTS", "INFY"]

avl1= ["CHOLAFIN", "VBL","PIDILITIND","SBICARD","ADANIGREEN","ZOMATO","DMART", "BANKBARODA", "NAUKRI", "BAJFINANCE",]
avl = ["ACC","AXISBANK","M&M", "ICICIBANK", "BAJAJ-AUTO", "TATAMOTORS", "LT", "NTPC", "UPL", "BHARTIARTL", "ONGC", "RELIANCE", "HDFC", "HDFCLIFE", "BAJAJFINSV", "SBIN", "NESTLEIND", "APOLLOHOSP", "TCS", "TATASTEEL", "INDUSINDBK", "COALINDIA", "ADANIPOWER"]
avl1.extend(paid_options)
avl.extend(avl1)


avl=sorted(avl)
selected = st.selectbox('Stock', avl)

if selected in paid_options:
    st.subheader(f'[Subscribe to know about this stock!](%s) You can take a look at other companies! ' % goole_form_url)
    option = 'ICICIBANK'
else:
    option = selected


#format for yfinance data is 180d or 32d or 48d
#integer+d


days = st.radio(
    "Time Period",
    ('30 days', '60 days', '365 days'))
#days=re.findall(r'\d+', days)[0]


days = int(days.split("days")[0])






columns_to_drop = ["Dividends", "Stock Splits"]
weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def remove_time(timestamp):
    timestamp = str(timestamp)
    return timestamp.replace('00:00:00+05:30', ' ')


def date_to_day(my_date):
    """Note that there is a space after %d"""
    my_date = str(my_date)
    return dt.datetime.strptime(my_date, "%Y-%m-%d ").strftime("%a")


def date_to_indian_format(date1):
    """Note that there is a space after %d"""
    my_date = str(date1)
    return dt.datetime.strptime(date1, "%Y-%m-%d ").strftime("%B %d, %Y")



def get_data(stock_name):
    stock = yf.Ticker(stock_name)
    stock_historical = stock.history(period=str(str(days)+'d'))
    stock_historical = stock_historical.drop(columns_to_drop, axis=1)
    # Creating a Day column
    stock_historical["Day"] = stock_historical.index
    stock_historical["Temp_Date"] = stock_historical["Day"].apply(remove_time)

    stock_historical["Day"] = stock_historical["Temp_Date"].apply(date_to_day)
    stock_historical["Date"] = stock_historical["Temp_Date"].apply(date_to_indian_format)

    stock_historical["Intraday_Change"] = stock_historical["High"] - stock_historical["Open"]
    stock_historical["Close-Open"] = stock_historical["Close"] - stock_historical["Open"]
    return stock_historical


def barchart(specs_dictionary):
    chart = go.Figure(go.Bar(x=specs_dictionary['x'],
                             y=specs_dictionary['y'],

                             marker_color=specs_dictionary['marker_color'],
                             marker_line=dict(width=specs_dictionary['line_width'],
                                              color=specs_dictionary['line_color']),
                             text=specs_dictionary['text_source'],
                             textposition=specs_dictionary['textpositon']

                             ))
    chart.update_layout(title=dict(text='<b>' + specs_dictionary["title"] + '</b>',
                                   font=dict(size=23),
                                   font_family='Arial',
                                   font_color='#7E6E13'
                                   ),

                        xaxis_title=specs_dictionary["xaxis_title"],
                        yaxis_title=specs_dictionary["yaxis_title"],
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        xaxis={'fixedrange': True},
                        yaxis={'fixedrange': True}
                        )

    chart.update_xaxes(title_font_family='Arial',
                       title_font=dict(size=20))
    chart.update_yaxes(title_font_family='Arial',
                       title_font=dict(size=20))

    chart.add_hline(y=0, line_width=2, line_color="black")

    chart.update_traces(texttemplate='%{text:.3s}')

    return chart





stock_historical = get_data(str(option)+'.NS')

#############################################################################################
#last close price
#currency
currency = "₹"
lcp = stock_historical["Close"][-1:][0]
st.subheader(f"{option} : {round(lcp, 2)}")
st.write("This is the last closing price.")
################################################################################
st.title("Average Weekday Volume")
st.write(f"For the past {days} days, the average volume of {option} for each weekday is shown. Here the median is used! "
         f"This is very similar to the Average Daily Trading Volume (ADVT), however, it gives a more detailed picture of a "
         f"particular weekday's volume.")


def median_volume(d):
    vol = stock_historical[stock_historical["Day"] == d]["Volume"]
    return vol.median()

median_volumes = {}
for d in weekdays:
    median_volumes[d] = median_volume(d)

median_volumes = pd.DataFrame({'Day': median_volumes.keys(),
             'Median_Volume' : median_volumes.values()})


median_volumes_chart_specs = {'x': median_volumes['Day'],
                              'y': median_volumes['Median_Volume'],
                            'title' : f'AVERAGE WEEKDAY<br>VOLUME<br><sup>{option}',

                              # can be one color or multiple colors
                              'marker_color': '#0A7029',
                              # integer
                              'line_width': 3,
                              'line_color': '#1A4314',

                              # df column
                              'text_source': median_volumes['Median_Volume'],
                              # 'outside' or 'auto'
                              'textpositon': 'auto',

                              # strings as titles
                              'xaxis_title': 'DAY',
                              'yaxis_title': 'MEDIAN VOLUME'
                              }
st.plotly_chart(barchart(median_volumes_chart_specs), use_container_width=True)


################################################################################
# Intraday Positive Change
st.title("Average Intraday Positive Change")
st.write("What is the Average Intraday Positive Change? ")
st.write("Suppose the Average Intraday Positive Change for a stock ABCD is Rs 2, "
         "that means half the time, the positive change in price has been above Rs 2 and half the time it has been below Rs 2.")


# Intraday Positive Change
def median_intraday_change(d):
    mic = stock_historical[stock_historical["Day"] == d]["Intraday_Change"]
    return mic.median()


# Separate Loop
median_intraday_changes = {}
for d in weekdays:
    median_intraday_changes[d] = median_intraday_change(d)

# Converting the dictionary to a Pandas Series
median_intraday_changes = pd.DataFrame({'Day': median_intraday_changes.keys(),
                                        'Median Intraday Change': median_intraday_changes.values()})

median_intraday_changes["Median Intraday Change"] = median_intraday_changes["Median Intraday Change"].apply(
    lambda x: round(x, 1))

st.table(median_intraday_changes)
####################################################################################
median_intraday_changes_chart_specs = {'x': median_intraday_changes['Day'],
                                       'y': median_intraday_changes['Median Intraday Change'],
                                        'title' : f'AVERAGE INTRADAY<br>POSITIVE CHANGE<br><sup>{option}</sup>',

                                       # can be one color or multiple colors
                                       'marker_color': '#0A7029',
                                       # integer
                                       'line_width': 3,
                                       'line_color': '#1A4314',

                                       # df column
                                       'text_source': median_intraday_changes['Median Intraday Change'],
                                       # 'outside' or 'auto'
                                       'textpositon': 'auto',

                                       # strings as titles
                                       'xaxis_title': 'DAY',
                                       'yaxis_title': 'MEDIAN INTRADAY CHANGE'
                                       }
st.plotly_chart(barchart(median_intraday_changes_chart_specs), use_container_width=True)

###################################################################################
def one_way(rise_or_fall):
    display_columns = ["Date", "Day", "Open", "High", "Low"]

    if rise_or_fall == 'Rise':
        condition_for_table = stock_historical['Open'] == stock_historical["Low"]
        only = stock_historical[condition_for_table][display_columns].set_index('Date')

        only["Absolute"] = round(only["High"] - only["Open"], 2)
        only["%"] = round((only["Absolute"] / only["Open"]) * 100, 2)

        only = only.drop(["Open", "High", "Low"], axis=1)
        if only.empty: print("NO DATA!")
        return only

    elif rise_or_fall == 'Fall':
        condition_for_table = stock_historical['Open'] == stock_historical["High"]
        only = stock_historical[condition_for_table][display_columns].set_index('Date')

        only["Absolute"] = round(only["Low"] - only["Open"], 2)
        only["%"] = round((only["Absolute"] / only["Open"]) * 100, 2)

        only = only.drop(["Open", "High", "Low"], axis=1)
        if only.empty: print("NO DATA!")
        return only


st.title(f"When {option} Only Fell")
st.write(f"Listed below are the days when the {option} stock price only kept falling. "
         f"On these days, it never went above the opening price. This data is for the past {days} days.")
st.table(one_way("Fall"))

st.title(f"When  {option} Only Rose")
st.write(f"Listed below are the days when the {option} stock price only rose. "
         f"On these days, it never went below the opening price. This data is for the past {days} days.")
st.table(one_way("Rise"))

###########################################################################
def close_status(close):
    def weekday_rise_or_fall_probability(d, close):
        prob = stock_historical[stock_historical["Day"] == d]
        if close == 'High':
            prob_condition = prob["Close-Open"]>0
        elif close == 'Low':
            prob_condition = prob["Close-Open"]<0
        return str(prob[prob_condition].count()[0])+str('/')+str(prob.count()[0])

    probabilities = {}
    for d in weekdays:
        probabilities[d] = weekday_rise_or_fall_probability(d, close)


    probabilities = pd.DataFrame({'Day' : probabilities.keys(),
                                 'Chances' : probabilities.values(),
                                 #'Chances(%)' : probabilities.values()
                                 })

    probabilities["Chances"] = probabilities["Chances"]
    return probabilities


st.title(f"How Many Times Did {option} Close High")
st.write(f"On how many Mondays did the price of {option} close higher than the opening price? "
         f"Similary, listed below is the data for all days.")
st.table(close_status("High"))

st.title(f"How Many Times Did {option} Close Low")
st.write(f"On how many Mondays did the price of {option} close lower than the opening price? "
         f"Similary, listed below is the data for all days.")
st.table(close_status("Low"))





#####################################################
st.session_state.horizontal = True
chosen_day = st.radio("Day",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        horizontal=st.session_state.horizontal)

#past_days = past_particular_weekday(chosen_day[:3])

#############################################
no_of_previous_weekdays = st.slider(f'Number of previous weekdays',
                                    2, 5, 4)
#############################################################################################
def past_particular_weekday(d):
    day_condition = stock_historical["Day"]==d

    past = stock_historical[day_condition][-no_of_previous_weekdays:][["Day", "Date", "Close-Open"]]
    past["Close-Open"] = past["Close-Open"].apply(lambda x: round(x, 2))
    #past["Day"] = past["Day"].apply(lambda x: dt.datetime.strptime(x, "%a").strftime("%A"))

    past["Color"] = np.where(past["Close-Open"]<0, 'red', '#0A7029')
    past["Day"] = past["Date"].apply(lambda x: dt.datetime.strptime(x, "%B %d, %Y").strftime("%A"))
    return past

###################################################
past_days = past_particular_weekday(chosen_day[:3])
###############################################


past_days_chart_specs = {'x': past_days['Date'],
                         'y': past_days['Close-Open'],
                         'title': f'HOW MUCH DID<br>{option} RISE OR FALL?<br><sup>{currency}',

                         # can be one color or multiple colors
                         'marker_color': past_days["Color"],
                         # integer
                         'line_width': 2,
                         'line_color': 'black',

                         # df column
                         'text_source': past_days['Close-Open'],
                         # 'outside' or 'auto'
                         'textpositon': 'auto',

                         # strings as titles
                         'xaxis_title': f'PREVIOUS {(past_days["Day"][0]).upper()}S',
                         'yaxis_title': 'RISE OR FALL'
                         }

st.plotly_chart(barchart(past_days_chart_specs), use_container_width=True)

st.subheader(f'[Subscribe Now!](%s)' % goole_form_url)
st.write(f'To see more previous {past_days["Day"][0]}s.')

import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf

openai.api_key = open('API_KEY', 'r').read()

def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period='1y').iloc[-1].Close)

def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    return str(data.rolling(window=window).mean().iloc[-1])

def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1])


def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14-1, adjust=False).mean()
    ema_down = down.ewm(com=14-1, adjust=False).mean()
    rs = ema_up / ema_down
    return str(100 - (100 / (1+rs)).iloc[-1])

def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal

    return f'{MACD[-1]}, {signal[-1]}, {MACD_histogram[-1]}'


def get_dividend_yield(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    if "dividendYield" in info and info["dividendYield"]:
        return f'{info["dividendYield"] * 100:.2f}%'
    else:
        return "No dividend yield information available."

def plot_moving_averages(ticker):
    short_window=20
    long_window=50
    data = yf.Ticker(ticker).history(period='1y')
    data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
    
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Stock Price', alpha=0.8)
    plt.plot(data.index, data['SMA_short'], label=f'{short_window}-Day SMA', alpha=0.8)
    plt.plot(data.index, data['SMA_long'], label=f'{long_window}-Day SMA', alpha=0.8)
    
    plt.title(f'{ticker} Stock Price and Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig('moving_averages.png')
    plt.close()


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    plt.figure(figsize=(10,5))
    plt.plot(data.index, data.Close)
    plt.title(f'{ticker} Stock Price YTD')
    plt.xlabel('Date')
    plt.grid(True)
    plt.savefig('stock.png')
    plt.close()



functions = [
    {
        'name': 'get_stock_price',
        'description': 'Gets the latest stock price given the ticker symbol of a company.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
    {
        'name': 'calculate_SMA',
        'description': 'Calculate the simple moving average for a given stock ticker and a window.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
                'window': {
                    'type': 'integer',
                    'description': 'The timeframe to consider when calculating the SMA'
                },
            },
            'required': ['ticker', 'window']
        },
    },
    {
        'name': 'calculate_EMA',
        'description': 'Calculate the exponential moving average for a given stock ticker and a window.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
                'window': {
                    'type': 'integer',
                    'description': 'The timeframe to consider when calculating the EMA'
                },
            },
            'required': ['ticker', 'window']
        },
    },
    {
        'name': 'calculate_RSI',
        'description': 'Calculate the RSI for a given ticker symbol of a company.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
    {
        'name': 'calculate_MACD',
        'description': 'Calculate the MACD for a given stock ticker.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
    {
        'name': 'get_dividend_yield',
        'description': 'Calculates and returns the dividend yield of a stock for a given stock ticker.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
    {
        'name': 'plot_moving_averages',
        'description': 'Generates a plot of the stocks price along with its SMA over two different windows for a given stock ticker.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
    {
        'name': 'plot_stock_price',
        'description': 'Plot the stock price for the last year given the ticker symbol of a company.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (example: AAPL is for Apple).'
                },
            },
            'required': ['ticker']
        },
    },
]



available_functions = {
    'get_stock_price': get_stock_price,
    'calculate_SMA': calculate_SMA,
    'calculate_EMA': calculate_EMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
    'get_dividend_yield': get_dividend_yield,
    'plot_moving_averages': plot_moving_averages,
    'plot_stock_price': plot_stock_price
}

if 'message' not in st.session_state:
    st.session_state['messages'] = []

st.title('Stock Analysis Chatbot')

user_input = st.text_input('Your input:')

if user_input:
    try:
        st.session_state['messages'].append({'role': 'user', 'content': f'{user_input}'})

        response = openai.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages=st.session_state['messages'],
            functions=functions,
            function_call='auto'
        )
        response_message = response.choices[0].message

        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            args_dict = {'ticker': function_args.get('ticker')}
            if function_name in ['calculate_EMA', 'calculate_SMA']:
                args_dict['window'] = function_args.get('window')

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)

            if function_name in ['plot_stock_price', 'plot_moving_averages']:
                st.image('stock.png' if function_name == 'plot_stock_price' else 'moving_averages.png')
            else:
                # st.session_state['messages'].append(response_message)
                st.session_state['messages'].append(
                    {
                        'role': 'function',
                        'name': function_name,
                        'content': function_response
                    }
                )
                second_response = openai.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=st.session_state['messages']
                )
                st.text(second_response.choices[0].message.content)
                st.session_state['messages'].append({'role': 'assistant', 'content': second_response.choices[0].message.content})
        else:
            st.text(response_message.content)
            st.session_state['messages'].append({'role': 'assistant', 'content': response_message.content})
    except Exception as e:
        raise e
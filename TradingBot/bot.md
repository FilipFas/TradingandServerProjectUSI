# Bollinger-RSI Convergence Strategy

## Technical Analysis

Technical analysis is a method used to evaluate and predict the future price movements of financial assets, such as stocks, commodities, and currencies, by analyzing past market data, primarily price and volume. Unlike fundamental analysis, which focuses on a company's financial health and economic factors, technical analysis looks for patterns and trends in the historical price data to identify trading opportunities.

## Introduction

This trading strategy utilizes two main tools: Bollinger Bands and the Relative Strength Index (RSI). The strategy relies on signals that occur simultaneously from both indicators to make buy and sell decisions.

## Bollinger Bands

Bollinger Bands consist of three lines:
1. **Upper Band:** represents the high price level.
2. **Middle Band:** is the average price.
3. **Lower Band:** represents the low price level.

When the price of a stock touches the upper band, it means it is relatively high; when it touches the lower band, it means it is relatively low.

## RSI (Relative Strength Index)

The RSI is a number ranging from 0 to 100 that indicates whether a stock is "overbought" or "oversold":
- **RSI above 70:** the stock is overbought (price is too high).
- **RSI below 30:** the stock is oversold (price is too low).

## Strategy Rules

### Entering a Long Position (Buy)

Buy the stock **when** the price touches the lower Bollinger Band **and simultaneously** the RSI is below 30 (indicating the price is very low and may rise).

### Exiting a Long Position (Sell)

Sell the stock **when** the price touches the upper Bollinger Band **and simultaneously** the RSI is above 70 (indicating the price is very high and may fall).

### Entering a Short Position (Sell Short)

Sell short (i.e., sell a stock you do not own) **when** the price touches the upper Bollinger Band **and simultaneously** the RSI is above 70 (indicating the price is very high and may fall).

### Exiting a Short Position (Buy to Cover)

Buy to cover the stock **when** the price touches the lower Bollinger Band **and simultaneously** the RSI is below 30 (indicating the price is very low and may rise).

## Practical Example

### Buy

If the price of a stock drops and touches the lower Bollinger Band and simultaneously the RSI is below 30, it means the stock is likely undervalued. In this case, we buy the stock. We hold the stock until the price touches the upper Bollinger Band and simultaneously the RSI exceeds 70. At this point, we sell the stock because the price is likely overvalued.

### Sell Short

If the price of a stock rises and touches the upper Bollinger Band and simultaneously the RSI is above 70, it means the stock is likely overvalued. In this case, we sell the stock short. We hold the short position until the price touches the lower Bollinger Band and simultaneously the RSI falls below 30. At this point, we buy to cover the stock because the price is likely undervalued.

## Comment on the strategy

This strategy combines two technical analysis indicators to make buy and sell decisions based on signals that occur simultaneously. By using Bollinger Bands and RSI, we can identify moments when a stock's price is too high or too low, allowing us to enter and exit the market in a more informed and potentially profitable manner.

## How to Use the Bot



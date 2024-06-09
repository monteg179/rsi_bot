from pandas import (
    DataFrame,
    Series,
)
import pandas_ta


def rsi(close: Series, length: int = 14) -> DataFrame:
    return pandas_ta.rsi(close, length)


def volatility(
    high: Series,
    low: Series,
    close: Series,
    length: int = 14
) -> DataFrame:
    return pandas_ta.atr(high, low, close, length)


def flats(
    close: Series,
    max_difference: float,
    min_length: int = 4,
) -> list[tuple[int, int]]:
    result = []
    first = 0
    value = close.iloc[first]
    high = value * (1.0 + max_difference / 100.0)
    low = value * (1.0 - max_difference / 100.0)
    for index in range(1, len(close)):
        current = close.iloc[index]
        if current < low or current > high:
            if index - first >= min_length:
                result.append((first, index))
            first = index
            high = current * (1.0 + max_difference / 100.0)
            low = current * (1.0 - max_difference / 100.0)
    else:
        if index - first >= min_length:
            result.append((first, index))
    return result


def poc_val_vah(
    high: Series,
    low: Series,
    volume: Series,
    va: float = 68.0
) -> dict[str, float]:
    threshold = volume.sum() * va / 100.0
    total = 0.0
    sorted = volume.sort_values(inplace=False, ascending=False)
    for number in range(len(sorted)):
        value = sorted.iloc[number]
        total += value
        if total >= threshold:
            sorted = sorted[:number]
            break
    first = sorted.index[0]
    poc = (high.loc[first] + low.loc[first]) / 2
    val = low.loc[first]
    vah = high.loc[first]
    for number in range(1, len(sorted)):
        index = sorted.index[number]
        low_value = low.loc[index]
        high_value = high.loc[index]
        if low_value < val:
            val = low_value
        if high_value > vah:
            vah = high_value
    return {
        'poc': poc,
        'val': val,
        'vah': vah,
    }


def trend(high: Series, low: Series, close: Series, length: int = 14) -> int:
    indicator = pandas_ta.adx(high[:-4], low[:-4], close[:-4], length)
    value = indicator.iloc[-1]
    pos = value[f'DMP_{length}']
    neg = value[f'DMN_{length}']
    if pos > neg:
        threshold = low.iloc[-4]
        if (close.iloc[-3] < threshold and close.iloc[-2] < threshold and
                close.iloc[-1] < threshold):
            return -1
    if neg > pos:
        threshold = high.iloc[-4]
        if (close.iloc[-3] > threshold and close.iloc[-2] > threshold and
                close.iloc[-1] > threshold):
            return 1
    return 0

import csv
import sys

def get_profitable_trade(records):
    """
    Generate a trade from a list of historical data.

    This function accept a list of dictionary containing the minutes and price
    ex. [{ 'mins': 94, 'price': 1.2 }]

    It will attempt to generate a profitable trade by sorting the given records base on price in descending order
    then it will use the last item as the buying point and will start looking at the beginning of the sorted data
    for the selling point.

    It will follow the minimum 30 minutes and less than 60 minutes trade duration.
    The first comparison that matches the duration critera will be the trade and will be returned by this function.
    This function may return None if nothing passed the duration criteria.
    """
    trade = None
    sorted_records = sorted(records, key=lambda item: item['price'], reverse=True)
    while not trade:
        lowest_record = sorted_records.pop()
        if not sorted_records:
            break
        for highest_record in sorted_records:
            time_diff = highest_record['mins'] - lowest_record['mins']
            if time_diff >= 30 and time_diff < 60:
                trade = {
                    'open': lowest_record,
                    'close': highest_record,
                    'profit': highest_record['price'] - lowest_record['price'],
                    'duration': highest_record['mins'] - lowest_record['mins']
                }
                break
    return trade

def get_best_trades(csv_file):
    """
    This function accepts a csv reader object and will loop thru its content.
    """
    records = []
    trades = []
    for row in csv_file:

        minutes = int(row[0])
        # gather 30+ records of historical data to start a profitable trade
        records.append({
            'mins': int(row[0]),
            'price': float(row[1])
        })

        # it will start creating a profitable trade for every 30 records
        # I decided to do it every 30 records because I think
        # I could do more transactions and maximize the total profit with that
        if minutes and minutes % 30 == 0:
            trade = get_profitable_trade(records)
            # the returned object maybe None, meaning it didn't find a profitable trade within the set of records
            # if the return is None, it will continue on using the records and add it to the next set of records of the next iteration
            if trade:
                trades.append(trade)
                # after finding a profitable trade it will reuse those records that minutes is later than the selling point
                # if the selling point is the last item in the records then it will just clear the records
                records = records[records.index(trade['close']) + 1:]

    # this is just to cover the last items from the csv file
    if len(records) > 1:
        trade = get_profitable_trade(records)
        if trade:
            trades.append(trade)

    return trades

with open(sys.argv[1]) as file:

    reader = csv.reader(file)
    # skip the column name
    next(reader, None)

    total_profit = 0
    trades = get_best_trades(reader)
    # this another loop can be prevented but for the sake of demonstrating how I decouple the function base on task/role and reusability
    # I decided to make a function that return a list of profitable trades instead
    for trade in trades:
        total_profit += trade['profit']
        print(
            'open at ' + str(trade['open']['mins']) + ' ( ' + str(trade['open']['price']) + ' ), ' + \
            'close at ' + str(trade['close']['mins']) + ' ( ' + str(trade['close']['price']) + ' ), ' + \
            'duration = ' + str(trade['duration']) + ', ' + \
            'profit = ' + ('%.16f' % trade['profit'])
        )

    print()
    print('Total profit = ' + str(total_profit))

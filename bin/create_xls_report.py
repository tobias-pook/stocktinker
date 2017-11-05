#!/bin/env python
import argparse

from stocktinker.stock import Stock
import openpyxl as xls

def main():
    parser = argparse.ArgumentParser(description='Create xls reports based on stock symbol')
    parser.add_argument('stock_symbols', nargs="+")

    args = parser.parse_args()
    out = []
    wb = xls.Workbook(write_only=True)
    ws = wb.create_sheet("summary")
    ws.append(Stock.get_summary_header_row())
    # print ("{0:<12} {0:<14} {0:<14} {0:<14} {0:<22} {0:<20} ".format(*out[0]))
    for symbol in args.stock_symbols:
        split = symbol.split(":")
        if len(split) > 1:
            symbol, currency = split [0], split[1]
        else:
            currency="usd"
        stock = Stock(symbol, currency=currency)
        stock.write_xls_report()
        stock.plot_growth_ratios()
        ws.append(stock.get_summary_row())
    wb.save("analysis_report.xlsx")

if __name__ == '__main__':
    main()

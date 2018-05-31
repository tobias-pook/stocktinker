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
    for symbol in args.stock_symbols:
        stock = Stock(symbol)
        stock.write_xls_report()
        stock.plot_growth_ratios()
        ws.append(stock.get_summary_row())
        print(list(stock.ratios.keys()))
        print(stock.ratios['short-term-debt'])
        # print(stock.ratios.head(1))
    # wb.save("analysis_report.xlsx")

if __name__ == '__main__':
    main()

class StockFilter():
    ''' Base class for filters with required functions '''
    name = "stock-filter"

    def check(self, df):
        return True

class MeanRevenueFilter(StockFilter):

    def __init__(self, name='test-filter'):
        self.name = name

    def check(self, df):
        if df.ratios['revenue-usd'].mean() < 1000009:
            return False
        return True

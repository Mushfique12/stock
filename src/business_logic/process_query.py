import configparser
import logging

import joblib

from src.IO.get_data_from_yahoo import get_last_stock_price
from src.IO.storage_tools import create_bucket, get_model_from_bucket, upload_file_to_bucket
from src.algo.dummy_model import Stock_model

# Create an Object of
def create_business_logic():
    data_fetcher = get_last_stock_price #data_fetcher contains a panda dataframe
    return BusinessLogic(Stock_model(data_fetcher))


class BusinessLogic:

    def __init__(self, model_creator):
        self._root_bucket = 'model_bucket_ycng_228'
        self._config = configparser.ConfigParser()
        self._config.read('application.conf')
        self._model_creator = model_creator
        self._create_bucket()

    def get_version(self):
        return self._config['DEFAULT']['version']

    def get_myName(self):
        return self._config['DEFAULT']['myName']

    def get_bucket_name(self):
        return f'{self._root_bucket}_{self.get_version().replace(".", "")}{self.get_myName()}'

    def _get_or_create_model(self, ticker):
        log = logging.getLogger()
        model_filename = self.get_model_filename_from_ticker(ticker)
        model = get_model_from_bucket(model_filename, self.get_bucket_name())
        if model is None:
            log.warning(f'training model for {ticker}')
            model = self._model_creator.fit(ticker)
            with open(model_filename, 'wb') as f:
                joblib.dump(model, f)
            upload_file_to_bucket(model_filename, self.get_bucket_name())
        return model

    def get_model_filename_from_ticker(self, ticker):
        return f'{ticker}.pkl'

    def _create_bucket(self):
        bucket = self.get_bucket_name()
        print(bucket)
        create_bucket(self.get_bucket_name())


    def do_predictions_for(self, ticker):
        model = self._get_or_create_model(ticker)
        predictions = model.predict(ticker)
        return predictions

if __name__ == '__main__':
    business_logic = create_business_logic()
    business_logic.get_bucket_name()
    print(business_logic.get_bucket_name())
    print("hello")
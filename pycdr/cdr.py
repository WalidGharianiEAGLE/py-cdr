import operator
import requests
from typing import List
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

class CDRApi:
    _VALID_DATASETS = {'AVHRR_VIIRS_NDVI_V5', 'AVHRR_LAI_FAPAR_V5'}

    def __init__(self, start_date: str, end_date: str, dataset: str):
        self.start_date = start_date
        self.end_date = end_date 
        self.dataset = dataset
        self.dataset_urls = []
        self.dataset_info = {}

    def _generate_date_range(self) -> List[str]:
        dates_period = []
        current_date = self.start_date
        while current_date <= self.end_date:
            dates_period.append(current_date.strftime('%Y%m%d'))
            current_date += timedelta(days=1)
        return dates_period

    def _connect_thredds(self, year: int) -> BeautifulSoup:
        if self.dataset not in self._VALID_DATASETS:
            raise ValueError(f'Invalid dataset: {self.dataset}')
        noaa_thredds = f'https://www.ncei.noaa.gov/thredds/catalog/cdr/ndvi/{year}/catalog.html'
        try:
            page = requests.get(f"{noaa_thredds}")
        except requests.RequestException as e:
            raise 
        return BeautifulSoup(page.content, 'html.parser')  

    def query(self, return_urls=False) -> List[str]:
        base_url = 'https://www.ncei.noaa.gov/thredds/dodsC/cdr/ndvi/'
        data_urls = []
        start_year = self.start_date.year
        end_year = self.end_date.year

        for year in range(start_year, end_year + 1):
            soup = self._connect_thredds(year)
            nc_links = [link.text.strip() for link in soup.select('a') if 'nc' in link.text]
            date_range = self._generate_date_range()
            nc_valid = [n for n in nc_links if any(date in n for date in date_range)]
            year_urls = [f'{base_url}{year}/{id}' for id in nc_valid]
            data_urls.extend(year_urls)
        self.dataset_urls = data_urls
        if return_urls:
            return data_urls
        
    def _parse_das_content(self, das_content: str, data_id: str):
        attributes = {}
        lines = das_content.split('\n')
        current_attribute = None
        current_properties = {}

        for line in lines:
            if not line.strip():
                continue
                
            if line.strip().endswith('{'):
                if current_attribute is not None:
                    attributes.setdefault(data_id, {})[current_attribute] = current_properties
                current_attribute = line.strip().split()[0]
                current_properties = {}

            elif '"' in line:
                key, value = line.strip().split('"')[0].strip(), line.strip().split('"')[1]
                current_properties[key] = value

        if current_attribute is not None:
            attributes.setdefault(data_id, {})[current_attribute] = current_properties

        return attributes

    def info(self, return_info=False):
        ids = [url.split('/')[-1][:-3] for url in self.dataset_urls]
        all_attributes_dict = {}
        for url, id_ in zip(self.dataset_urls, ids):
            das_url = f'{url}.das'
            response = requests.get(das_url)
            das_content = response.text
            attributes = self._parse_das_content(das_content, id_)
            all_attributes_dict[id_] = attributes
            
            self.dataset_info = all_attributes_dict
        if return_info:
            return all_attributes_dict
    
    start_date =  property(operator.attrgetter('_start_date'))
    @start_date.setter
    def start_date(self, value):
        try:
            date = datetime.strptime(value, '%Y-%m-%d')
            self._start_date = date
        except Exception as e:
            raise TypeError(f"'start_date' must be a string in a '%Y-%m-%d' format") from e
    
    end_date =  property(operator.attrgetter('_end_date'))
    @end_date.setter
    def end_date(self, value):
        try:
            date = datetime.strptime(value, '%Y-%m-%d')
            self._end_date = date
        except Exception as e:
            raise TypeError(f"'end_date' must be a string in a '%Y-%m-%d' format") from e

    
    dataset_urls =  property(operator.attrgetter('_dataset_urls'))
    @dataset_urls.setter
    def dataset_urls(self, value):
        if not isinstance(value, list):
            raise AttributeError (f'dataset_urls must be a list')
        self._dataset_urls = value

    dataset_info =  property(operator.attrgetter('_dataset_info'))
    @dataset_info.setter
    def dataset_info(self, value):
        if not isinstance(value, dict):
            raise AttributeError (f'dataset_info must be a dict')
        self._dataset_info = value
    
    @classmethod
    def from_dict(cls, dict_args):
        return cls(**dict_args)
    
    def is_available(self, url) -> bool:
        return url in self.dataset_urls

    def __repr__(self) -> str:
        return f"CDRApi(start_date={self.start_date}, end_date={self.end_date}, dataset='{self.dataset}')"

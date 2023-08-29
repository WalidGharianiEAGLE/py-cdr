from typing import List
import requests
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup

class CDRApi:
    _VALID_DATASETS = {'AVHRR_VIIRS_NDVI_V5', 'AVHRR_LAI_FAPAR_V5'}

    def __init__(self, start_date: str, end_date: str, dataset: str):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.dataset = dataset
        self.day_range = timedelta(days=1)
        self._data_ids = []
        self._dataset_urls = []

    def _generate_date_range(self) -> List[str]:
        dates_period = []
        current_date = self.start_date
        while current_date <= self.end_date:
            dates_period.append(current_date.strftime('%Y%m%d'))
            current_date += self.day_range
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

    def get_urls(self) -> List[str]:
        base_url = 'https://www.ncei.noaa.gov/thredds/dodsC/cdr/ndvi/'
        data_urls = []
        self._dataset_urls.clear()
        start_year = self.start_date.year
        end_year = self.end_date.year

        for year in range(start_year, end_year + 1):
            soup = self._connect_thredds(year)
            nc_links = [link.text.strip() for link in soup.select('a') if 'nc' in link.text]
            date_range = self._generate_date_range()
            nc_valid = [n for n in nc_links if any(date in n for date in date_range)]
            self._data_ids.extend([n.strip('.nc') for n in nc_valid])
            year_urls = [f'{base_url}{year}/{id}' for id in nc_valid]
            data_urls.extend(year_urls)
        self._dataset_urls = data_urls
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

    def get_info(self):
        all_attributes_dict = {}

        for url, id_ in zip(self._dataset_urls, self._data_ids):
            das_url = f'{url}.das'
            response = requests.get(das_url)
            das_content = response.text
            attributes = self._parse_das_content(das_content, id_)
            all_attributes_dict[id_] = attributes

        return all_attributes_dict

    def is_available(self, data_id: str) -> bool:
        return data_id in self._data_ids

    def __repr__(self) -> str:
        return f"CDRApi(start_date={self.start_date}, end_date={self.end_date}, dataset='{self.dataset}')"

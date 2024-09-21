import requests
from typing import List
from datetime import datetime

from bs4 import BeautifulSoup

from pycdr.datasets import Datasets
from pycdr.utils import generate_date_range


class DateDescriptor:
    """ Descriptor for managing date attributes."""

    def __init__(self, param) -> None:
        self.param = param
        
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.param]
    
    def __set__(self, obj, val):
        try:
            date = datetime.strptime(val, '%Y-%m-%d')
            obj.__dict__[self.param] = date
        except Exception as e:
            raise ValueError(f"{self.param} must be a string in a '%Y-%m-%d' format") from e
        

class CDRApi:
    """
    An API for accessing climate data records.

    Args:
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        dataset (str): The dataset name, should match Datasets enum.

    Attributes:
        start_date (datetime): The start date as a datetime object.
        end_date (datetime): The end date as a datetime object.
        dataset (str): The dataset name.
        dataset_urls (list): List of URLs for dataset access.
        dataset_info (dict): Dictionary containing dataset information.
    """
    
    start_date = DateDescriptor("start_date")
    end_date = DateDescriptor("end_date")

    def __init__(self, start_date: str, end_date: str, dataset: Datasets):
        self.start_date = start_date
        self.end_date = end_date
        if not isinstance(dataset, Datasets):
            raise ValueError("Dataset must be an instance of Datasets Enum.")
        self.dataset = dataset
        self._dataset_urls = []
        self._dataset_info = {}

    def _connect_thredds(self, year: int) -> BeautifulSoup:
        base_url = Datasets.get_url(self.dataset).replace('/dodsC', '')
        
        urls = [
            f"{base_url}{year}/catalog.html",            # Primary format
            f"{base_url}/files/{year}/catalog.html"      # Fallback format
        ]
        
        def try_request(url):
            try:
                page = requests.get(url)
                page.raise_for_status() 
                return page, None
            except requests.RequestException as e:
                return None, e
        
        for url in urls:
            page, error = try_request(url)
            if page:  
                return BeautifulSoup(page.content, 'html.parser')
        
        raise ConnectionError(f"Could not connect to any URL for year {year}. Errors: {error}")


    def query(self, return_urls=False) -> List[str]:
        base_url = Datasets.get_url(self.dataset)
        data_urls = []
        start_year = self.start_date.year
        end_year = self.end_date.year

        for year in range(start_year, end_year + 1):
            soup = self._connect_thredds(year)
            nc_links = [link.text.strip() for link in soup.select('a') if 'nc' in link.text]            
            date_range = generate_date_range(self.start_date, self.end_date)  
            nc_valid = [n for n in nc_links if any(date in n for date in date_range)]
            year_urls = [f'{base_url}{year}/{id_}' for id_ in nc_valid]
            data_urls.extend(year_urls)

        self._dataset_urls = data_urls
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
    
    def info(self, url_id=None, return_info=False):
        if url_id is None:
            ids = [url.split('/')[-1][:-3] for url in self._dataset_urls]
        else:
            ids = [url_id]

        all_attributes_dict = {}
        for url, id_ in zip(self._dataset_urls, ids):
            das_url = f'{url}.das'
            try:
                response = requests.get(das_url)
                response.raise_for_status()
            except requests.RequestException as e:
                raise ConnectionError(f"Could not fetch DAS for {url}: {e}")

            das_content = response.text
            attributes = self._parse_das_content(das_content, id_)
            all_attributes_dict[id_] = attributes
        
        self._dataset_info = all_attributes_dict
        if return_info:
            return all_attributes_dict
        
    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, val):
        if not isinstance(val, Datasets):
            raise ValueError(f"Invalid dataset: {val}. Must be an instance of the Datasets enum.")
        self._dataset = val

    @property
    def dataset_urls(self):
        return self._dataset_urls

    @property
    def dataset_info(self):
        return self._dataset_info
    
    @classmethod
    def from_dict(cls, dict_args):
        return cls(**dict_args)

    def is_available(self, url) -> bool:
        return url in self.dataset_urls

    def __repr__(self) -> str:
        return f"CDRApi(start_date={self.start_date}, end_date={self.end_date}, dataset={self.dataset.name})"
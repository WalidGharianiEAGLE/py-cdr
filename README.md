# pycdr - Climate Data Records API

This is a small project in progress. pycdr provides an API for accessing climate data records from the National Centers for Environmental Information (NCEI) hosted datasets. With pycdr, you can easily query datasets, retrieve dataset URLs, and access dataset information.

This is a MVP that provides some dataset to retrieve: 

- [x] AVHRR and VIIRS NDVI
- [x] Leaf Area Index & Fraction of Absorbed Photosynthetically Active Radiation (LAI FAPAR)/
- [ ] Add more dataset (Incomplete)

## Installation

CDRApi will be installed using pip

## Usage

```python
from pyscdr.cdr import CDRApi

# Create an instance of CDRApi
api = CDRApi(start_date='2022-01-01', end_date='2022-01-10', dataset='AVHRR_VIIRS_NDVI_V5')

# Query data and retrieve URLs
api.query(return_urls=False)

# Display the saved dataset URLs
print("Dataset URLs:")
for url in api.dataset_urls:
    print(url)
# Retrieve dataset information
infos = api.info(return_info=True)
infos

# Check if a specific URL is available
url_to_check = 'https://www.ncei.noaa.gov/thredds/dodsC/cdr/ndvi/2022/VIIRS-Land_v001-preliminary_NPP13C1_S-NPP_20220101_c20220419212429.nc'
if api.is_available(url_to_check):
    print(f"{url_to_check} is available.")
else:
    print(f"{url_to_check} is not available.")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the National Centers for Environmental Information (NCEI) for hosting the datasets used by this API.

---
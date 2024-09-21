# py-cdr - Climate Data Records API

This is a small project in progress. pycdr provides an API for accessing climate data records from the National Centers for Environmental Information (NCEI) hosted datasets. With pycdr, you can easily query datasets, retrieve dataset URLs, and access dataset information.

This is a MVP that provides some dataset to retrieve: 

- [x] [AVHRR](https://doi.org/10.7289/V5ZG6QH9) and [VIIRS](https://doi.org/10.25921/gakh-st76) Normalized Difference Vegetation Index (NDVI)
- [x] [AVHRR](https://doi.org/10.7289/V5TT4P69) and [VIIRS](https://doi.org/10.25921/9x3m-0e02) Leaf Area Index & Fraction of Absorbed Photosynthetically Active Radiation (LAI FAPAR)
- [x] [AVHRR](https://doi.org/10.7289/V53776Z4) and [VIIRS](https://doi.org/10.25921/e86y-fe34) Surface Reflectance.
- [x] [AVHRR Daily and Monthly Aerosol Optical Thickness (AOT)](https://doi.org/10.25921/w3zj-4y48)
- [x] [Pecipitation - PERSIANN CDR](http://doi.org/10.7289/V51V5BWQ)
- [x] [GRIDSAT-B1 Geostationary IR Channel Brightness Temperature](https://doi.org/10.7289/V59P2ZKR)
- [x] [Sea Surface Temperature - WHOI, Version 2](http://doi.org/10.7289/V5FB510W)
- [x] [Ocean Heat Fluxes; SeaFlux OSB CDR: Heat Fluxes, Version 2](http://doi.org/10.7289/V59K4885)
- [x] [Sea Ice Concentration](https://doi.org/10.7265/efmz-2t65)
- [ ] Add more dataset (Incomplete)

## Installation.

pycdr will be installed using pip

## Usage

```python
from pycdr.cdr import CDRApi
from pycdr.datasets import Datasets

# Create an instance of CDRApi
api = CDRApi(start_date='2022-01-01', end_date='2022-01-10', dataset=Datasets.AVHRR_VIIRS_NDVI_V5)

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

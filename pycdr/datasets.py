from enum import Enum

class Datasets(Enum):
    AVHRR_VIIRS_NDVI_V5 = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/ndvi/"
    AVHRR_LAI_FAPAR_V5 = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/lai/"
    AVHRR_VIIRS_SURFACE_REFLECTANCE = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/surface-reflectance/"
    AVHHR_AOT_DAILY = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/avhrr-aot-daily/"
    PERSIANN = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/persiann/"
    GRIDSAT = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/gridsat/"
    SEA_SURFACE_TEMP_WHOI = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/sea-surface-temp-whoi/"
    OCEAN_HEAT_FLUXES = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/ocean-heat-fluxes/"
    SEA_ICE_CONCENTRATION = "https://www.ncei.noaa.gov/thredds/dodsC/cdr/sea-ice-concentration/"

    @classmethod
    def list_datasets(cls):
        return [dataset.name for dataset in cls]

    @classmethod
    def get_url(cls, dataset):
        if isinstance(dataset, cls):
            return dataset.value
        raise ValueError(f"Invalid dataset: {dataset}. Use one of {cls.list_datasets()}.")


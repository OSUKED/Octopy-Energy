# Octopy-Energy

![svg](docs/img/alt_logo.png){:height="50%" width="50%"}

Python client for the Octopus energy API. You can visit the documentation by clicking <a href="ayrtonb.github.io/octopy-energy">here</a>

<br>

### Installing Octopy-Energy

The first step to getting running with the library is to install it through pip.


```python
! pip install octopyenergy
```
    Requirement already satisfied: octopyenergy in c:\users\user\path\to\octopy-energy (0.0.1)
    
<br>

Once installed `octopyenergy` can be imported into your scripts.


```python
import octopyenergy as oe
from octopyenergy.api import DownloadManager
```

<br>

### User Inputs

We now need to assign values for our account/meter details.

N.b. we recommend that you store your account details in a `.env` file and then use the `dotenv` library to set them as environment variables, which can in turn be picked up by `os` and assigned to local variables.


```python
octopus_api_key = 'your_octopus_api_key'
meter_mpan = 'your_meter_mpan'
meter_serial = 'your_meter_serial'
```

<br>

### Configuring the Download Manager

We'll start by initialising the `DownloadManager`, when we do so we can pass a number of parameters which will configure defaults in the download manager. The `octopus_api_key` is also required for some requests.


```python
download_manager = DownloadManager(meter_mpan=meter_mpan, 
                                   meter_serial=meter_serial, 
                                   api_key=octopus_api_key)

download_manager
```

    Welcome to the octopyenergy DownloadManager! For more information please read the documentation at https://github.com/AyrtonB/Octopy-Energy.
    
    The following API end-points are available: 
    retrieve_products, retrieve_product, retrieve_tariff_charges, retrieve_meter_point, retrieve_electricity_consumption, retrieve_gas_consumption, retrieve_gsps

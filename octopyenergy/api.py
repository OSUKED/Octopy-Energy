"""
Imports
"""
import json
import pandas as pd

import os
import copy
import inspect
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


"""
Defining Global Variables 
"""
package_dir = Path(__file__).parent.absolute()

with open(f'{package_dir}/end_points.json', 'r') as fp:
    end_points = json.load(fp)


"""
Helper Functions
"""
def add_end_point_func(end_points, end_point_func_name, DownloadManager, user_defaults={}):
    argument_defaults = {
        'product_code': 'VAR-17-01-11',
        'tariff_type': 'electricity-tariffs',
        'tariff_code': 'E-1R-VAR-17-01-11-A',
        'charge_type': 'standing-charges',
    }
    
    argument_defaults.update(user_defaults)
    
    description = end_points[end_point_func_name]['description']
    parameters = end_points[end_point_func_name]['parameters']
    arguments = end_points[end_point_func_name]['arguments']
    
    argument_defs = [
        f"{arg}='{argument_defaults[arg]}'" 
        if arg in argument_defaults.keys() 
        else arg 
        for arg in arguments
    ]
    
    argument_defs = sorted(argument_defs, key = lambda x: '=' in x) # ensures args come before kwargs

    func_def = (
        f"def func({', '.join(argument_defs+['**kwargs'])}):\n"
        "\tlocals_=locals()\n"
        "\tlocals_.pop('kwargs')\n"
        "\tkwargs.update(locals_)\n"
        f"\treturn DownloadManager.query_endpoint(end_point='{end_point_func_name}', end_point_kwargs=kwargs)"
    )
    
    globals_, locals_ = {'DownloadManager':DownloadManager}, {}
    exec(func_def, globals_, locals_)  
    
    end_point_func = locals_['func']
    end_point_func.__name__ = end_point_func_name
    end_point_func.__doc__ = description + '\n\n' + 'Parameters:' + '\n    ' + '\n    '.join(arguments+parameters)
    
    setattr(DownloadManager, end_point_func_name, end_point_func)
    
    return
    
def add_attr_assignment_func(attribute, DownloadManager):
    assignment_func = lambda value: setattr(DownloadManager, attribute, value) 
    assignment_func.__name__ = f'assign_{attribute}'
    assignment_func.__doc__ = f'The value passed will be assigned to `{attribute}`'
    
    setattr(DownloadManager, assignment_func.__name__, assignment_func)
    
    return

def results_to_df(results, index_col='interval_start', value_cols='consumption', dt_index=True):
    s = (pd
         .DataFrame(results)
         .set_index(index_col)
         [value_cols]
        )

    if dt_index == True:
        s.index = pd.to_datetime(s.index)
    
    return s

class SadOctopy(Exception):
    pass

def check_API_response(r):
    if r.ok == False:
        r_json = r.json()
        
        if 'detail' in r_json:
            raise SadOctopy(r_json['detail']) 
        else:
            raise SadOctopy('The request to the Octopus API was unsuccesful, please check the documentation.')    
    
    
"""
Download Manager
"""
class DownloadManager():
    def __init__(self, meter_mpan:str=None, meter_mprn:str=None, 
                 meter_serial:str=None, api_key:str=None):
        """
        Initialises the Octopus Energy API DownloadManager.
        
        Some requests require authentication, in which case the `api_key` 
        should be passed. The `meter_mpan`, `meter_mprn`, and `meter_serial` 
        can optionally be passed, when they are they're use as defaults 
        in methods like `retrieve_meter_point`.
        
        Parameters:
            meter_mpan: Meter point administration number
            meter_mprn: Meter point reference number
            meter_serial: Meter serial number
            api_key: Octopus API key
            
        Returns:
            download_manager: Instantiation of the DownloadManager class
        
        Example:
            >>> download_manager = DownloadManager(meter_mpan='1012839417444', 
            >>>                                    meter_serial='20L9375357', 
            >>>                                    api_key='kt_live_lihwqe89pw45buioh3bw')
            
        """
        
        # Assigning attributes
        self.api_root = 'https://api.octopus.energy'
        self.docs_url = 'https://github.com/AyrtonB/Octopy-Energy'
            
        locals_ = locals()
        self.attributes = ['meter_mpan', 'meter_mprn', 'meter_serial']
        
        for attribute in self.attributes:
            setattr(self, attribute, locals_[attribute])
            add_attr_assignment_func(attribute, self)
        
        # Constructing request authentication
        self.authenticate(api_key)
        
        # Dynamically constructing methods from end points
        argument_defaults = {attr: getattr(self, attr) for attr in self.attributes}
        
        for end_point_func_name in end_points.keys():
            add_end_point_func(end_points, end_point_func_name, self, argument_defaults)
        
        return
    
    def authenticate(self, api_key:str=None):
        """
        Adds authentication for the API requests. If no 
        api_key is provided then the authentication will 
        be reset and both the auth and api_key set to None.
        
        Parameters:
            api_key: Octopus API key
            
        """
        
        if api_key is not None:
            self.api_key = api_key
            self.auth = HTTPBasicAuth(self.api_key, '')
        else:
            self.api_key = api_key
            self.auth = None
        
        return
        
    def query_endpoint(self, end_point, end_point_kwargs, all_pages=False):
        # Extracting endpoint metadata
        end_point_template = end_points[end_point]['endpoint']
        end_point_available_parameters = end_points[end_point]['parameters']
        end_point_available_arguments = [arg.split('=')[0] for arg in end_points[end_point]['arguments']]
        
        # Checking and separating arguments and parameters
        set_args_params = set(end_point_available_arguments) | set(end_point_available_parameters)
        excess_kwargs = list(set(end_point_kwargs.keys()) - set_args_params)
        assert len(excess_kwargs)==0, f"The following are not arguments or parameters for {end_point} and so should not be passed as kwargs: {', '.join(excess_kwargs)}"

        end_point_arguments_keys = list(set(end_point_kwargs.keys()) - set(end_point_available_parameters))
        end_point_parameters_keys = list(set(end_point_kwargs.keys()) - set(end_point_arguments_keys))

        end_point_arguments = {argument: end_point_kwargs[argument] for argument in end_point_arguments_keys}
        end_point_parameters = {parameter: end_point_kwargs[parameter] for parameter in end_point_parameters_keys}

        # Making request      
        end_point_url = f'{self.api_root}{end_point_template.format(**end_point_arguments)}'
        r = requests.get(end_point_url, params=end_point_parameters, auth=self.auth)
        
        check_API_response(r)

        return r
    
    def retrieve_all_results(self, r):
        r_json = r.json()
        results = []

        if 'next' in r_json.keys():
            if 'results' in r_json.keys():
                results += r_json['results']

            if r_json['next'] is not None:
                next_page_url = r_json['next']
                r = requests.get(next_page_url, auth=self.auth)
                results += self.retrieve_all_results(r)

        return results
    
    def check_attribute_is_assigned(self, attribute):
        assert f'{attribute}' in dir(self), f'`{attribute}` has not been assigned'
        assert getattr(self, attribute) is not None, f'You must specify a `{attribute}` to carry out this operation. This can be done when the download manager is initialised or by using `download_manager.assign_{attribute}({attribute})`.'
    
    def check_attributes_are_assigned(self, attributes):
        for attribute in attributes:
            self.check_attribute_is_assigned(attribute)
            
    def assign_non_none_attributes(self, attributes, attribute_map):
        """
        Iterate over each attribute and
        assigns to the class if not None
        """
        
        for attribute in attributes:
            attribute_val = attribute_map[attribute]
            
            if attribute_val is not None:
                setattr(self, attribute, attribute_val)
                
        return
            
    def process_required_parameters(self, attributes, attribute_map):
        """
        Iterate over each attribute and
        assigns to the class if not None,
        then checks that all attributes
        assigned to the class are not None.
        """
        
        self.assign_non_none_attributes(attributes, attribute_map)
        self.check_attributes_are_assigned(attributes)
        
        return
    
    def create_elec_consumption_s(self, meter_mpan=None, meter_serial=None, **kwargs):
        default_kwargs = {'page_size': 25_000}
        default_kwargs.update(kwargs)
        self.process_required_parameters(['meter_mpan', 'meter_serial'], locals())
        r = self.retrieve_electricity_consumption(self.meter_mpan, self.meter_serial, **default_kwargs)
        results = self.retrieve_all_results(r)
        s_elec_consumption = results_to_df(results)
        
        return s_elec_consumption
    
    def create_gas_consumption_s(self, meter_mprn=None, meter_serial=None, **kwargs):
        default_kwargs = {'page_size': 25_000}
        default_kwargs.update(kwargs)
        self.check_attributes_are_assigned(['meter_mprn', 'meter_serial'])   
        r = self.retrieve_gas_consumption(self.meter_mprn, self.meter_serial, **default_kwargs)
        results = self.retrieve_all_results(r)
        s_gas_consumption = results_to_df(results)
        
        return s_gas_consumption
    
    def __repr__(self):
        repr_text = (
            f'Welcome to the octopyenergy DownloadManager! For more information please read the documentation at {self.docs_url}.\n\n'
            f"The following API end-points are available: \n{', '.join(end_points.keys())}\n\n"
        )
        
        return repr_text

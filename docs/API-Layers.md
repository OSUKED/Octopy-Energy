# API Layers

The `octopyenergy` library provides three levels of abstraction for requesting data from the Octopus Energy API

So far we've mainly used the `create_elec_consumption_s` method, this is a high-level function in the API that carries out the request and then converts the response into a tidied `pandas` series. Underneath this layer lie several lower-level functions which can provide us additional control.

Here we'll query the `retrieve_electricity_consumption` end-point and extract the JSON response.


```python
r = download_manager.retrieve_electricity_consumption(meter_mpan=meter_mpan, meter_serial=meter_serial)

r.json().keys()
```
    dict_keys(['count', 'next', 'previous', 'results'])

<br>

We can use another `octopyenergy` helper function, `response_to_data` to convert the response into a dataframe.

N.b. this will only work for responses which can be converted into a dataframe, such as those from `retrieve_electricity_consumption` and `retrieve_gas_consumption`. 


```python
s_elec_consumption = oe.api.results_to_df(r.json()['results'])

s_elec_consumption.head()
```

| interval_start            |   consumption |
|:--------------------------|--------------:|
| 2020-10-27 23:00:00+00:00 |         0.008 |
| 2020-10-27 22:30:00+00:00 |         0.007 |
| 2020-10-27 22:00:00+00:00 |         0.008 |
| 2020-10-27 21:30:00+00:00 |         0.008 |
| 2020-10-27 21:00:00+00:00 |         0.007 |

<br>

The deepest abstraction level is available through the `query_endpoint` method, this provides access to all of the end-points but requires a larger number of parameters to be passed. The benefit of this level is that it can be easier to work with when the end-point being used is specified through another variable.


```python
end_point = 'retrieve_electricity_consumption'

end_point_kwargs = {
    'meter_mpan': meter_mpan,
    'meter_serial': meter_serial,
}

r = download_manager.query_endpoint(end_point, end_point_kwargs)

r.json().keys()
```

    dict_keys(['count', 'next', 'previous', 'results'])

<br>

One of the issues when working with the direct responses is that we have to iterate through the data pages, we can use a helper method called `retrieve_all_results` to do this for us and return the combined results.


```python
results = download_manager.retrieve_all_results(r)
results_count = len(results)

assert results_count == r.json()['count'], "The full dataset was not returned"

print(results_count)
```

    816
    
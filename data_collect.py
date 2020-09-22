import urllib.request as req
import json
import pandas as pd
import datetime as dt

source_url = "https://wuhan-coronavirus-api.laeyoung.endpoint.ainize.ai/"


def process_api_data(df):
    df['lastupdate'] = pd.to_datetime(df['lastupdate'])
    df['iso3'] = df['countrycode'].apply(lambda x: x['iso3'] if type(x) == dict else None)
    df['iso2'] = df['countrycode'].apply(lambda x: x['iso2'] if type(x) == dict else None)
    df['lat'] = df['location'].apply(lambda x: x['lat' if type(x) == dict else None])
    df['lng'] = df['location'].apply(lambda x: x['lng' if type(x) == dict else None])
    df = df.drop(['countrycode', 'location'], axis=1)
    return df


def get_latest_state(by_country=True, iso2=None):
    latest_ext = "jhu-edu/latest" if not by_country else "jhu-edu/latest?onlyCountries=true"
    latest_ext = "jhu-edu/latest?iso2={}".format(iso2) if iso2 is not None else latest_ext
    url = source_url + latest_ext
    response = req.urlopen(url)
    data = json.loads(response.read())
    df = pd.DataFrame(data)
    df = process_api_data(df)
    return df


def get_time_series(by_country=True, iso2=None):
    time_ext = "jhu-edu/timeseries" if not by_country else "jhu-edu/timeseries?onlyCountries=true"
    time_ext = "jhu-edu/timeseries?iso2={}".format(iso2) if iso2 is not None else time_ext
    url = source_url + time_ext
    response = req.urlopen(url)
    data = json.loads(response.read())
    out_ts = []
    countries = []
    for d in data:
        df = pd.DataFrame(d['timeseries']).T
        df.index = pd.to_datetime(df.index)
        out_ts.append(df)
        c_info = {'countryregion':d['countryregion'],
                  'lat':d['location']['lat'] if 'location' in d else None,
                  'lng':d['location']['lng'] if 'location' in d else None,
                  'iso2':d['countrycode']['iso2'] if 'countrycode' in d else None,
                  'iso3':d['countrycode']['iso3'] if 'countrycode' in d else None}
        countries.append(c_info)
    countries = pd.DataFrame(countries)
    countries['index'] = countries.index
    return out_ts, pd.DataFrame(countries)


def get_date_state(date, country_df=None, ts_list=None):
    if country_df is None  or ts_list is None:
        ts_list, country_df = get_time_series()
    df_date = pd.concat([a.loc[date] for a in ts_list], axis=1)
    out = country_df.copy()
    df_date.columns = out.index
    out[df_date.index] = df_date.T
    return out






if __name__ == "__main__":
    ts_list, country_df = get_time_series()
    a = get_date_state(country_df,ts_list,dt.date(2020,3,10))


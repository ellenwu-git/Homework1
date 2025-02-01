#########################################################################
## Read in service area data
#########################################################################

import numpy as np
import pandas as pd

# Read in monthly files, append to yearly file, fill in missing info, and collapse down to yearly file
service_area_data = []
y_start = 2015
y_end = 2015
monthlist = range(1, 13)
contract_service_area = pd.DataFrame()

service_year = pd.DataFrame()

for y in range(y_start, y_end+1):
    service_year = pd.DataFrame()
    
    for m in monthlist:
        # Pull service area data by contract/month
        m = str(m).rjust(2, '0')
        ma_path = f"/Users/ellenwu/econ470/Homework1/data/input/MA_Cnty_SA_2015_01(in).csv"
        service_area = pd.read_csv(ma_path, skiprows=1, names=[
            "contractid", "org_name", "org_type", "plan_type", "partial", "eghp",
            "ssa", "fips", "county", "state", "notes"
        ], dtype={
            "contractid": str,
            "org_name": str,
            "org_type": str,
            "plan_type": str,
            "partial": str,
            "eghp": str,
            "ssa": float,
            "fips": float,
            "county": str,
            "state": str,
            "notes": str
        })
        
        service_area['month'] = m
        service_area['year'] = y
        service_area['partial'] = np.where(service_area['partial'] == '*', True, False)
        service_area['eghp'] = np.where(service_area['eghp'] == 'Y', True, False)
        
        service_year = pd.concat([service_year, service_area], ignore_index=True)

    # Fill in missing fips codes (by state and county)
    service_year['fips'] = service_year.groupby(['state', 'county'])['fips'].ffill().bfill()

    # Fill in missing plan type, org info, partial status, and eghp status (by contractid)
    list_chars = ['plan_type', 'org_name', 'org_type', 'partial', 'eghp']
    for char in list_chars:
        service_year[char] = service_year.groupby('contractid')[char].ffill().bfill()

    # Collapse to yearly data
    service_year['id_count'] = service_year.groupby(['contractid', 'fips']).cumcount() + 1
    service_year = service_year[service_year['id_count'] == 1].drop(columns=['id_count', 'month'])

    # Concatenate data
    contract_service_area = pd.concat([contract_service_area, service_year], ignore_index=True)

contract_service_area.to_csv("/Users/ellenwu/econ470/Homework1/data/output/contract_service_area.csv", index=False)
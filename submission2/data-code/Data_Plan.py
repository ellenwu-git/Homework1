import pandas as pd

y_start = 2015
y_end = 2015
full_ma_data = pd.DataFrame()

for y in range(y_start, y_end+1):
    # Basic contract/plan information
    ma_path = f"/Users/ellenwu/econ470/Homework1/data/input/CPSC_Contract_Info_2015_01(in).csv"
    contract_info = pd.read_csv(ma_path, skiprows=1, encoding='latin1', names=[
        "contractid", "planid", "org_type", "plan_type", "partd", "snp", "eghp", "org_name",
        "org_marketing_name", "plan_name", "parent_org", "contract_date"
    ], dtype={
        "contractid": str,
        "planid": float,
        "org_type": str,
        "plan_type": str,
        "partd": str,
        "snp": str,
        "eghp": str,
        "org_name": str,
        "org_marketing_name": str,
        "plan_name": str,
        "parent_org": str,
        "contract_date": str
    })

    contract_info['id_count'] = contract_info.groupby(['contractid', 'planid']).cumcount() + 1
    contract_info = contract_info[contract_info['id_count'] == 1].drop(columns=['id_count'])

    # Enrollments per plan
    ma_path = f"/Users/ellenwu/econ470/Homework1/data/input/CPSC_Contract_Info_2015_01(in).csv"
    enroll_info = pd.read_csv(ma_path, skiprows=1, names=[
        "contractid", "planid", "ssa", "fips", "state", "county", "enrollment"
    ], dtype={
        "contractid": str,
        "planid": float,
        "ssa": float,
        "fips": float,
        "state": str,
        "county": str,
        "enrollment": float
    }, na_values="*")

    # Merge contract info with enrollment info
    plan_data = contract_info.merge(enroll_info, on=["contractid", "planid"], how="left")
    plan_data['year'] = y

    # Fill in missing fips codes by state and county
    plan_data['fips'] = plan_data.groupby(['state', 'county'])['fips'].ffill().bfill()

    # Fill in missing plan characteristics by contract and plan id
    list_char = ['plan_type', 'partd', 'snp', 'eghp', 'plan_name']
    for char in list_char:
        plan_data[char] = plan_data.groupby(['contractid', 'planid'])[char].ffill().bfill()

    # Fill in missing contract characteristics by contractid
    list_char = ['org_type', 'org_name', 'org_marketing_name', 'parent_org']
    for char in list_char:
        plan_data[char] = plan_data.groupby(['contractid'])[char].ffill().bfill()

    # Assume January is the avg enrollment for the year
    plan_data.rename(columns={'enrollment': 'avg_enrollment'}, inplace=True)

    # Concatenate data
    full_ma_data = pd.concat([full_ma_data, plan_data], ignore_index=True)

full_ma_data.to_csv("/Users/ellenwu/econ470/Homework1/data/output/full_ma_data.csv", index=False)
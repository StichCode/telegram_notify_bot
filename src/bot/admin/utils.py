import pandas as pd
import requests


def get_file(file_url: str, col_name: str) -> list[str]:
    resp = requests.get(file_url, verify=False)
    df = pd.read_excel(resp.content)
    return df[col_name].tolist()

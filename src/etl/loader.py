
import pandas as pd

from normaliser import (
    normalize_columns
)

def load_excel(path, header=1):

    df = pd.read_excel(path, header = header)

    df = normalize_columns(df)

    return df


if __name__ == "__main__":

    df = load_excel(r"C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\companies.xlsx")

    df = df.fillna("")

    print(df.head())

    print(df.columns)
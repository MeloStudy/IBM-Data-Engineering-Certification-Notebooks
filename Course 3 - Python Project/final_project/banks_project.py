# Project Scenario
"""
You have been hired as a data engineer by research organization.
Your boss has asked you to create a code that can be used
to compile the list of the top 10 largest banks in the world
ranked by market capitalization in billion USD.
Further, the data needs to be transformed and stored
in GBP, EUR and INR as well, in accordance with the exchange rate
information that has been made available to you as a CSV file.
The processed information table is to be saved locally in a CSV format and as a database table.

Your job is to create an automated system to generate this information
so that the same can be executed in every financial quarter to prepare the report.
"""

# Importing the required libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime


def log(message, log_file="code_log.txt"):
    timestamp_format = "%Y-%h-%d-%H:%M:%S"  # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now()  # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open(log_file, "a") as f:
        f.write(timestamp + " : " + message + "\n")


def extract(data_url, extract_attributes=["Name", "MC_USD_BILLION"]):
    page = requests.get(data_url).text
    data = BeautifulSoup(page, "html.parser")
    df = pd.DataFrame(columns=extract_attributes)

    tables = data.find_all("tbody")
    rows = tables[0].find_all("tr")
    for row in rows:
        col = row.find_all("td")
        if len(col) != 0:
            if col[1].find("a") is not None and "—" not in col[2]:
                aList = col[1].find_all("a")
                data_dict = {
                    "Name": aList[1].text,
                    "MC_USD_BILLION": float(col[2].text),
                }
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df, df1], ignore_index=True)
    return df


def transform(df, exchange_data="exchange_rate.csv"):
    exchanges_df = pd.read_csv(exchange_data)
    gbp_rate = exchanges_df[exchanges_df["Currency"] == "GBP"]["Rate"].values[0]
    eur_rate = exchanges_df[exchanges_df["Currency"] == "EUR"]["Rate"].values[0]
    inr_rate = exchanges_df[exchanges_df["Currency"] == "INR"]["Rate"].values[0]

    df["MC_GBP_Billion"] = df["MC_USD_BILLION"] * gbp_rate
    df["MC_EUR_Billion"] = df["MC_USD_BILLION"] * eur_rate
    df["MC_INR_Billion"] = df["MC_USD_BILLION"] * inr_rate

    ## round
    df = df.round(2)
    print(df)
    return df


def load_to_csv(df, output_path):
    df.to_csv(output_path)


def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists="replace")


def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)


data_url = "https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks"
bd_attributes = [
    "Name",
    "MC_USD_BILLION",
    "MC_GBP_Billion",
    "MC_EUR_Billion",
    "MC_INR_Billion",
]
csv_path = "./Largest_banks_data.csv"
db_name = "Banks.db"
table_name = "Largest_banks"

log("Preliminaries complete. Initiating ETL process")
df = extract(data_url)

log("Data extraction complete. Initiating Transformation process")
df = transform(df)

log("Data transformation complete. Initiating loading process")

load_to_csv(df, csv_path)

log("Data saved to CSV file")

sql_connection = sqlite3.connect(db_name)

log("SQL Connection initiated.")

load_to_db(df, sql_connection, table_name)

log("Data loaded to Database as table. Executing the query")

query_statement = f"SELECT * from {table_name}"
run_query(query_statement, sql_connection)

query_statement = f"SELECT AVG(MC_GBP_Billion) from {table_name}"
run_query(query_statement, sql_connection)

query_statement = f"SELECT Name from {table_name} LIMIT 5"
run_query(query_statement, sql_connection)

log("Process Complete")

sql_connection.close()

log("Server Connection closed")

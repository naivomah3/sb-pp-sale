import csv
import argparse
import uuid
import sys
import os, time
import pandas as pd
from itertools import islice
from random import seed, choice
from datetime import date
import math
from mapbox import Geocoder
import requests
import logging
import time


def CalculNormalyzecExpenseConcierge(NumUnit):
    if 4 <= NumUnit <= 6:
        NormExpConcierge = NumUnit*125
    elif 7 <= NumUnit <= 11:
        NormExpConcierge = NumUnit*170
    else:
        NormExpConcierge = NumUnit*300
    return NormExpConcierge    

def CalculNormalyzecExpenseManagement(NumUnit, RBA):
    if 5 <= NumUnit <= 6:
        NormExpManagement = RBA*0.03
    elif 7 <= NumUnit <= 11:
        NormExpManagement = RBA*0.04
    else:
        NormExpManagement = RBA*0.05
    return NormExpManagement  

def round_up(n, decimals=0): 
    multiplier = 10 ** decimals 
    return math.ceil(n * multiplier) / multiplier

def SetExpensesInsurances(NumUnit,ExpenIns):
    if not ExpenIns or ExpenIns < 100:
        ExpIns = NumUnit * 500
    else:
        ExpIns = ExpenIns
    return ExpIns

def SetExpensesElectricity(NumUnit, ExpenElect):
    if not ExpenElect or ExpenElect < 100:
        ExpElec = NumUnit * 100
    else:
        ExpElec = ExpenElect
    return ExpElec


CSVfile = '07_09_10-14_COMP_ALL.csv'


with open(os.path.join(application_path, CSVfile), 
          'r', 
          newline='', 
          encoding='utf-8-sig') as ReadcsvFileRowComp:
    
    readerRawComp = csv.DictReader(ReadcsvFileRowComp)
    for rowRawComp in readerRawComp:    
        #print(rowRawComp)
        NumUnit = int(rowRawComp["UNITS_NUMBER"])
        if NumUnit >= 5:
            
            RBA = int(rowRawComp["REVENUS_RESIDENTIAL"]) + \
                int(rowRawComp["REVENUS_COMMERCIAL"]) + \
                int(rowRawComp["REVENUS_GARAGES"]) + \
                int(rowRawComp["REVENUS_OTHERS"])
            
            REVENUS_GROSS_ROUND = round_up(RBA, -3)
            
            EXPENSES_HEATING = int(rowRawComp["EXPENSES_GAZ"]) + int(rowRawComp["EXPENSES_OIL"])
            NORMALYZED_EXPENSES_MAINTENANCE = NumUnit * 500
            NORMALYZED_EXPENSES_CONCIERGE = CalculNormalyzecExpenseConcierge(NumUnit)
            NORMALYZED_EXPENSES_MANAGMENT = CalculNormalyzecExpenseManagement(NumUnit, RBA)
            NORMALYZED_EXPENSES_VACANCY = round(RBA * 0.03, 2)
            EXPENSES_INSURANCES =  SetExpensesInsurances(NumUnit, int(rowRawComp["EXPENSES_INSURANCES"]))
            EXPENSES_ELECTRICITY = SetExpensesElectricity(NumUnit, int(rowRawComp["EXPENSES_ELECTRICITY"]))
            
            TOTAL_NORMALYZED_EXPENSE = round(EXPENSES_INSURANCES + \
                                             EXPENSES_ELECTRICITY + \
                                             EXPENSES_HEATING + \ 
                                             int(rowRawComp["EXPENSES_MUNICIPAL_TAXES"]) + \
                                             int(rowRawComp["EXPENSES_SCHOLAR_TAXES"]) + \
                                             NORMALYZED_EXPENSES_MAINTENANCE + \
                                             NORMALYZED_EXPENSES_CONCIERGE + \
                                             NORMALYZED_EXPENSES_MANAGMENT + \
                                             NORMALYZED_EXPENSES_VACANCY, 2)
            
            NORMALYZED_EXPENSES_ROUND = abs(round_up(TOTAL_NORMALYZED_EXPENSE, -2))
            
            NET_NORMALYZED_INCOME = round(RBA - TOTAL_NORMALYZED_EXPENSE,2)
            CAP_RATE = round((NET_NORMALYZED_INCOME / int(rowRawComp["PURCHASE_PRICE"]) * 100), 2)
            PRICE_PER_UNIT = round(int(rowRawComp["PURCHASE_PRICE"]) / NumUnit,2)
            GROSS_REVENUE_MULTIPLICATOR = round(int(rowRawComp["PURCHASE_PRICE"]) / RBA, 2)
            NET_REVENUE_MULTIPLICATOR = round(int(rowRawComp["PURCHASE_PRICE"]) / NET_NORMALYZED_INCOME, 2)
            
            print(rowRawComp["FULL_ADDRESSES"] + " " + rowRawComp["PURCHASE_PRICE"], \ 
                  RBA, REVENUS_GROSS_ROUND, TOTAL_NORMALYZED_EXPENSE, \
                  str(NORMALYZED_EXPENSES_ROUND) + " TGA : " + str(CAP_RATE))
            

            ADDRESS = rowRawComp["FULL_ADDRESSES"]
            #response = geocoder.forward(ADDRESS)
            #print(response.text)
            #place = response.geojson()['features'][0]

            geocode_result = get_google_results(ADDRESS, API_KEY, return_full_response=RETURN_FULL_RESULTS)
            #print(geocode_result["formatted_address"])
            LATITUDE = geocode_result["latitude"]
            LONGITUDE = geocode_result["longitude"]
            PLACE_NAME = geocode_result["formatted_address"]
            
            print(str(PLACE_NAME)+" "+rowRawComp["PURCHASE_PRICE"], RBA, \
                  REVENUS_GROSS_ROUND, \
                  TOTAL_NORMALYZED_EXPENSE,  \
                  str(NORMALYZED_EXPENSES_ROUND) + \
                  " TGA : "+str(CAP_RATE))
            
            if "Montr" in str(PLACE_NAME):
                if 3 <= CAP_RATE <= 6: 

                    with open(os.path.join(application_path,'TAB_COMPARABLE_PROPERTIES_'+CSVfile), 
                              mode='a', 
                              encoding='utf-8') as resultFile:
                        result_writer = csv.writer(resultFile, 
                                                   delimiter=',', 
                                                   quotechar='"', 
                                                   quoting=csv.QUOTE_MINIMAL, 
                                                   lineterminator='\n')
                        result_writer.writerow([date.today(),
                                                rowRawComp["PURCHASE_PRICE"],
                                                rowRawComp["DATE_OF_SALE"],
                                                PLACE_NAME,
                                                LATITUDE,
                                                LONGITUDE,
                                                rowRawComp["UNITS_NUMBER"],
                                                rowRawComp["YEAR_BUILD"],
                                                REVENUS_GROSS_ROUND,
                                                NORMALYZED_EXPENSES_ROUND,
                                                CAP_RATE, 
                                                PRICE_PER_UNIT,
                                                GROSS_REVENUE_MULTIPLICATOR, 
                                                NET_REVENUE_MULTIPLICATOR])
            else:
                if 4 <= CAP_RATE <= 9: 
                    with open(os.path.join(application_path,'TAB_COMPARABLE_PROPERTIES_'+CSVfile), 
                              mode='a', 
                              encoding='utf-8') as resultFile:
                        result_writer = csv.writer(resultFile, 
                                                   delimiter=',', 
                                                   quotechar='"', 
                                                   quoting=csv.QUOTE_MINIMAL, 
                                                   lineterminator='\n')
                        result_writer.writerow([date.today(),
                                                rowRawComp["PURCHASE_PRICE"],
                                                rowRawComp["DATE_OF_SALE"],
                                                PLACE_NAME,
                                                LATITUDE,
                                                LONGITUDE,
                                                rowRawComp["UNITS_NUMBER"],
                                                rowRawComp["YEAR_BUILD"],
                                                REVENUS_GROSS_ROUND,
                                                NORMALYZED_EXPENSES_ROUND,
                                                CAP_RATE, 
                                                PRICE_PER_UNIT,
                                                GROSS_REVENUE_MULTIPLICATOR, 
                                                NET_REVENUE_MULTIPLICATOR])
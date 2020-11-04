import sqlite3
import os
import sys
import mysql.connector
from mysql.connector import errorcode

# Variables
database = r"05_DATABASE/DB_02_Comparable_Matrix.db"


def create_local_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to SQLite")
    except sqlite3.Error as e:
        print(e)

    return conn


def create_mysql_connection():
    try:
        cnx = mysql.connector.connect(user='USERINSERT', password='INSERT_PASS', host='35.182.103.143', database='upky')
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


def save_mysql_upky_comparable_properties(conn, CREATION_DATE, PURCHASE_PRICE, ADDRESSES_FULL, LATITUDE, LONGITUDE, UNIT_NUMBER, YEAR_BUILD, REVENU_GROSS_ROUNDED, NORMALYZED_EXPENSES_ROUNDED, CAP_RATE, PRICE_PER_UNIT, GROSS_REVENUE_MULTIPLICATOR, NET_REVENUE_MULTIPLICATOR, DATE_OF_SALE):
    try:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO comparable_properties_20200717 (CREATION_DATE,PURCHASE_PRICE,ADDRESSES_FULL,LATITUDE,LONGITUDE,UNIT_NUMBER,YEAR_BUILD,REVENU_GROSS_ROUNDED,NORMALYZED_EXPENSES_ROUNDED,CAP_RATE,PRICE_PER_UNIT,GROSS_REVENUE_MULTIPLICATOR,NET_REVENUE_MULTIPLICATOR,DATE_OF_SALE)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (CREATION_DATE, PURCHASE_PRICE, ADDRESSES_FULL, LATITUDE, LONGITUDE, UNIT_NUMBER, YEAR_BUILD, REVENU_GROSS_ROUNDED, NORMALYZED_EXPENSES_ROUNDED, CAP_RATE, PRICE_PER_UNIT, GROSS_REVENUE_MULTIPLICATOR, NET_REVENUE_MULTIPLICATOR, DATE_OF_SALE))
        conn.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)


def SelectAllDistinc(conn):
    try:

        cursor = conn.cursor()
        # UNIT 2-3-4
        #cursor.execute('''SELECT * from MATRIX_MULTI_RES_SOLD WHERE UNIT_NUMBER <='4' GROUP BY(ADDRESS) ORDER BY ID ASC''')
        # UNIT 5+
        cursor.execute('''SELECT * from MATRIX_MULTI_RES_SOLD WHERE UNIT_NUMBER >='5' GROUP BY(ADDRESS) ORDER BY ID ASC''')
        rows = cursor.fetchall()
        print(len(rows))
        return rows
    except sqlite3.Error as error:
        print("Failed to Select Data into sqlite table", error)


def SetExpensesInsurances(NumUnit, ExpenIns):
    if not ExpenIns or ExpenIns < 100:
        if NumUnit > 5:
            ExpIns = NumUnit * 500
        else:
            ExpIns = NumUnit * 650
    else:
        ExpIns = ExpenIns
    return ExpIns


def SetExpensesElectricity(NumUnit, ExpenElect):
    if not ExpenElect or ExpenElect < 100:
        ExpElec = NumUnit * 100
    else:
        ExpElec = ExpenElect
    return ExpElec


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


def main():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    # create a database connection
    connlocal = create_local_connection(database)
    connmysql = create_mysql_connection()
    with connlocal:
        print("2. Query all tasks")
        AllRow = SelectAllDistinc(connlocal)
        i = 0
        TOTALMRN = 0
        for row in AllRow:

            #############
            # Set Variables for Property
            CREATION_DATE = row[1]
            SOLD_DATE = row[2]
            ADDRESSES_FULL = row[4]
            LATITUDE = row[5]
            LONGITUDE = row[6]
            PURCHASE_PRICE = int(row[7])
            UNIT_NUMBER = row[8]
            YEAR_BUILD = row[14]
            RBA = row[18] + row[19] + row[20] + row[21]
            TAXES_MUNI = int(row[22])
            TAXES_SCHOOL = int(row[23])
            EXPENSES_ELECTRICITY = row[24]
            EXPENSES_HEATING = row[25] + row[26]
            REVENUS_GROSS_ROUND = round(RBA, -3)
            NORMALYZED_EXPENSES_VACANCY = round(RBA * 0.03, 2)
            EXPENSES_INSURANCES = SetExpensesInsurances(UNIT_NUMBER, int(row[27]))

            if UNIT_NUMBER >= 5:
                NORMALYZED_EXPENSES_MAINTENANCE = UNIT_NUMBER*500
                NORMALYZED_EXPENSES_CONCIERGE = CalculNormalyzecExpenseConcierge(UNIT_NUMBER)
                NORMALYZED_EXPENSES_MANAGMENT = CalculNormalyzecExpenseManagement(UNIT_NUMBER, RBA)
                TOTAL_NORMALYZED_EXPENSE = round(EXPENSES_INSURANCES +
                                                 EXPENSES_ELECTRICITY +
                                                 EXPENSES_HEATING +
                                                 TAXES_MUNI +
                                                 TAXES_SCHOOL +
                                                 NORMALYZED_EXPENSES_MAINTENANCE +
                                                 NORMALYZED_EXPENSES_CONCIERGE +
                                                 NORMALYZED_EXPENSES_MANAGMENT +
                                                 NORMALYZED_EXPENSES_VACANCY, 2)

                NORMALYZED_EXPENSES_ROUND = abs(round(TOTAL_NORMALYZED_EXPENSE, -2))
                NET_NORMALYZED_INCOME = round(RBA - TOTAL_NORMALYZED_EXPENSE, 2)
                CAP_RATE = round((NET_NORMALYZED_INCOME/PURCHASE_PRICE)*100, 2)
                PRICE_PER_UNIT = round(PURCHASE_PRICE/UNIT_NUMBER, 2)
                GROSS_REVENUE_MULTIPLICATOR = round(PURCHASE_PRICE/RBA, 2)
                NET_REVENUE_MULTIPLICATOR = round(int(PURCHASE_PRICE)/NET_NORMALYZED_INCOME, 2)

                if PURCHASE_PRICE > 50000 and 5 < GROSS_REVENUE_MULTIPLICATOR < 80 and 5 < NET_REVENUE_MULTIPLICATOR < 50:
                    print("ID : "+str(row[0])+" - UNIT:"+str(UNIT_NUMBER)+" - RBA: "+str(RBA)+" - VACANCY: "+str(NORMALYZED_EXPENSES_VACANCY)+" - ASS: "+str(EXPENSES_INSURANCES)+" - Maintenance: "+str(NORMALYZED_EXPENSES_MAINTENANCE)+" - Concierge : "+str(
                        NORMALYZED_EXPENSES_CONCIERGE)+" - Mgmt: "+str(NORMALYZED_EXPENSES_MANAGMENT)+" - TOTAL_EXPENSE: "+str(TOTAL_NORMALYZED_EXPENSE)+" - PPU : "+str(PRICE_PER_UNIT)+" - CAP Rate: "+str(CAP_RATE)+" - MRB: "+str(GROSS_REVENUE_MULTIPLICATOR)+" - MRN :"+str(NET_REVENUE_MULTIPLICATOR))

                    save_mysql_upky_comparable_properties(connmysql,
                                                          CREATION_DATE,
                                                          PURCHASE_PRICE,
                                                          ADDRESSES_FULL,
                                                          LATITUDE,
                                                          LONGITUDE,
                                                          UNIT_NUMBER,
                                                          YEAR_BUILD,
                                                          REVENUS_GROSS_ROUND,
                                                          NORMALYZED_EXPENSES_ROUND,
                                                          CAP_RATE,
                                                          PRICE_PER_UNIT,
                                                          GROSS_REVENUE_MULTIPLICATOR,
                                                          NET_REVENUE_MULTIPLICATOR,
                                                          SOLD_DATE)

            if 2 <= UNIT_NUMBER <= 4 and RBA > 5000:
                TOTAL_NORMALYZED_EXPENSE = round(EXPENSES_INSURANCES +
                                                 EXPENSES_ELECTRICITY +
                                                 EXPENSES_HEATING +
                                                 TAXES_MUNI +
                                                 TAXES_SCHOOL +
                                                 NORMALYZED_EXPENSES_VACANCY +
                                                 int(row[27]) +
                                                 int(row[28]), 2)

                NORMALYZED_EXPENSES_ROUND = round(TOTAL_NORMALYZED_EXPENSE, -2)
                NET_NORMALYZED_INCOME = round(RBA-TOTAL_NORMALYZED_EXPENSE, 2)
                CAP_RATE = round((NET_NORMALYZED_INCOME/PURCHASE_PRICE)*100, 2)
                PRICE_PER_UNIT = round(PURCHASE_PRICE/UNIT_NUMBER, 2)
                GROSS_REVENUE_MULTIPLICATOR = round(PURCHASE_PRICE/RBA, 2)
                NET_REVENUE_MULTIPLICATOR = round(int(PURCHASE_PRICE)/NET_NORMALYZED_INCOME, 2)

                if PURCHASE_PRICE > 30000 and 5 < GROSS_REVENUE_MULTIPLICATOR < 50 and 5 < NET_REVENUE_MULTIPLICATOR < 80:
                    TOTALMRN = TOTALMRN + NET_REVENUE_MULTIPLICATOR
                    i = i + 1
                    print("ID : " + str(row[0]) +
                          "\n - UNIT:" + str(UNIT_NUMBER) +
                          "\n - RBA: " + str(RBA) +
                          "\n - VACANCY: " + str(NORMALYZED_EXPENSES_VACANCY) +
                          "\n - ASS: " + str(EXPENSES_INSURANCES) +
                          "\n - TOTAL_EXPENSE: " + str(TOTAL_NORMALYZED_EXPENSE) +
                          "\n - PPU : " + str(PRICE_PER_UNIT) +
                          "\n - MRB: " + str(GROSS_REVENUE_MULTIPLICATOR) +
                          "\n - MRN :" + str(NET_REVENUE_MULTIPLICATOR))

                    save_mysql_upky_comparable_properties(connmysql,
                                                          CREATION_DATE,
                                                          PURCHASE_PRICE,
                                                          ADDRESSES_FULL,
                                                          LATITUDE,
                                                          LONGITUDE,
                                                          UNIT_NUMBER,
                                                          YEAR_BUILD,
                                                          REVENUS_GROSS_ROUND,
                                                          NORMALYZED_EXPENSES_ROUND,
                                                          CAP_RATE,
                                                          PRICE_PER_UNIT,
                                                          GROSS_REVENUE_MULTIPLICATOR,
                                                          NET_REVENUE_MULTIPLICATOR,
                                                          SOLD_DATE)


if __name__ == '__main__':
    main()

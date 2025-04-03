import sqlite3 as sql, os, json
import datetime as dt
from datetime import datetime
import os

current_path = os.path.dirname(os.path.abspath(__file__))
DTpath = os.path.join(current_path, "static", "devicetype.json")
currentdate = dt.datetime.now().strftime("%m-%d")
print(currentdate)


def get_tables(cust, devicetype):
    path2 = os.path.join(current_path, cust, f"{devicetype}.db")
    if not os.path.exists(path2):
        return []
    tables_list = []
    try:
        with sql.connect(path2) as con:
            cursor = con.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            for table in table_names:
                tables_list.append(int(table))
            if tables_list:
                tables_list.pop(0)  # Remove default table '0'
    except sql.Error as e:
        print(f"Database error: {e}")
    return tables_list


def larged_table(cust, devicetype):
    path2 = os.path.join(current_path, cust, f"{devicetype}.db")
    try:
        with sql.connect(path2) as con:
            cursor = con.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [int(table[0]) for table in tables if table[0].isdigit()]
            return max(table_names) if table_names else 0
    except sql.Error as e:
        print(f"Database error: {e}")
        return max(table_names) if table_names else 1


def show(cust, devicetype):
    file_path = os.path.join(current_path, cust, f"{devicetype}.db")
    total = 0
    totalsales = 0
    current = 0
    totalprice = 0

    if not os.path.exists(file_path):
        return (total, totalsales, current, f"{totalprice:,}", totalprice)

    try:
        with sql.connect(file_path) as con:
            cursor = con.cursor()
            # الحصول على أحدث جدول تلقائيًا
            current_table = str(larged_table(cust, devicetype))
            cursor.execute(f"SELECT السعر, المباع, الكل FROM '{current_table}'")
            data = cursor.fetchall()

            if data:
                prices = [row[0] or 0 for row in data]
                sales = [row[1] or 0 for row in data]
                total = data[0][2] if len(data[0]) > 2 else 0
                totalprice = sum(prices)
                totalsales = sum(sales)
                current = total - totalsales

    except Exception as e:
        print(f"Error: {e}")
    return total, totalsales, current, f"{totalprice:,}", totalprice


def add(cust, devicetype, SALE, PRICE):
    em, totalsales, current, em, totalprice = show(cust, devicetype)
    SALE = 0 if SALE == "" else SALE
    PRICE = 0 if PRICE == "" else PRICE

    if SALE == 0 and PRICE == 0:
        return "الكمية والسعر لا يمكن أن تكونا 0!"

    if int(SALE) > int(current) or int(SALE) < -int(totalsales):
        return "الكمية المباعة تتجاوز المخزون الحالي!"
    elif int(PRICE) < -int(totalprice):
        return "السعر يتجاوز المال الحالي!"
    else:
        file_path = os.path.join(current_path, cust, f"{devicetype}.db")
        con = sql.connect(file_path)
        curs = con.cursor()
        curs.execute(
            f"INSERT INTO '{larged_table(cust, devicetype)}' VALUES({PRICE}, {SALE}, '{currentdate}',0)"
        )
        con.commit()
        con.close()
        return "تم"


def create_Table(cust, devicetype, TOTAL):
    em, totalsales, em, em, em = show(cust, devicetype)
    last_table = larged_table(cust, devicetype)
    file_path = os.path.join(current_path, cust, f"{devicetype}.db")

    con = sql.connect(file_path)
    curs = con.cursor()
    curs.execute(f"UPDATE '{last_table}' SET الكل = {totalsales} WHERE rowid = 1")
    con.commit()
    curs.execute(
        f"CREATE TABLE '{last_table+1}'(السعر INTEGER,المباع INTEGER,التاريخ TEXT,الكل INTEGER)"
    )
    con.commit()
    curs.execute(f"INSERT INTO '{last_table+1}'(الكل) VALUES({TOTAL})")
    con.commit()
    con.close()


def add_new_device(devicetype):
    cust = ["اشرف", "محمود"]
    with open(DTpath, "r", encoding="utf-8") as f:
        my_array = json.load(f)

    if (devicetype not in my_array) and (devicetype != ""):
        my_array.append(str(devicetype))

        with open(DTpath, "w", encoding="utf-8") as f:
            json.dump(my_array, f, indent=4)

        # Create directories for each customer
        for i in cust:
            file_path = os.path.join(current_path, i, f"{str(devicetype)}.db")
            con = sql.connect(file_path)
            curs = con.cursor()
            curs.execute(
                "CREATE TABLE '0'(السعر INTEGER,المباع INTEGER,التاريخ TEXT,الكل INTEGER)"
            )
            con.commit()
            con.close()
        return "تم"

    else:
        return "موجود بالفعل"


def get_data(cust, devicetype, num):
    file_path = os.path.join(current_path, cust, f"{devicetype}.db")
    if not os.path.exists(file_path):
        return []
    con = sql.connect(file_path)
    cur = con.cursor()
    try:
        cur.execute(f"SELECT السعر, المباع, التاريخ FROM '{num}'")
        data = cur.fetchall()
    except sql.OperationalError as e:
        print(f"Error: {e}")
        data = []
    finally:
        con.close()
    return data[1:] if data else []

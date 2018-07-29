import sqlite3
import pandas as pd
import sys
import string
import random

def connect_to_db():
    conn = sqlite3.connect("airport_management.db")
    cur = conn.cursor()
    return conn, cur

def close_db(conn, cur):
    cur.close()
    conn.close()

def check_query(query):
    if query.upper() == 'Y' or query.upper() == 'YES':
        return 1
    elif query.upper() == 'N' or query.upper() == 'NO':
        print ("SUCESSFULLY EXITED...")
	print
        return 2
    else:
        print ("INVALID INPUT.....AUTOMATICALLY EXITED")
	print
        return 2

def validate_pnr(df, PNR_entered):
    if (len(df.index) == 0):
        print ("No results found for the PNR: {0}".format(PNR_entered))
	print
        query = raw_input("Do you want to try again with different PNR number [Y/N]: ")
        return check_query(query)

    return 0

def validate_last_name(df, last_name):
    if df['L_NAME'][0] != last_name.upper():
        print ("WRONG LAST NAME: {0}".format(last_name))
	print
        query = raw_input("Do you want to try again with different LAST NAME [Y/N]: ")
        return check_query(query)

    return 0

def validate_flight_no(df, flight_no_entered):
    if (len(df.index) == 0):
        print ("No such Flight exists or None of the passenger has done check in: {0}".format(flight_no_entered))
	print
        query = raw_input("Do you want to try again with different Flight number [Y/N]: ")
        return check_query(query)
    return 0

def is_alpha(your_string):
    ALPHABETS = string.ascii_lowercase + string.ascii_uppercase
    for c in your_string:
        if c not in ALPHABETS:
            print("INVALID NAME....ALPHABETS REQUIRED")
            print
            close_db(conn, cur)
            sys.exit()
    return

def validate_flight_no_is_int(flight_no_entr):
    try:
        val = int(flight_no_entr)
        if val <= 0:
            print("POSITIVE INTEGER REQUIRED....")
            print
            close_db(conn, cur)
            sys.exit()
    except ValueError:
        print("POSITIVE INTEGER REQUIRED....")
        print
        close_db(conn, cur)
        sys.exit()

def SequerityPersonnel():
    while 1:

        PNR_entered = raw_input("Please Enter the PNR number: ")
        flight_no_entr = raw_input("Please Enter the Flight number: ")

        validate_flight_no_is_int(flight_no_entr)

        df = pd.read_sql_query("Select * from PASSENGER where PNR = " + "'" + PNR_entered + "'", conn)

        val = validate_pnr(df, PNR_entered)
        if(val == 1):
            continue
        if(val == 2):
            return

        if df['flight_no'][0] != int(flight_no_entr):
            print ("WRONG Flight Number: {0}".format(flight_no_entr))
            print

            query = raw_input("Do you want to try again with different Flight Number [Y/N]: ")

            val = check_query(query)
            if(val == 1):
                continue
            if(val == 2):
                return

        print (df)
        print

        check = raw_input("Are the detailes valid [Y/N]: ")
        if check.upper() == 'Y' or check.upper() == 'YES':
            cur.execute("update PASSENGER set Sequerity_CheckIN=1 where PNR = " + "'" + PNR_entered + "'")
            conn.commit()
            print ("SECURITY CHECKIN SUCESSFULL... PERSON CAN BOARD THE FLIGHT")
            print

        elif check.upper() == 'N' or check.upper() == 'NO':
            cur.execute("update PASSENGER set Sequerity_CheckIN=0 where PNR = " + "'" + PNR_entered + "'")
            conn.commit()
            print ("INVALID DETAILS....PERSON CAN NOT BOARD THE FLIGHT.")
            print

        else:
            print ("INVALID INPUT.....AUTOMATICALLY EXITED")
            print

        return

def FlightStaff():
    while 1:

        flight_no_entered = raw_input("Please Enter the Flight number: ")

        validate_flight_no_is_int(flight_no_entered)

        df = pd.read_sql_query("Select * from PASSENGER where Sequerity_CheckIN = 1 and flight_no = " + flight_no_entered + " ORDER BY TRIM(F_NAME) ASC, TRIM(L_NAME) ASC", conn)

        val = validate_flight_no(df, flight_no_entered)
        if(val == 1):
            continue
        if(val == 2):
            return

        print (df)
        print

        check = raw_input("Do you want to proceed with deletion of passengers details [Y/N]: ")

        if check.upper() == 'Y' or check.upper() == 'YES':
            cur.execute("delete from PASSENGER where flight_no=" + flight_no_entered)
            conn.commit()
            print ("SUCESSFULLY DELETED...")
            print

        elif check.upper() == 'N' or check.upper() == 'NO':
            print ("DELETION CANCELED...")
            print

        else:
            print ("INVALID INPUT.....AUTOMATICALLY EXITED")
            print

        return

def web_checkin(df, PNR_entered):
    cur.execute("update PASSENGER set WEB_CheckIN=1 where PNR = " + "'" + PNR_entered + "'")
    conn.commit()
    print ("WEB CHECKIN SUCESSFULL.....")
    print

def check_status():

    while 1:

        PNRentered = raw_input("Enter your unique 6 character PNR: ")
        last_name = raw_input("Enter your LAST NAME: ")

        df_pgr = pd.read_sql_query("Select * from PASSENGER where PNR = " + "'" + PNRentered + "'", conn)

        val = validate_pnr(df_pgr, PNRentered)
        if val == 1:
            continue
        if val == 2:
            close_db(conn, cur)
            sys.exit()

        val_lname = validate_last_name(df_pgr, last_name)
        if val_lname == 1:
            continue
        if val_lname == 2:
            close_db(conn, cur)
            sys.exit()

        df_flight = pd.read_sql_query("Select * from FLIGHT where FlightID = " + str(df_pgr['flight_no'][0]), conn)
        df_airline = pd.read_sql_query("Select * from AIRLINE where AirlineID = " + str(df_flight['AirlineID'][0]), conn)

        col_pgr = ['Sequerity_CheckIN', 'WEB_CheckIN', 'flight_no']
        df_pgr.drop(col_pgr, axis=1, inplace=True)

        col_flight = ['FlightID', 'AirlineID']
        df_flight.drop(col_flight, axis=1, inplace=True)

        df_airline.drop('AirlineID', axis=1, inplace=True)

        df = pd.concat([df_pgr, df_airline, df_flight], axis=1)

        return df, PNRentered

def show_available_src_dests(df_flight):
    cols = ['Source', 'Destination']
    print ("Flights are available between following locations:")
    print (df_flight.drop_duplicates(subset = cols)[cols].to_string(index = False))
    print

def random_generator():
    size = 6
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))

def generate_pnr():
    df_pnr = pd.read_sql_query("Select PNR from PASSENGER", conn)
    df_pnr = df_pnr.T.squeeze()

    while 1:
        pnr_gen = random_generator()
        if pnr_gen in set(df_pnr):
            continue
        return pnr_gen

def new_booking():

    df_flight = pd.read_sql_query("Select * from FLIGHT", conn)

    show_available_src_dests(df_flight)

    source_entr = raw_input("Enter your Source Name: ").upper()
    dest_entr = raw_input("Enter your Destination Name: ").upper()

    avl_flights = df_flight[(df_flight['Source'] == source_entr) & (df_flight['Destination'] == dest_entr)]

    if (len(avl_flights.index) == 0):
        print ("No Flights are available between {0} and {1}".format(source_entr, dest_entr))
        print
        return

    df_airline = pd.read_sql_query("Select * from AIRLINE", conn)
    df_airline.set_index('AirlineID',  inplace=True)

    avl_flights = avl_flights.join(df_airline, on='AirlineID')
    avl_flights.drop('AirlineID', axis=1, inplace=True)

    print (avl_flights.to_string(index=False))
    print

    flight_no_entr = raw_input("Enter the Flight Id you want to book: ")

    validate_flight_no_is_int(flight_no_entr)
    if not (avl_flights['FlightID'] == int(flight_no_entr)).any():
        print ("INVALID FLIGHT NUMBER...BOOKING CANCELED")
        return

    f_name = raw_input("Your First Name: ").upper()
    is_alpha(f_name)

    l_name = raw_input("Your Last Name: ").upper()
    is_alpha(l_name)

    age = raw_input("Your AGE: ")
    validate_flight_no_is_int(age)

    pnr = generate_pnr()

    values = (pnr, f_name, l_name, age, 0, flight_no_entr, 0)
    cur.execute("INSERT INTO PASSENGER VALUES (?,?,?,?,?,?,?)", values)
    conn.commit()

    print ("Booking Sucessfull...Your Ticket is:")
    print

    df_pgr = pd.read_sql_query("Select PNR, F_NAME, L_NAME, flight_no from PASSENGER where PNR = " + "'" + pnr + "'", conn)
    df_pgr.set_index('flight_no',  inplace=True)

    avl_flights = avl_flights[avl_flights['FlightID'] == int(flight_no_entr)]
    avl_flights = avl_flights.join(df_pgr, on='FlightID')
    cols = ['FlightID', 'SIZE']
    avl_flights.drop(cols, axis=1, inplace=True)

    print (avl_flights.to_string(index=False))
    print

def show_flight_to_fro():
    df_flight = pd.read_sql_query("Select * from FLIGHT", conn)
    show_available_src_dests(df_flight)

    loc = raw_input("Enter the name of location to which you want to come or go: ").upper()

    avl_flights = df_flight[(df_flight['Source'] == loc) | (df_flight['Destination'] == loc)]

    if (len(avl_flights.index) == 0):
        print ("No Flights come and go from {0}".format(loc))
        print
        return

    print ("These are the avaiable flights at max 10 flights will be displayed:")
    print (avl_flights.head(10).to_string(index=False))
    print

    query = raw_input("Do you want to see all the flights come and go from this airport [Y/N]: ")

    val = check_query(query)
    if val == 1:
        print (avl_flights.to_string(index=False))
        print

def passenger():

    print ("Want to know the flight details enter: 1")
    print ("For WEB CHECKIN enter: 2")
    print ("New Booking enter: 3")
    print ("Want to know the flights come and go from some specific airport enter: 4")
    print

    entered = raw_input()

    if entered == '1':
        df, PNRentered = check_status()
        print (df)
        print

    elif entered == '2':
        df, PNRentered = check_status()
        web_checkin(df, PNRentered)

    elif entered == '3':
        new_booking()

    elif entered == '4':
        show_flight_to_fro()

    else:
        print ("INVALID INPUT.....AUTOMATICALLY EXITED")
        print

if __name__ == "__main__":

    conn, cur = connect_to_db()

    print ("Who are you?---->")
    print ("Security Personnel please enter: S")
    print ("Flight Staff please enter: F")
    print ("Passengers please Enter: P")
    print

    query = raw_input()

    if query.upper() == 'S':
        SequerityPersonnel()

    elif query.upper() == 'F':
        FlightStaff()

    elif query.upper() == 'P':
        passenger()

    else:
        print ("INVALID INPUT.....AUTOMATICALLY EXITED")
	print

    close_db(conn, cur)

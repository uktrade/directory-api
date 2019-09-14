import psycopg2
import sys
import argparse
text = 'This script will update SSO or Directory API databases with exported data from ExOpps database. We need to connect to SSO or API database via cf conduit, then pass username/password/db_name from conduit to this script.'

# enquiries exopps DB input file structure
# "first_name","last_name","uid","company_telephone","company_name","company_address","company_address2","company_address3","company_house_number","company_postcode","company_url","email","data_protection","enquiries.created_at"

def main():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="show program version", action="store_true")

    parser.add_argument("-c", "--connection_mode", help="connection mode, SSO or API")
    parser.add_argument("-u", "--username", help="username from conduit")
    parser.add_argument("-p", "--password", help="password from conduit")
    parser.add_argument("-d", "--db_name", help="db name from conduit")
    parser.add_argument("-e", "--exopps_file", help="exopps file to load")

    args = parser.parse_args()

    if args.version:
        print("this is myprogram version 0.1")
    elif args.connection_mode and args.username and args.password and args.db_name and args.exopps_file:
        import pdb;pdb.set_trace()
        # usage python script.py <MODE> <USERNAME> <PASSWORD> <DBNAME> <EXOPPS_DB>
        connection_mode = args.connection_mode
        username = args.username
        password = args.password
        db_name = args.db_name
        exopps_db = args.exopps_file #enquiries_sso_data_20190902.csv

        if args.version:
            print("this is myprogram version 0.1")

        # read enquiries file, fetch the most recent enquiry per user
        enquiries_file = open(exopps_db, "r")
        enquiries = enquiries_file.readlines()[1:]
        users_dict = {}
        for enquiry in enquiries:
            user = enquiry.split(',')[2]
            # if we have not added this user's enquiry to the dictionary, do it now.
            # enquiries are sorted by created_at desc, so the first enquiry that we encounter will be the most recent one
            if user not in users_dict:
                users_dict[user] = enquiry.replace('"','').split(',')
        for uu in users_dict.values():
            first_name = uu[0]
            last_name  = uu[1]
            uid = uu[2]
            company_telephone = uu[3]
            company_name = uu[5]
            company_address = uu[5]
            company_address2 = uu[6]
            company_address3 = uu[7]
            company_house_number = uu[9]
            company_postcode = uu[10]
            company_url = uu[11]
            email = uu[12]


            # update Database
            cur = connection(username=username, password=password, db_name=db_name)
            if connection_mode == 'SSO':
                # TODO: test this
                import pdb;pdb.set_trace()
                cur.execute("update user_userprofile set first_name=%s, last_name=%s where user_id=%s", (first_name, last_name, uid))


            elif connection_mode == 'API':
                #TODO: what about company_house_number? where is it stored? what's user_user in directory_API? we have user_userprofile in SSO already.
                import pdb;pdb.set_trace()
                cur.execute("UPDATE company_company SET mobile_number=%s, name=%s, address_line_1=%s, address_line_2=%s, po_box=%s,  "
                            "WHERE id IN (SELECT company_company.id FROM company_company JOIN supplier_supplier ON supplier_supplier.company_id=company_company.id WHERE supplier_supplier.sso_id=%s)",
                            (company_telephone, company_name, company_address, company_address2, company_postcode, uid))
    enquiries_file.close()

def connection(db_name, username, password):
    conn = psycopg2.connect(database=db_name,
                            user=username,
                            password=password,
                            host= "127.0.0.1",
                            port="7080") # default conduit port
    return conn.cursor()


if __name__=="__main__":
    main()


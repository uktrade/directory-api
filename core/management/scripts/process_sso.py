import psycopg2
import sys
import argparse
from io import StringIO

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
            user = enquiry.split('\t')[2]
            # if we have not added this user's enquiry to the dictionary, do it now.
            # enquiries are sorted by created_at desc, so the first enquiry that we encounter will be the most recent one
            if user not in users_dict:
                users_dict[user] = enquiry

        # temp vars
        hit = 0
        miss = 0

        _sso_user_present = 0
        _sso_user_not_present = 0

        _api_user_present = 0
        _api_user_not_present = 0


        # open connection to DB
        cur = connection(username=username, password=password, db_name=db_name)
        for uu in users_dict.values():
            # import pdb;pdb.set_trace()
            uu = uu.split('\t')
            first_name = uu[0]
            last_name  = uu[1]
            uid = uu[2]
            company_telephone = uu[3]
            company_name = uu[4]
            company_address = uu[5]
            # company_address2 = uu[6]
            # company_address3 = uu[7]
            company_house_number = uu[6]
            company_postcode = uu[7]
            company_url = uu[8]
            email = uu[9]


            # update Database

            if connection_mode == 'SSO':
                # TODO: test this
                if "@" in email:
                    hit = hit + 1
                else:
                    miss = miss + 1
                print(email)

                # try to find the user in SSO

                _uid = int(uid)
                cur.execute("select count(*) from user_userprofile where user_id=%s", [_uid])
                res = cur.fetchone()
                # if the user is not present, create him/her & count
                if res[0] == 0:
                    _sso_user_not_present = _sso_user_not_present + 1

                    # uncomment to insert the user
                    # cur.execute("insert into user_userprofile values(%s, %s, %s)", (first_name,last_name,uid))

                # else count that the user is already present
                else:
                    _sso_user_present = _sso_user_present + 1
                    # cur.execute("update user_userprofile set first_name=%s, last_name=%s where user_id=%s", (first_name, last_name, uid))


            elif connection_mode == 'API':
                print(f'now processing {email}')

                #TODO: what about company_house_number? where is it stored? what's user_user in directory_API? we have user_userprofile in SSO already.
                # import pdb;pdb.set_trace()
                _uid = int(uid)
                cur.execute("SELECT count(company_company.id) FROM company_company JOIN supplier_supplier ON supplier_supplier.company_id=company_company.id WHERE supplier_supplier.sso_id=%s", [_uid])
                res = cur.fetchone()
                # if the company is not present, create him/her & count
                if res[0] == 0:
                    _api_user_not_present = _api_user_not_present + 1
                    # cur.execute("INSERT INTO company_company(mobile_number, name, address_line_1, address_line_2, po_box, id) values(%s, %s, %s, %s, %s)", (company_telephone, company_name, company_address, company_address2, company_postcode, uid))
                else:
                    _api_user_present = _api_user_present + 1

                # cur.execute("UPDATE company_company SET mobile_number=%s, name=%s, address_line_1=%s, address_line_2=%s, po_box=%s,  "
                #             "WHERE id IN (SELECT company_company.id FROM company_company JOIN supplier_supplier ON supplier_supplier.company_id=company_company.id WHERE supplier_supplier.sso_id=%s)",
                #             (company_telephone, company_name, company_address, company_address2, company_postcode, uid))
        print(f'{hit} hits and {miss} misses')
        print(f'{_sso_user_present} users present and {_sso_user_not_present} users NOT present to update in SSO') #41 users    present and 16618 users NOT present to update in SSO
        print(f'{_api_user_present} users present and {_api_user_not_present} users NOT present to update in API') #174 users present and 16485 users NOT present to update in API


    # cur.connection.close()
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


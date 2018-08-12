'''
Created on Nov 13, 2017

@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from psycopg2 import connect
from psycopg2.extras import DictCursor
from api_config import config_database_connect
from api_log import log

def backfill(conn, cur, table, sql_template):
    cur.execute( 'select max(date) from %s' % ( table ) )
    rows = cur.fetchall()
    existing_date = rows[0][0];
    cur_date = existing_date + timedelta( days=1 )
    
    log.info("Backfilling from existing_date %s in %s" % ( existing_date, table ))
    while cur_date < cur_date.today():
        sql = sql_template % (cur_date, existing_date)
        cur.execute( sql );
        conn.commit()
        log.info("Backfilled %s" % ( cur_date ))
        cur_date = cur_date + timedelta( days=1 )
           
def main():
    log.info("Started...")
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)

    backfill(conn, cur, 'balances_history', "insert into balances_history (select '%s', type, value from balances_history where date='%s')" )
    backfill(conn, cur, 'index_history', "insert into index_history (select '%s', type, value from index_history where date='%s')" )
    backfill(conn, cur, 'divisors_history', "insert into divisors_history (select '%s', type, value from divisors_history where date='%s')" )
    backfill(conn, cur, 'portfolio_history', "insert into portfolio_history (select '%s', symbol, value, type, pricing_type, quantity, price from portfolio_history where date='%s')" )
    
    cur.close()
    conn.close()
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 
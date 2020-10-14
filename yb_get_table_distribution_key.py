#!/usr/bin/env python3
"""
USAGE:
      yb_get_table_distribution_key.py [database] [options]

PURPOSE:
      Identify the column name(s) on which this table is distributed.

OPTIONS:
      See the command line help message for all options.
      (yb_get_table_distribution_key.py --help)

Output:
      The columns comprising the distribution key are echoed out, one column
      name per line, in the order in which they were specified in the
      DISTRIBUTE ON ( )   clause.

      If the table is distributed on random (round-robin), then this script will
      simply return the string  RANDOM
"""

import sys

import yb_common
from yb_common import text


class get_table_distribution_key:
    """Issue the ybsql command used to identify the column name(s) on which
    this table is distributed.
    """

    def __init__(self, db_conn=None, db_filter_args=None):
        """Initialize get_table_distribution_key class.

        This initialization performs argument parsing and login verification.
        It also provides access to functions such as logging and command
        exec
        """
        if db_conn:
            self.db_conn = db_conn
            self.db_filter_args = db_filter_args
        else:
            self.args_handler = yb_common.args_handler(
                description=
                    'Identify the distribution column or type (random '
                    'or replicated) of the requested table.',
                required_args_single=['table'],
                optional_args_multi=['owner'])

            self.args_handler.args_process()
            self.db_conn = yb_common.db_connect(self.args_handler.args)
            self.db_filter_args = self.args_handler.db_filter_args

    def execute(self):
        filter_clause = self.db_filter_args.build_sql_filter(
            {'owner':'ownername','schema':'schemaname','table':'tablename'}
            , indent='    ')

        sql_query = """
WITH
tbl AS (
    SELECT
        DECODE(
            LOWER(t.distribution)
                , 'hash', t.distribution_key
                , UPPER(t.distribution)
        ) AS distribution
        , c.relname AS tablename
        , n.nspname AS schemaname
        , pg_get_userbyid(c.relowner) AS ownername
    FROM {database_name}.pg_catalog.pg_class AS c
        LEFT JOIN {database_name}.pg_catalog.pg_namespace AS n
            ON n.oid = c.relnamespace
        LEFT JOIN {database_name}.sys.table AS t
            ON c.oid = t.table_id
    WHERE
        c.relkind = 'r'::CHAR
)
SELECT
    distribution
FROM
    tbl
WHERE
    distribution IS NOT NULL
    AND {filter_clause}""".format(
             filter_clause = filter_clause
             , database_name = self.db_conn.database)

        self.cmd_results = self.db_conn.ybsql_query(sql_query)


def main():
    gtdk = get_table_distribution_key()
    gtdk.execute()

    if gtdk.cmd_results.stdout != '':
        if gtdk.cmd_results.stdout.strip() in ('RANDOM', 'REPLICATED'):
            sys.stdout.write(gtdk.cmd_results.stdout)
        else:
            sys.stdout.write(yb_common.common.quote_object_paths(gtdk.cmd_results.stdout))
    if gtdk.cmd_results.stderr != '':
        sys.stdout.write(text.color(gtdk.cmd_results.stderr, fg='red'))

    exit(gtdk.cmd_results.exit_code)


if __name__ == "__main__":
    main()
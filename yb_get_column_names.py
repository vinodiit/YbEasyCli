#!/usr/bin/env python3
"""
USAGE:
      yb_get_column_names.py [database] object [options]

PURPOSE:
      List the column names comprising an object.

OPTIONS:
      See the command line help message for all options.
      (yb_get_column_names.py --help)

Output:
      The column names for the object will be listed out, one per line.
"""

import sys

import yb_common


class get_column_names:
    """Issue the ybsql command used to list the column names comprising an
    object.
    """

    def __init__(self, common=None, db_args=None):
        """Initialize get_column_names class.

        This initialization performs argument parsing and login verification.
        It also provides access to functions such as logging and command
        execution.
        """
        if common:
            self.common = common
            self.db_args = db_args
        else:
            self.common = yb_common.common()

            self.db_args = self.common.db_args(
                description=
                    'List/Verifies that the specified column names exist.',
                optional_args_multi=['owner', 'column'],
                positional_args_usage='[database] object')

            self.common.args_process()

        self.db_conn = yb_common.db_connect(self.common.args)

    def execute(self):
        filter_clause = self.db_args.build_sql_filter({
            'owner':'tableowner'
            ,'schema':'schemaname'
            ,'object':'objectname'
            ,'column':'columnname'}
            , indent='    ')

        sql_query = """
WITH
objct AS (
    SELECT
        a.attname AS columnname
        , a.attnum AS columnnum
        , c.relname AS objectname
        , n.nspname AS schemaname
        , pg_get_userbyid(c.relowner) AS tableowner
    FROM {database_name}.pg_catalog.pg_class AS c
        LEFT JOIN {database_name}.pg_catalog.pg_namespace AS n
            ON n.oid = c.relnamespace
        JOIN {database_name}.pg_catalog.pg_attribute AS a
            ON a.attrelid = c.oid
    WHERE
        c.relkind IN ('r', 'v')
        AND a.attnum > 0
)
SELECT
    --'<database_name>.' || schemaname || '.' || objectname || '.' || columnname AS column_path
    columnname
FROM
    objct
WHERE
    objectname = '{object_name}'
    AND {filter_clause}
ORDER BY
    LOWER(schemaname), LOWER(objectname), columnnum""".format(
             filter_clause = filter_clause
             , database_name = self.db_conn.database
             , object_name = self.common.args.object)

        self.cmd_results = self.db_conn.ybsql_query(sql_query)


def main():
    gcns = get_column_names()
    gcns.execute()

    gcns.cmd_results.write(quote=True)

    exit(gcns.cmd_results.exit_code)


if __name__ == "__main__":
    main()
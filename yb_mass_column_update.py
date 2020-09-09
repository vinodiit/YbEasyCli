#!/usr/bin/env python3
"""
USAGE:
      yb_mass_column_update.py [database] [options]

PURPOSE:
      Update the value of multiple columns.

OPTIONS:
      See the command line help message for all options.
      (yb_mass_column_update.py --help)

Output:
      The update statements for the requested set of columns.
"""

import sys

import yb_common


class mass_column_update:
    """Issue the ybsql command used to list the column names comprising an
    object.
    """

    def __init__(self):

        common = self.init_common()

        filter_clause = self.db_args.build_sql_filter(
            {
                'owner':'tableowner'
                , 'schema':'schemaname'
                , 'table':'tablename'
                , 'column':'columnname'
                , 'datatype':'datatype'}
                , indent='        ')

        sys.stdout.write('-- Running mass column update.\n')

        cmd_results = common.call_stored_proc_as_anonymous_block(
            'yb_mass_column_update_p'
            , args = {
                'a_update_where_clause' : common.args.update_where_clause
                , 'a_set_clause' : common.args.set_clause
                , 'a_column_filter_clause' : filter_clause
                , 'a_exec_updates' : ('TRUE' if common.args.exec_updates else 'FALSE')}
            , pre_sql = common.args.pre_sql
            , post_sql = common.args.post_sql)

        cmd_results.write(tail='-- Completed mass column update.\n')

        exit(cmd_results.exit_code)

    def add_args(self, common):
        common.args_process_init(
            description=(
                'Update the value of multiple columns.'
                '\n'
                '\nnote:'
                '\n  Mass column updates may cause performance issues due to the change '
                '\n  of how the data is ordered in storage.'))

        common.args_add_positional_args()
        common.args_add_optional()
        common.args_add_connection_group()

        args_mass_r_grp = common.args_parser.add_argument_group('mass update required arguments')
        args_mass_r_grp.add_argument(
            "--update_where_clause", required=True
            , help=("update column only if this boolean clause is satisfied, like: "
                "'LENGTH(<columnname>)<>LENGTH(RTRIM(<columnname>))',  "
                "Note: the special use of the string '<columnname>' ")
        )
        args_mass_r_grp.add_argument(
            "--set_clause", required=True
            , help=("Set the column to this value, Like; "
                "'RTRIM(<columnname>)', "
                "Note: the special use of the string '<columnname>' ")
        )

        args_mass_o_grp = common.args_parser.add_argument_group('mass update optional arguments')
        args_mass_o_grp.add_argument(
            "--exec_updates"
            , action='store_true'
            , help=("defaults to False and only prints the update statements. When set "
                "to True, execute the update statements.")
        )
        args_mass_o_grp.add_argument("--pre_sql", default=''
            , help="SQL to run before the chunking DML, only runs if execute_chunk_dml is set")
        args_mass_o_grp.add_argument("--post_sql", default=''
            , help="SQL to run after the chunking DML, only runs if execute_chunk_dml is set")

        self.db_args = yb_common.db_args(
            optional_args_multi=['owner', 'schema', 'table', 'column', 'datatype']
            , required_args_single=[], optional_args_single=[], common=common)

    def init_common(self):
        """Initialize common class.

        This initialization performs argument parsing and login verification.
        It also provides access to functions such as logging and command
        execution.

        :return: An instance of the `common` class
        """
        common = yb_common.common()

        self.add_args(common)

        common.args_process()

        self.db_args.schema_set_all_if_none()

        if '<columnname>' not in common.args.update_where_clause:
            sys.stderr.write("UPDDATE_WHERE_CLAUSE must contain the string '<columnname>'\n")
            exit(1)

        if not common.args.exec_updates:
            common.args.pre_sql = ''
            common.args.post_sql = ''

        return common

mass_column_update()

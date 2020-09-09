test_cases = [
    test_case(
        cmd='yb_get_table_name.py @{argsdir}/db1 --current_schema dev --table a1_t --'
        , exit_code=0
        , stdout="""a1_t"""
        , stderr='')

    , test_case(
        cmd='yb_get_table_name.py @{argsdir}/db1 --schema dev --table a1_t --'
        , exit_code=0
        , stdout='a1_t'
        , stderr='')

    , test_case(
        cmd=(
            'yb_get_table_name.py @{argsdir}/db1 --current_schema dev --schema '
            "'Prod' --table b1_t --")
        , exit_code=0
        , stdout='b1_t'
        , stderr='')

    , test_case(
        cmd=(
            """yb_get_table_name.py @{argsdir}/db1 --current_schema dev --schema """
            """'Prod' --table "C1_t" -- {db2} """)
        , exit_code=0
        , stdout='"C1_t"'
        , stderr='')

    , test_case(
        cmd=(
            """yb_get_table_name.py @{argsdir}/db1 --current_schema dev --schema """
            """'Prod' --table "C1_t" -- {db2} extra_pos_arg""")
        , exit_code=2
        , stdout=''
        , stderr="""usage: yb_get_table_name.py [database] [options]
yb_get_table_name.py: error: unrecognized arguments: extra_pos_arg""")
]
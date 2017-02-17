NO_CASE_STUDIES = 'no_case_studies'
HASNT_LOGGED_IN = 'hasnt_logged_in'
VERIFICATION_CODE_NOT_GIVEN = 'verification_code_not_given'
VERIFICATION_CODE_2ND_REMINDER = 'verification_code_2nd_reminder'
SUPPLIER_NOTIFICATION_CATEGORIES = (
    (NO_CASE_STUDIES, 'Case studies not created'),
    (HASNT_LOGGED_IN, 'Not logged in after first 30 days'),
    (VERIFICATION_CODE_NOT_GIVEN, 'Verification code not supplied'),
    (VERIFICATION_CODE_2ND_REMINDER,
        'Verification code not supplied - 2nd reminder'),
)


NEW_COMPANIES_IN_SECTOR = 'new_companies_in_sector'
BUYER_NOTIFICATION_CATEGORIES = (
    (NEW_COMPANIES_IN_SECTOR, 'New companies in sector'),
)

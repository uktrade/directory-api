# Changelog

## Pre release

### Implemented enhancements
- TT-1733 - Added request identity verification feature
- TT-1733 - Allow name to be provided on supplier create
- TT-1716 - Allow disconnecting self from company
- TT-1727 - Consolidate collaboration models in backwards compatible way.
- TT-1734 - Allow adding second user as member to a company profile
- TT-1716 - Company search stop words
- TT-1761 - Remove fab casestudies notification
- TT-1727 - Allow changing role of collaborator
- TT-1748 - Allow anonymous user retrieving collaboration invite
- No ticket - Refactor makefile and speed up tests
- No ticket - Remove mobile number unique constraint
- TT-1714 - Implement Collaborator Notifications 
- TT-1841 - Send admin emails for exiting company in signals 
- TT-1761 - Remove notification hasn't logged-in
- TT-1923 - allow to programmatically change verification flags via testapi
- TT-1910 - admin send new invite accepted email
- TT-1911 - Expose created timestamp for company serializer
- TT-2012 - Add non-ch request verification email
- TT-2013 - Generate company number for all non registered companies
- TT-2027 - Make testapi to return company number (for testing non-CH companies)
- TT-2143 - Tech debt refactor: removed user.User, introduced company.CompanUser, and deprecated supplier.Supplier

## Breaking changes
- TT-1538 - AWS-S3 Pass Bucket setup - Pass is required to be setup in target env and set env variable.
    ENSURE TO SET DATASCIENCE AWS SETTINGS IN VAULT
 
### Fixed bugs
- No ticket - Upgrade django to 1.11.23 to fix vulnerability
- TT-1768 - Fix elasticsearch migrate
- TT-1538  - Fix datascience s3 bucket - read from vault see above
- TT-1289 - Allow company names longer than 250 chars
- TT-2011 - Handle verified with id
- TT-2064 - Submit user details with request to verify

## [2019.08.12](https://github.com/uktrade/directory-api/releases/tag/2019.08.12)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.07.15..2019.08.12)

### Implemented enhancements
- TT-1619 - Sending New Registration Letters new env FEATURE_REGISTRATION_LETTERS_ENABLED
- no ticket - Increase flake8 Char limit to 120
- TT-851 - Companies house status check admin upgrade
- TT-1613 Reduce stannp to flag errors from <50 to <10 
- TT-1697 - SSO integration (setup ENVS STAFF_SSO_AUTHBROKER_URL/AUTHBROKER_CLIENT_ID/AUTHBROKER_CLIENT_SECRET, ENFORCE_STAFF_SSO_ON) 
- TT-1700 - Show error when user doesn't have staff status
- TT-1735 - Forms & Directory-API SSO display message for 1st time users

## [2019.07.15](https://github.com/uktrade/directory-api/releases/tag/2019.07.15)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.06.25...2019.07.15)

### Implemented enhancements

- No ticket - Moved over GDS PaaS S3 bucket.
- TT-1574 - Support more non-companies house companies
- TT-1590 - Port ISD search logic to FAS
- No ticket - Remove obsolete case study search endpoint
- No ticket -  Mask product data make email unique
- No ticket - Upgrade vulnerable django version to django 1.11.22

### Fixed bugs
- No ticket - Fixed migrations during deployment

## [2019.06.25](https://github.com/uktrade/directory-api/releases/tag/2019.06.25)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.05.23...2019.06.25)

### Implemented enhancements
- TT-1491 Adding sorting via title and more relevance to query that matches in titles
- TT-1459 Added testapi endpoint to create ISD companies which are used in automated tests
- TT-1558 Add managment command to mask personal company data
- No-ticket move factory-boy to requirement.in and upgrade django to 1.11.21

### Fixed bugs
- No ticket - Upgraded djangorestframework to resolve security vulnerability
- No ticket - Upgraded directory-client-core to fix inconsistency in cache.
- TT-1438 - Allow searching for companies via case study attributes
- TT-1438 - Add website Testimonial to CaseStudySearch

## [2019.05.23](https://github.com/uktrade/directory-api/releases/tag/2019.05.23)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.05.16...2019.05.23)

### Fixed bugs

- TT-1480 - Fixed pagination
- TT-1463 - Improved ordering of companies that match multiple filters
- TT-1481 - Allow searching via expertise fields in term

## [2019.05.16](https://github.com/uktrade/directory-api/releases/tag/2019.05.16)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.05.09...2019.05.16)

### Implemented enhancements
- TT-1408 - Customize ISD search results order.

### Fixed bugs:
- TT-7 - Fixed Server Error (500) when searching for pre-verified enrolments
- Replaced is_published field in fixtures/development.json from is_published_investment_support_directory & is_published_find_a_supplier
- TT-1438 - Fixed inability to search by case study contents.
- TT-1472 - Fixed unwanted partial matches of expertise filters

## [2019.05.09](https://github.com/uktrade/directory-api/releases/tag/2019.05.09)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.04.08...2019.05.09)

### Implemented enhancements
- Upgraded Elasticsearch from 5 to 6
- TT-1317 - Added feature to bulk upload expertise from django admin
- TT-1348 - Added Investment Support Directory search endpoint
- TT-1398 - Populate products and services from keywords
- TT-1428 - fixed 404 ,allow investment support directory companies and FAS to return a profile.
- TT-1446 - Added new testapi endpoint to discover unpublished companies & extra details to testapi responses in order to facilitate automated testing for pre-verified companies.

### Fixed bugs:

- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)

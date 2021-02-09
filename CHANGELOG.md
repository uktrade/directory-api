# Changelog

## Pre release

### Implemented enhancements

- GP2-1344 - Added API for trading blocs
- GP2-1392 - lock down public data access

### Bugs fixed


## [1.3.0](https://github.com/uktrade/directory-api/releases/tag/1.3.0)
[Full Changelog](https://github.com/uktrade/directory-api/compare/1.2.0...1.3.0)

### Implemented enhancements

- GP2-1343 - Added Trading blocs data
- GP2-1348 - Economy and population raw values and rank totals
- GP2-1264 - Added currencies data
- GP2-1267 - Added Rule of Law data
- GP2-1258 - Society data
- GP2-1270 - Imported Income data
- GP2-1218 - Country data alignment
- GP2-173 - Updated Male population CSV
- GP2-1068 - Apply black and isort autoformatting to codebase incl makefile additions
- GP2-1063 - Moved SuggestedCountries under dataservices app
- GP2-1025 - Refactor economy data from ComTrade
- GP2-849 - add total pop
- GP2-849 - add internet usage total
- GP2-285 - cost and price be
- GP2-1359 - add funding fields
- NOTICKET - Add export plan data to admin
- GP2-1139 - save EP progress
- NOTICKET - inner dict update by key for json fields
- GP2-1382 - getting paid structure
- GP2-1180 - travel bus BE
 
### Bugs fixed

- GP2-1347 - Stop missing CPI or internet usage data from blowing up
- GP2-1391 - US missing from cpi
- GP2-1314 - ComTrade World import value fix

## [1.1.0](https://github.com/uktrade/directory-api/releases/tag/1.1.0)
[Full Changelog](https://github.com/uktrade/directory-api/compare/1.0.0...1.1.0)

### Implemented enhancements
- GP2-1069 - Added deprecation warning for user profile fields
- GP2-1147 - Added  management command to import GDP Per Capita Data
- GP2-1025 - New endpoint for getting economy data from ComTrade
- GP2-849 - target audience progress


## [1.0.0](https://github.com/uktrade/directory-api/releases/tag/1.0.0)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2020.05.21...1.0.0)

### Implemented enhancements

- No ticket - change PopulationByCountry endpoint request parameter to plural
- GB2-918 - Added Internet Usage and CPI data for PopulationByCountry endpoint
- GBAU-61 - Added company endpoint for consumption by activity stream
- GP2-510 - Added Suggested Countries model and relevant data
- GP-96 - HS Codes saved on Country
- GP2-113 - Remove company objectives update from export plan update, add delete to objective update endpoint
- MVP-581 - new objective fields
- MVP-432 - error on none-found companies
- No Ticket - remove redudant field on model
- GP2-125 - Add business objectives rest CRUD api
- GP2-154 - update country list
- GP2-168 - CIA Fackbook load data
- GP2-169 - WEO load data world economic  (view/management)
- no-ticket - fix codecov status stuck
- GP2-187 - pull views cia-factbook
- GP2-183 - load internet access data from world bank
- GP2-244 - load internet consumer price index data from world bank
- GP2-245 - generic view for CIA factbook
- GP2-188 - population data from UN
- GP2-316 - rename json field from target markets to market approach
- GP2-315 - route-to-market model/view new api
- GP2-393 - model changes adaption target markets fields
- GP2-395 - add target market documents
- GP2-545 - remove airtable dependency
- GP2-543 - country name mapping to improve lookup
- GP2-706 - rename rational to objectives
- GP2-699 - swamp route to market constants
- Noticket - update-admin
- Noticket - upgrade-es-7
- Noticket - allow partial updates json fields



### Bugs fixed
- GP2-872 - Reverse order of suggested markets
- No ticket - Migration fix for new build
- No ticket - Upgrade django and markdown to fix security vulnerability
- No Ticket - Faker spamming log message - only passing error message
- No Ticket - Migration leaf node
- GP2-360 - un-data match
- No Ticket - fix route to markets choices make optional
- no commodity code make optional

## [2020.05.21](https://github.com/uktrade/directory-api/releases/tag/2020.05.21)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2020.02.04_1...020.05.21)

### Implemented enhancements
No ticket - v3-cipipeline manifest.yml file fix
TT-2253 - Detect duplicate companies
TT-2223 - Handle preverified company multiple users
No ticket - List company users in Company admin
TT-2286 - update test email domain
MVP - Add personalisation APIs
MVP-108 - export-plan-saving
MVP-108 - export-plan-saving - add rules and regulations
MVP-147 - Allow for piecemeal company creation
MVP-205 - extend export plan model
MVP - Add Lat/Lng lookup to Personalisation Events API
MVP-250 - EaseofBusiness Index Backend
MVP-252 - CPI data import backend
MVP - Add search term to Personalisation ExOps API
MVP-276 - comtrade download component
MVP-310 - comtrade pull api-views
MVP-279 - support export actions
MVP-319 - support for update/create lists (actions/objectives)
MVP-323 - Recommended Country End Point
MVP-363 - move MADB Airtable to backend
MVP-359 - add multiple target countries preload
MVP-369 - save historical data on safe signal
MVP-386 - add country TZ
MVP-387 - add commodity name to target markets
MVP-398 - feature flag historical data
MVP-416 - Personalise events by user sector and country of interest
MVP-395 - cache comtrade data using backend cache
MVP-479 - Brand Product Details
MVP-474 - pre-populate dataservices cache task

### Fixed bugs
TT-2254 - Cleaned up obsolete settings
no ticket - Django vulnerability upgrade
TT-2260 - Include email address when creating preverified links


## [2020.02.04_1](https://github.com/uktrade/directory-api/releases/tag/2020.02.04_1)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2020.02.04...2020.02.04_1)

## Hotfix
- No ticket - Fix company user deletion


## [2020.02.04](https://github.com/uktrade/directory-api/releases/tag/2020.02.04)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2020.01.14...2020.02.04)

## Hotfix
- No ticket - CVE-2020-5236 & CVE-2020-7471: Potential SQL injection via StringAgg(delimiter)


## [2020.01.14](https://github.com/uktrade/directory-api/releases/tag/2020.01.14)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.12.18...2020.01.14)

### Implemented enhancements
TT-2234 - upgrade staff-sso to allow id rather then email/username
no-ticket - upgrade waitress vulnerability
TT-2248 - Facilitate .internal domain communication
TT2247 - verification confirmation

### Fixed bugs
TT-2220 sent-verification-letters-in-error
TT-2165 send user accept/decline new admin request
TT-1624 send admin new admin request email
TT-2216 - TestApi: add endpoint to delete buyers created by automated tests

## [2019.12.18](https://github.com/uktrade/directory-api/releases/tag/2019.12.18)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.12.04_1...2019.12.18)

### Fixed bugs
No ticket - Remove obsolete code
No ticket - change admin confirm url

## [2019.12.04_1](https://github.com/uktrade/directory-api/releases/tag/2019.12.04_1)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.12.04...2019.12.04_1)

### Hotfix
- No ticket - wait for migrations before starting celery beat

## [2019.12.04](https://github.com/uktrade/directory-api/releases/tag/2019.12.04)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.10.22...2019.12.04)

### Implemented enhancements
- TT-2027 - Make testapi to return company number (for testing non-CH companies)
- TT-2143 - Tech debt refactor: removed user.User, introduced company.CompanUser, and deprecated supplier.Supplier
- TT-2194 - TestApi: add endpoint to get buyer details by email
- TT-2187 - Add django admin filters for GDPR, publish place and verification method
- TT-2198 - TestApi: add endpoint to delete companies created by automated tests
- TT-1304 - Upgrade sentry client
- TT-2216 - TestApi: add endpoint to delete buyers created by automated tests

### Fixed bugs
- TT-2064 - Submit user details with request to verify
- TT-2168 - Expose company user name in registration email
- no ticket - Upgrade django
- TT-2145 - validate non-companies-house-companies address during bulk create
- no ticket - fix redis after upgrade: removed rediss -> redis workaround
- TT-2202 - Fix enrolment

## [2019.10.22](https://github.com/uktrade/directory-api/releases/tag/2019.10.22)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.08.22...2019.10.22)

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

## Breaking changes
- TT-1538 - AWS-S3 Pass Bucket setup - Pass is required to be setup in target env and set env variable.
    ENSURE TO SET DATASCIENCE AWS SETTINGS IN VAULT

### Fixed bugs
- No ticket - Upgrade django to 1.11.23 to fix vulnerability
- TT-1768 - Fix elasticsearch migrate
- TT-1538  - Fix datascience s3 bucket - read from vault see above
- TT-1289 - Allow company names longer than 250 chars
- TT-2011 - Handle verified with id

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

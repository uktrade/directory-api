# Changelog

### Implemented enhancements
- [TT-1408] Customize ISD search results order.

### Fixed bugs:
- [TT-7] Fixed Server Error (500) when searching for pre-verified enrolments

- Replaced is_published field in fixtures/development.json from is_published_investment_support_directory & is_published_find_a_supplier

- [TT-1438] Fixed inability to search by case study contents.

## [2019.05.09](https://github.com/uktrade/directory-api/releases/tag/2019.05.09)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.04.08...2019.05.09)

### Implemented enhancements
- Upgraded Elasticsearch from 5 to 6
- [TT-1317] Added feature to bulk upload expertise from django admin
- [TT-1348] Added Investment Support Directory search endpoint
- [TT-1398] Populate products and services from keywords
- [TT-1428] fixed 404 ,allow investment support directory companies and FAS to return a profile.
- [TT-1446] Added new testapi endpoint to discover unpublished companies & extra details to testapi responses in order to facilitate automated testing for pre-verified companies.

### Fixed bugs:

- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)

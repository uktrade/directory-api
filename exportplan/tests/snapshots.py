BUILD_QUERY_SNAPSHOT = """
        SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'about_your_business' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.about_your_business)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'business_objectives' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.objectives)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'target_markets_research' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.target_markets_research)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'adapting_your_product' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.adaptation_target_market)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'marketing_approach' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.marketing_approach)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'costs_and_pricing' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.direct_costs)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'costs_and_pricing' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.overhead_costs)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'costs_and_pricing' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.total_cost_and_price)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'funding_and_credit' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.funding_and_credit)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'getting_paid' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.getting_paid)
UNION
SELECT
            id as exportplan_id,
            sso_id,
            created,
            modified,
            'travel_plan' as section,
            key as question
        FROM
        exportplan_companyexportplan,
        jsonb_each_text(exportplan_companyexportplan.travel_business_policies)
        UNION
        SELECT
            exportplan_companyexportplan.id,
            sso_id,
            exportplan_companyexportplan.created,
            exportplan_companyexportplan.modified,
            'Business risk' as section,
            'business_risk' as question
        FROM
            exportplan_companyexportplan
        RIGHT JOIN
            exportplan_businessrisks
        ON
            exportplan_companyexportplan.id = exportplan_businessrisks.companyexportplan_id
        WHERE
            (
                (
                    exportplan_companyexportplan.id > 123
                    AND exportplan_companyexportplan.modified = '2022-07-01T15:19:11.031368'::timestamptz
                )
                OR exportplan_companyexportplan.modified > '2022-07-01T15:19:11.031368'::timestamptz
            )
        ORDER BY
            modified ASC,
            exportplan_id ASC;
"""

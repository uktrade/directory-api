from company.tests.factories import CompanyCaseStudyFactory, CompanyFactory


def test_remove_bad_images_from_company(migration):
    app = 'company'
    model_name = 'Company'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good = [
        CompanyFactory.create(logo='thing.png'),
        CompanyFactory.create(logo='thing.jpg'),
        CompanyFactory.create(logo='thing.svg'),
        CompanyFactory.create(logo=''),
    ]
    bad = [
        CompanyFactory.create(logo='thing.pdf'),
        CompanyFactory.create(logo='thing.wav'),
        CompanyFactory.create(logo='thing.js'),
    ]

    migration.apply('company', '0032_remove_bad_images')

    for item in good:
        expected = str(item.logo)
        item.refresh_from_db()
        assert str(item.logo) == expected

    for item in bad:
        item.refresh_from_db()
        assert str(item.logo) == ''


def test_remove_bad_images_from_case_study_image_one(migration):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good = [
        CompanyCaseStudyFactory.create(image_one='thing.png'),
        CompanyCaseStudyFactory.create(image_one='thing.jpg'),
        CompanyCaseStudyFactory.create(image_one='thing.svg'),
        CompanyCaseStudyFactory.create(image_one=''),
    ]
    bad = [
        CompanyCaseStudyFactory.create(image_one='thing.pdf'),
        CompanyCaseStudyFactory.create(image_one='thing.wav'),
        CompanyCaseStudyFactory.create(image_one='thing.js'),
    ]

    migration.apply('company', '0032_remove_bad_images')

    for item in good:
        expected = str(item.image_one)
        item.refresh_from_db()
        assert str(item.image_one) == expected

    for item in bad:
        item.refresh_from_db()
        assert str(item.image_one) == ''


def test_remove_bad_images_from_case_study_image_two(migration):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good = [
        CompanyCaseStudyFactory.create(image_two='thing.png'),
        CompanyCaseStudyFactory.create(image_two='thing.jpg'),
        CompanyCaseStudyFactory.create(image_two='thing.svg'),
        CompanyCaseStudyFactory.create(image_two=''),
    ]
    bad = [
        CompanyCaseStudyFactory.create(image_two='thing.pdf'),
        CompanyCaseStudyFactory.create(image_two='thing.wav'),
        CompanyCaseStudyFactory.create(image_two='thing.js'),
    ]

    migration.apply('company', '0032_remove_bad_images')

    for item in good:
        expected = str(item.image_two)
        item.refresh_from_db()
        assert str(item.image_two) == expected

    for item in bad:
        item.refresh_from_db()
        assert str(item.image_two) == ''


def test_remove_bad_images_from_case_study_image_three(migration):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good = [
        CompanyCaseStudyFactory.create(image_three='thing.png'),
        CompanyCaseStudyFactory.create(image_three='thing.jpg'),
        CompanyCaseStudyFactory.create(image_three='thing.svg'),
        CompanyCaseStudyFactory.create(image_three=''),
    ]
    bad = [
        CompanyCaseStudyFactory.create(image_three='thing.pdf'),
        CompanyCaseStudyFactory.create(image_three='thing.wav'),
        CompanyCaseStudyFactory.create(image_three='thing.js'),
    ]

    migration.apply('company', '0032_remove_bad_images')

    for item in good:
        expected = str(item.image_three)
        item.refresh_from_db()
        assert str(item.image_three) == expected

    for item in bad:
        item.refresh_from_db()
        assert str(item.image_three) == ''


def test_remove_bad_images_from_case_study_image_multiple_bad(migration):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good = [
        CompanyCaseStudyFactory.create(
            image_one='thing.jpg',
            image_two='thing.svg',
            image_three='thing.png',
        ),
        CompanyCaseStudyFactory.create(
            image_one='thing.jpg',
            image_two='thing.svg',
            image_three='thing.png',
        ),
    ]
    bad = [
        CompanyCaseStudyFactory.create(
            image_one='thing.pdf',
            image_two='thing.wav',
            image_three='thing.js',
        ),
        CompanyCaseStudyFactory.create(
            image_one='thing.pdf',
            image_two='thing.wav',
            image_three='thing.js'
        ),
    ]

    migration.apply('company', '0032_remove_bad_images')

    for item in good:
        expected_one = str(item.image_one)
        expected_two = str(item.image_two)
        expected_three = str(item.image_three)
        item.refresh_from_db()
        assert str(item.image_one) == expected_one
        assert str(item.image_two) == expected_two
        assert str(item.image_three) == expected_three

    for item in bad:
        item.refresh_from_db()
        assert str(item.image_one) == ''
        assert str(item.image_two) == ''
        assert str(item.image_three) == ''


def test_remove_bad_images_from_case_study_image_multiple_good_and_bad(
    migration
):
    app = 'company'
    model_name = 'CompanyCaseStudy'
    name = '0031_auto_20170121_1552'
    migration.before(app, name).get_model(app, model_name)

    good_and_bad_one = CompanyCaseStudyFactory.create(
        image_one='thing.wav',
        image_two='thing.jpg',
        image_three='thing.gif',
    )
    good_and_bad_two = CompanyCaseStudyFactory.create(
        image_one='thing.svg',
        image_two='thing.pdf',
        image_three='thing.png',
    )
    good_and_bad_three = CompanyCaseStudyFactory.create(
        image_one='thing.gif',
        image_two='thing.png',
        image_three='thing.js',
    )

    migration.apply('company', '0032_remove_bad_images')

    good_and_bad_one.refresh_from_db()
    good_and_bad_two.refresh_from_db()
    good_and_bad_three.refresh_from_db()

    assert str(good_and_bad_one.image_one) == ''
    assert str(good_and_bad_one.image_two) == 'thing.jpg'
    assert str(good_and_bad_one.image_three) == 'thing.gif'
    assert str(good_and_bad_two.image_one) == 'thing.svg'
    assert str(good_and_bad_two.image_two) == ''
    assert str(good_and_bad_two.image_three) == 'thing.png'
    assert str(good_and_bad_three.image_one) == 'thing.gif'
    assert str(good_and_bad_three.image_two) == 'thing.png'
    assert str(good_and_bad_three.image_three) == ''

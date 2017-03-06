def example_test(migration):
    app = 'company'
    model_name = 'Company'
    name = 'before_migration_name_here'
    migration.before(app, name).get_model(app, model_name)

    migration.apply('company', 'migration_name_here')

    # assert migration did the job

from django.db import DatabaseError

from company.models import Company


class DatabaseHealthCheck:
    name = 'database'

    def check(self):
        try:
            Company.objects.all().exists()
        except DatabaseError as de:
            return False, de
        else:
            return True, ''


health_check_services = (DatabaseHealthCheck,)

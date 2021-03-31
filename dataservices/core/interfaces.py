import dateutil.parser


class APIModel:
    data = {}

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name in self.data:
            return self.data.get(name)
        raise AttributeError


class Barrier(APIModel):
    @property
    def is_resolved_text(self):
        if self.is_resolved:
            if self.status_date:
                return f"Yes - {self.status_date.strftime('%B %Y')}"
            return "Yes"
        return "No"

    @property
    def status_date(self):
        if self.data.get("status_date"):
            return dateutil.parser.parse(self.data["status_date"])

    @property
    def country(self):
        return self.data["country"].get("name")

    @property
    def location(self):
        return self.data["location"]

    @property
    def simple_location(self):
        if self.country:
            return self.country
        return self.trading_bloc

    @property
    def sectors(self):
        return ", ".join(self.sectors_list)

    @property
    def sectors_list(self):
        sector_names = [s.get("name") for s in self.data.get("sectors", {})]
        return sector_names

    @property
    def trading_bloc(self):
        trading_bloc = self.data.get("trading_bloc", {})
        return trading_bloc.get("name", "")

    @property
    def categories_list(self):
        return [s.get("name") for s in self.data.get("categories", {})]

    @property
    def last_published_on(self):
        return dateutil.parser.parse(self.data["last_published_on"])

    @property
    def reported_on(self):
        return dateutil.parser.parse(self.data["reported_on"])

    @property
    def public_id(self):
        return f"PID-{self.id}"

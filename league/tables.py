import django_tables2 as tables

class ValueColumn(tables.Column):
    def render(self, value):
        print(value.values)
        return 23

class LeagueTable(tables.Table):
    player = tables.Column()
    games = tables.Column(attrs={"th": {"class": "tgames"}, "td": {"class": "tgames"}})
    winn = tables.Column(attrs={"th": {"class": "twinn"}, "td": {"class": "twinn"}})
    loose = tables.Column(attrs={"th": {"class": "tloose"}, "td": {"class": "tloose"}})
    remis = tables.Column(attrs={"th": {"class": "tremis"}, "td": {"class": "tremis"}})
    winlegs = tables.Column()
    looselegs = tables.Column()
    diff = tables.Column()
    points = tables.Column()
    
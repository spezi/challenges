import django_tables2 as tables

class ValueColumn(tables.Column):
    def render(self, value):
        print(value.values)
        return 23

class LeagueTable(tables.Table):
    player = tables.Column()
    games = tables.Column()
    winn = tables.Column()
    loose = tables.Column()
    remis = tables.Column()
    winlegs = tables.Column()
    looselegs = tables.Column()
    diff = tables.Column()
    points = tables.Column()
    
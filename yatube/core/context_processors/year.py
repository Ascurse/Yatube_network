import datetime


def year(request):
    """Current year"""
    return {
        'year': datetime.date.today().year
    }

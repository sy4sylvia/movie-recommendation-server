title1 = 'Now And Then (1995)'


def get_title(title):
    year = title[len(title) - 5:len(title) - 1]
    if year.isnumeric():
        print(year)
        print(title[: len(title) - 7])
    else:
        return year


get_title(title1)

from time import strftime, localtime

def get_date(epoch_date):
    return strftime('%Y-%m-%d %H:%M:%S', localtime(epoch_date / 1000))

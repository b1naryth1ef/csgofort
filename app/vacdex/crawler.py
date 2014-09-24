def convert_steamid(id):
    if len(id) == 17:
        return int(id[3:]) - 61197960265728
    else:
        return '765' + str(int(id) + 61197960265728)

def crawl_every_steamid():
    steamid = "1"
    while True:
        print convert_steamid(steamid)
        break

crawl_every_steamid()

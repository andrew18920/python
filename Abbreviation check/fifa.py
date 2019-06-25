country_dict = {}
found_matches = {}

def country_from_abbr(abbr):
    global country_dict
    countries = [c[0] for c in country_dict]
    abbrs = [c[1] for c in country_dict]
    ind = abbrs.index(abbr)
    return countries[ind]

with open('fifa_abbr.txt') as file:
    for country in file:
        name,abbr = country.strip().split('	')
        if name[:3].upper() == abbr:
            country_dict[(name,abbr)] = []

        p = [c[1] for c in country_dict]
        if name[3:].upper() in p:
            matched_country = country_from_abbr(name[3:].upper())
            if (name,abbr) in found_matches:
                found_matches[(name,abbr)].append(matched_country)
            else:
                found_matches[(name,abbr)] = [matched_country]

print(found_matches)

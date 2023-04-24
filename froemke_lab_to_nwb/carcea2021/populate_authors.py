author_records = [
    {
        "ORCID": "http://orcid.org/0000-0002-4459-9321",
        "authenticated-orcid": False,
        "given": "Ioana",
        "family": "Carcea",
        "sequence": "first",
        "affiliation": []
    },
    {
        "given": "Naomi López",
        "family": "Caraballo",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Bianca J.",
        "family": "Marlin",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Rumi",
        "family": "Ooyama",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Justin S.",
        "family": "Riceberg",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Joyce M.",
        "family": "Mendoza Navarro",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Maya",
        "family": "Opendak",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Veronica E.",
        "family": "Diaz",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Luisa",
        "family": "Schuster",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Maria I.",
        "family": "Alvarado Torres",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Harper",
        "family": "Lethin",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Daniel",
        "family": "Ramos",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Jessica",
        "family": "Minder",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Sebastian L.",
        "family": "Mendoza",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Chloe J.",
        "family": "Bair-Marshall",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Grace H.",
        "family": "Samadjopoulos",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Shizu",
        "family": "Hidema",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "ORCID": "http://orcid.org/0000-0001-9756-7887",
        "authenticated-orcid": False,
        "given": "Annegret",
        "family": "Falkner",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "ORCID": "http://orcid.org/0000-0003-2006-0791",
        "authenticated-orcid": False,
        "given": "Dayu",
        "family": "Lin",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Adam",
        "family": "Mar",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Youssef Z.",
        "family": "Wadghiri",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Katsuhiko",
        "family": "Nishimori",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Takefumi",
        "family": "Kikusui",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Kazutaka",
        "family": "Mogi",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "given": "Regina M.",
        "family": "Sullivan",
        "sequence": "additional",
        "affiliation": []
    },
    {
        "ORCID": "http://orcid.org/0000-0002-1230-6811",
        "authenticated-orcid": False,
        "given": "Robert C.",
        "family": "Froemke",
        "sequence": "additional",
        "affiliation": []
    }
]

additional_contributors_list = []
for author_record in author_records:
    author_dandi_record = dict(
        name=f'{author_record["family"]}, {author_record["given"]}',
        roleName=['dcite:Author'],
        schemaKey='Person',
        affiliation=[],
        includeInCitation=True,
    )
    if "ORCID" in author_record:
        author_dandi_record.update(identifier=author_record['ORCID'].split("\\/")[-1])

    additional_contributors_list.append(author_dandi_record)

from dandi.dandiapi import DandiAPIClient
from dandischema.models import Person
api = DandiAPIClient()
api.authenticate(token="...")
ds = api.get_dandiset("000114")

meta_raw = ds.get_raw_metadata()

meta_raw["contributor"] = additional_contributors_list
# try validate contributors, fix errors if any (can also embed in try except)
for i in range(len(meta_raw['contributor'])):
    print(meta_raw['contributor'][i])
    Person(**meta_raw['contributor'][i])


#ds.set_raw_metadata(meta_raw)

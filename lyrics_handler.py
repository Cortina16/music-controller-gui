import json
import requests
from requests.utils import CaseInsensitiveDict

url = "https://api.spicylyrics.org/query"

headers = CaseInsensitiveDict()
headers["spicylyrics-webauth"] = "Bearer BQCeOAJRaFvNIhZUG_p6KnOX1wX_AXDpWPAJz7g9cLnepiCVm2-veNEHKfKTFSxtgrPZ26XwgFXrHALzeEtEA7fZZ_TPBk0G4r_Fv1y0504uMWcs4b875RZdemwV3SJVZ-RzD5m4FhTNISohecKQ9xVVtHBy-Tx4sNOCr8F-ajV7vb2Nx1HCRbZpzefZZhOGHqoye5BmEtrvYAK2ADy-8lipZ1bUXxehbi1Hcog2mH0lzEREDJiebaNxtF3ba6T_3GjKWKBUwKklQbxdiIidKf4_TYSyapnEqvPgtkSHeIjrwG62tZ4t1T4Yej284REGF1m3H2rUptxRju_uILxQlh70AGSmeyqqBeVh_qxmJOimuL86KMqFWt7LQ2x_JGK4lpF3CmuGDrUplkM8wALGbH1wGgyHAgGdH2U5JiaS49VSEUQGCapm5zTcJB-WK-ZFJLpSAUiaUHr9PPwA76b37rMx4CulUVoz7WTyyoSXG7hNWS0^"
headers["Content-Type"] = "application/json"

song_id = '4xigPf2sigSPmuFH3qCelB'

def get_song_lyrics(song_id):
    data = f'{{"queries":[{{"operation":"lyrics","variables":{{"id":"{song_id}","auth":"SpicyLyrics-WebAuth"}}}}],"client":{{"version":"5.19.11"}}}}'
    resp = requests.post(url, headers=headers, data=data)
    return resp.json()



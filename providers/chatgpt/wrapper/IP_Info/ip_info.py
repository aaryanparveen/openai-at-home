from curl_cffi  import requests
from ..logger   import Log
from ..runtime  import Utils


class IP_Info:

    DEFAULTS = [
        "0.0.0.0",
        "New York",
        "New York",
        "40.7128",
        "-74.0060",
        "America/New_York",
    ]

    @staticmethod
    def fetch_info(session: requests.session.Session) -> list:

        ip_infos: list = []

        try:
            info_request: requests.models.Response = session.get('https://iplocation.com/', timeout=8)

            ip_infos.append(Utils.between(info_request.text, '<td><b class="ip">', '<'))
            ip_infos.append(Utils.between(info_request.text, '<td class="city">', '<'))
            ip_infos.append(Utils.between(info_request.text, '<td><span class="region_name">', '<'))
            ip_infos.append(Utils.between(info_request.text, '<td class="lat">', '<'))
            ip_infos.append(Utils.between(info_request.text, '<td class="lng">', '<'))

            info_request_2: requests.models.Response = session.get('https://ipaddresslocation.net/ip-to-timezone', timeout=8)

            ip_infos.append(Utils.between(info_request_2.text, 'Time Zone:</strong> ', ' '))
        except Exception as e:
            Log.Error(f"IP lookup failed ({e}), using defaults")
            ip_infos = list(IP_Info.DEFAULTS)

        if len(ip_infos) < 6 or not ip_infos[5]:
            Log.Error("Incomplete IP data, using defaults")
            ip_infos = list(IP_Info.DEFAULTS)

        return ip_infos

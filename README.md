# weewx-nuasense

Upload your weewx station to [NuaSense](https://nuasense.com) and get the agronomy computed on it: tonight's low and frost risk, the next calm dry window for spraying, ET0, leaf wetness, spray quality, and a check of your station against the model. Any station weewx supports — Davis, Fine Offset, Oregon, Campbell, Vantage over a serial cable — becomes a NuaSense station. The first three stations on an account connect free.

The extension is small on purpose: weewx already knows how to post in the Wunderground format, retry, and fill in what a record lacks. This just points that at NuaSense.

## Install

1. In the NuaSense console: **External stations → Add a station**, pick *Home Assistant / weewx / Meteobridge / Node-RED*, give the station a name and a position. The last screen shows a path like `/station/kw7n-4hpd-x2vt`; the part after `/station/` is the token.
2. On the weewx machine:

   ```
   # weewx 5
   weectl extension install https://github.com/nuasense/weewx-nuasense/archive/refs/tags/v0.1.0.zip
   # weewx 4
   wee_extension --install weewx-nuasense-0.1.0.zip
   ```

3. In `weewx.conf`, put the token in:

   ```
   [StdRESTful]
       [[NuaSense]]
           enable = true
           token = kw7n-4hpd-x2vt
           station = weewx
   ```

4. Restart weewx. The log says `NuaSense: data for station weewx will be posted to http://ingest.nuasense.com/…`, and within one archive interval the station shows its first upload in the console.

Plain `http` is deliberate: the receiver speaks what consoles speak, and consoles cannot do TLS. The token is a write-only credential for this one station, bound to the first sender that uses it.

## What is sent

Each archive record, as weewx's Wunderground uploader formats it: temperature, humidity, dew point, barometer, wind, rain, solar radiation and UV where the station has them. NuaSense reduces the barometer back to station pressure from the station's altitude.

## Your data

When you connect a station, NuaSense stores its readings and computes your forecast, spray windows and risks from them. The readings are used aggregated and anonymised to improve forecasts and models for everyone; they are never passed on individually without your opt-in. You can disconnect the station in the console at any time and have all its data deleted.

MIT licence. Issues: https://github.com/nuasense/weewx-nuasense/issues

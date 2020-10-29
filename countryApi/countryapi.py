import requests
import json


class RestCountryApi:
    BASE_URI = 'https://restcountries.eu/rest/v2'
    QUERY_SEPARATOR = ','

    def _get_country_list(self, resource, term=''):
        """Takes a resource and a search term and return a list of countries or a country.
        :param resource - resource to create the URL
        :param term - search term provided by the user of this package
        :returns - either a Country object or a list of Countries
        """
        # build uri
        if term and not resource.endswith("="):
            # add the forward slash only when there is a term
            # and it is not specifying the value part of a query string
            term = "/{}".format(term)

        uri = "{}{}{}".format(self.BASE_URI, resource, term)

        response = requests.get(uri)
        if response.status_code == 200:
            result_list = []
            data = json.loads(response.text)  # parse json to dict
            if type(data) == list:
                for country_data in data:  # in case it is a list create python list with country instances
                    country = Country(country_data)
                    result_list.append(country)
            else:
                return Country(data)
            return result_list
        elif response.status_code == 404:
            raise requests.exceptions.InvalidURL
        else:
            raise requests.exceptions.RequestException

    def get_all(self):
        """Returns all countries provided by  restcountries.eu."""
        resource = '/all'
        return self._get_country_list(resource)

    def get_countries_by_name(self, name):
        """Returns a list of countries.
        :param name - Name string of a country. E.g. 'France'.
        :returns: list of Country objects
        """
        resource = '/name'
        return self._get_country_list(resource, name)

    def get_countries_by_language(self, language):
        """Returns a list of countries.
        :param language - Language string of a country. E.g. 'en'.
        :returns: list of Country objects
        """
        resource = '/lang'
        return self._get_country_list(resource, language)

    def get_countries_by_calling_code(self, calling_code):
        """Returns a list of countries.
        :param calling_code - Calling code string of a country. E.g. '1'.
        :returns: list of Country objects
        """
        resource = '/callingcode'
        return self._get_country_list(resource, calling_code)

    def get_country_by_country_code(self, alpha):
        """Returns a `Country` object by alpha code.
        :param alpha - Alpha code string of a country. E.g. 'de'.
        :returns: a Country object
        """
        resource = '/alpha'
        return self._get_country_list(resource, alpha)

    def get_countries_by_country_codes(self, codes):
        """Returns a list of countries.
        :param codes - List of strings which represent the codes of countries. E.g. ['us', 'uk']
        :returns: list of Country objects
        """
        resource = '/alpha?codes='
        codes = self.QUERY_SEPARATOR.join(codes)
        return self._get_country_list(resource, codes)

    def get_countries_by_currency(self, currency):
        """Returns a list of countries.
        :param currency - Currency string of a country. E.g. 'EUR'.
        :returns: list of Country objects
        """
        resource = '/currency'
        return self._get_country_list(resource, currency)

    def get_countries_by_region(self, region):
        """Returns a list of countries.
        :param region - Region string of a country. E.g. 'Europe'.
        :returns: list of Country objects
        """
        resource = '/region'
        return self._get_country_list(resource, region)

    def get_countries_by_subregion(self, subregion):
        """Returns a list of countries.
        :param subregion - Subregion string of a country. E.g. 'Western Europe'
        :returns: list of Country objects
        """
        resource = '/subregion'
        return self._get_country_list(resource, subregion)

    def get_countries_by_capital(self, capital):
        """Returns a list of countries.
        :param capital - Capital string of a country. E.g. 'London'
        :returns: list of Country objects
        """
        resource = '/capital'
        return self._get_country_list(resource, capital)

    def get_regions(self):
        """Returns a list of regions
        :return: list of Regions
        """
        countries = self.get_all()
        regions = []
        for country in countries:
            region = str(country.region).strip()
            if str(region) == "" or regions.__contains__(region):
                continue
            else:
                regions.append(region)
        regions.sort()
        return regions

    def get_subregions(self):
        """Returns a list of subregions
        :return: list of Subregions
        """
        countries = self.get_all()
        subregions = []
        for country in countries:
            subregion = str(country.subregion).strip()
            if str(subregion) == "" or subregions.__contains__(subregion):
                continue
            else:
                subregions.append(subregion)
        subregions.sort()
        return subregions

    def get_attr_countries(self, attribute, **kwargs):
        """

        :param attribute: name of country's attribute. E.g: 'name'
        :param kwargs: list of countries
        :return: list of specific attribute of countries
        """
        countries_attribute = []
        for country in self.get_all() if len(kwargs) == 0 else kwargs.get("countries"):
            country_attr = getattr(country, attribute)
            if type(country_attr) == list:
                for item in country_attr:
                    if type(item) == dict:
                        if attribute == "languages":
                            lang_dic = dict(name=item["name"], code=item["iso639_1"])
                            if lang_dic not in countries_attribute:
                                countries_attribute.append(lang_dic)
                    elif len(item) != 0 and not countries_attribute.__contains__(item):
                        countries_attribute.append(item)
            else:
                if not countries_attribute.__contains__(country_attr) and len(country_attr) != 0:
                    countries_attribute.append(country_attr)
        if type(countries_attribute[0]) != dict:
            countries_attribute.sort()
            return countries_attribute
        else:
            return sorted(countries_attribute, key=lambda i: i["name"])

    def get_languages(self, **kwargs):
        """return list of languages name
          :param lst: list of countries as Country
          :return: list of names as String
          """
        lang_list = self.get_attr_countries("languages") if len(kwargs) == 0 \
            else self.get_attr_countries("languages", countries=kwargs.get("countries"))
        lang_name_list = []
        lang_iso_list = []
        for pair in lang_list:
            if pair['code'] is not None:
                lang_name_list.append(pair["name"])
                lang_iso_list.append(pair["code"])
        return dict(names=lang_name_list, codes=lang_iso_list)


class Country:

    def __str__(self):
        return '{}'.format(self.name)

    def __init__(self, country_data):
        self.top_level_domain = country_data.get('topLevelDomain')
        self.alpha2_code = country_data.get('alpha2Code')
        self.alpha3_code = country_data.get('alpha3Code')
        self.currencies = country_data.get('currencies')
        self.capital = country_data.get('capital')
        self.calling_codes = country_data.get('callingCodes')
        self.alt_spellings = country_data.get('altSpellings')
        self.relevance = country_data.get('relevance')
        self.region = country_data.get('region')
        self.subregion = country_data.get('subregion')
        self.translations = country_data.get('translations')
        self.population = country_data.get('population')
        self.latlng = country_data.get('latlng')
        self.demonym = country_data.get('demonym')
        self.area = country_data.get('area')
        self.gini = country_data.get('gini')
        self.timezones = country_data.get('timezones')
        self.borders = country_data.get('borders')
        self.native_name = country_data.get('nativeName')
        self.name = country_data.get('name')
        self.numeric_code = country_data.get('numericCode')
        self.languages = country_data.get('languages')
        self.flag = country_data.get('flag')
        self.regional_blocs = country_data.get('regionalBlocs')
        self.cioc = country_data.get('cioc')

    def __eq__(self, other):
        assert isinstance(other, Country)
        return self.numeric_code == other.numeric_code

    def __lt__(self, other):
        assert isinstance(other, Country)
        return self.numeric_code < other.numeric_code

    def __hash__(self):
        return int(self.numeric_code)

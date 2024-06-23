from abc import ABC, abstractmethod
from urllib.parse import urljoin


class BaseApi(ABC):
    @abstractmethod
    def upload(self, *args, **kwargs):
        """
        Abstract method to upload data. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def download(self, *args, **kwargs):
        """
        Abstract method to download data. Must be implemented by subclasses.
        """
        pass

    def __init__(self, baseurl, resturi):
        """
        Initializes the BaseApi with a base URL and a REST URI.

        :param baseurl: The base URL for the API. eg. http://nexus3.homelab.com
        :param resturi: The REST URI segment for the API. eg. /service/rest/v1
        """
        self.baseurl = baseurl
        self.resturi = resturi

    def get_url(self, endpoint):
        """
        Constructs a full URL for a given API endpoint.

        :param endpoint: The specific API endpoint.
        :return: The full URL constructed from baseurl, resturi, and endpoint.
        """
        url = urljoin(self.baseurl, self.resturi + "/" + endpoint)
        return url


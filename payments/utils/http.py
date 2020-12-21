import requests


def post(url, headers, data):
    """
    Send a post request to the given url

        Parameters
        ----------

        url : str
            The url

        headers: dict
            The request headers

        data: dict
            The data to be posted

        Returns
        ---------
        request :
            The Http Response contains details of whether the request was successful
            and a response message.
    """
    request = requests.post(url=url, headers=headers, json=data)

    return request


def get(url, headers):
    """
    Post a request to a given url
    :param url:
    :param headers:
    :param data:
    :return:

    Send a GET Request to the given endpoint.

        Parameters
        ----------

        url : str
            The url

        headers: dict
            The request headers

        Returns
        ---------
        request :
            The Http Response contains details of whether the request was successful
            and a response message.
    """
    request = requests.get(url=url, headers=headers)

    return request

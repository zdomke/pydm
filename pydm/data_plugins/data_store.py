from enum import Enum


class DataKeys(str, Enum):
    """
    Enum class which holds the keys expected by the PyDMWidgets when used with
    a structured data to parse the data in search for the needed fields.
    """
    CONNECTION = 'CONNECTION'
    VALUE = 'VALUE'
    SEVERITY = 'SEVERITY'
    WRITE_ACCESS = 'WRITE_ACCESS'
    ENUM_STRINGS = 'ENUM_STRINGS'
    UNIT = 'UNIT'
    PRECISION = 'PRECISION'
    UPPER_LIMIT = 'UPPER_LIMIT'
    LOWER_LIMIT = 'LOWER_LIMIT'

    def generate_introspection_for(self, connection_key=None, value_key=None,
                                   severity_key=None, write_access_key=None,
                                   enum_strings_key=None, unit_key=None,
                                   precision_key=None, upper_limit_key=None,
                                   lower_limit_key=None
                                   ):
        """
        Generates an introspection dictionary for a given set of keys.
        This is used by PyDMWidgets to map the needed keys in a structured
        data source into the fields needed.

        Parameters
        ----------
        connection_key : str
            The key for the connection status information at the data
            dictionary
        value_key : str
            The key for the value information at the data dictionary
        severity_key : str
            The key for the severity information at the data dictionary
        write_access_key : str
            The key for the write access information at the data dictionary
        enum_strings_key : str
            The key for the enum strings information at the data dictionary
        unit_key : str
            The key for the engineering unit information at the data dictionary
        precision_key : str
            The key for the precision information at the data dictionary
        upper_limit_key : str
            The key for the upper limit information at the data dictionary
        lower_limit_key : str
            The key for the lower limit information at the data dictionary

        Returns
        -------
        introspection : dict

        """
        lookup_table = [
            (connection_key, self.CONNECTION),
            (value_key, self.VALUE),
            (severity_key, self.SEVERITY),
            (write_access_key, self.WRITE_ACCESS),
            (enum_strings_key, self.ENUM_STRINGS),
            (unit_key, self.UNIT),
            (precision_key, self.PRECISION),
            (upper_limit_key, self.UPPER_LIMIT),
            (lower_limit_key, self.LOWER_LIMIT)
        ]
        introspection = dict()

        for val, key in lookup_table:
            if val:
                introspection[key] = val

        return introspection


DEFAULT_INTROSPECTION = {i.name: i.value for i in DataKeys}


class DataStore(object):
    """
    Singleton class responsible for holding the data and instrospection tables
    for the channels.
    """
    __instance = None

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self._data = {}
        self._introspection = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(DataStore)
            cls.__instance.__initialized = False
        return cls.__instance

    def introspect(self, address):
        """
        Query the introspection mapping about the information for a given
        address.

        Parameters
        ----------
        address : str
            The address identifier.

        Returns
        -------
        introspection : dict or None
            If no information is found this method returns None
        """
        return self._introspection.get(address, None)

    def fetch(self, address, with_introspection=False):
        """
        Fetch the data associated with an address.

        Parameters
        ----------
        address : str
            The address identifier
        with_introspection : bool
            If True, returns also the introspection dictionary

        Returns
        -------
        data : dict or None
            If no information is found this method returns None
        introspection : dict
            Returned only if `with_introspection` is `True`
        """
        data = self._data.get(address, None)
        intro = self._introspection.get(address, None)
        if with_introspection:
            return data, intro
        return data

    def update(self, address, data, introspection=None):
        """
        Update the cache with the new values for data and introspection.

        Parameters
        ----------
        address : str
            The address identifier.

        data : dict
            The data payload to be stored.

        introspection : dict, optional.
            The introspection payload to be stored.

        """
        self._data.update({address: data})
        if introspection:
            self._introspection.update({address: introspection})

    def remove(self, address):
        """
        Removes all data associated with a given address from the Data Store.

        Parameters
        ----------
        address : str
            The address identifier.

        """
        self._data.pop(address, None)
        self._introspection.pop(address, None)

    def __getitem__(self, item):
        return self.fetch(item)

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            self.update(key, value[0], value[1])
        elif isinstance(value, dict):
            self.update(key, value)
        else:
            raise ValueError("Invalid value.")

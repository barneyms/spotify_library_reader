from configparser import ConfigParser


def get_config():

    config_dict = {}
    config = ConfigParser()
    config.read('config.ini')
    for section in config.sections():
        options = config.options(section)
        for option in options:
            try:
                config_dict[option] = config.get(section, option)
                if config_dict[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                config_dict[option] = None
        print(config_dict)
        return config_dict


class DefaultList(list):

   def __setitem__(self, index, value):
      size = len(self)
      if index >= size:
         self.extend(0 for _ in range(size, index + 1))

      list.__setitem__(self, index, value)


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

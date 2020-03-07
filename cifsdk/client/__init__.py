from csirtg_indicator import Indicator


class Client(object):

    @staticmethod
    def _kv_to_indicator(kv):
        return Indicator(**kv)

    def search(self, data):
        return self.indicators_search(data)

    def indicators_create(self, data):
        raise NotImplementedError

    def indicators_search(self, data):
        raise NotImplementedError

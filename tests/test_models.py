import gncgym.models as models


class TestModelLoading:
    def test_autoload(self):
        loaded_models = models.autoload()  # Result is cached after models are loaded for the first time
        assert type(loaded_models) is dict

    def test_model_interfaces(self):
        loaded_models = models.autoload()  # Result is cached after models are loaded for the first time

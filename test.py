def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset['LanguageTable'])) == 21


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset['ParameterTable'])) == 501


def test_sources(cldf_dataset):
    assert len(cldf_dataset.sources) == 17

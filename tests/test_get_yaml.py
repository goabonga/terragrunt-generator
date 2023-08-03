from generator.yaml import get_yaml


def test_get_yaml():
    name: str = 'test'
    variables: dict = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [
            {
                'name': 'optionals',
                'description': 'optionals',
                'default': 'optional_value',
            }
        ],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    resutls = get_yaml(name, variables)
    print(resutls)
    excepted = """test:
  enabled: true
  # mandatories - mandatories
  mandatories: 
  # optionals - optionals
  # optionals: "optional_value"
  # nullables - nullables
  # nullables: 
"""
    assert resutls == excepted

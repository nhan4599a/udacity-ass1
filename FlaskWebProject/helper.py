def get_form_values(form):
    values = dict()
    for key, value in form._fields.items():
        if type(value) != '<class \'<wtforms.fields.simple.SubmitField>\'>':
            values[key] = value.data
    return values

def parse_to_bool(str):
    lower_str = str.lower()
    if lower_str not in ['true', 'false']:
        raise ValueError(f'\"{str}\" is invalid for boolean type')
    return True if lower_str == 'true' else False

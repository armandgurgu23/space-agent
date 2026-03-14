from jinja2 import Environment

def render_prompt(template_file: str, jinja_env:Environment, **kwargs) -> str:
    template = jinja_env.get_template(template_file)
    return template.render(**kwargs)
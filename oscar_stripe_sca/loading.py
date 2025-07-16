import importlib
import logging


def get_class_by_path(class_path):
	"""Return the Python class found at the specified path.

	For example, `get_class_by_path("oscar_stripe_sca.facade.Facade")`
	returns the `Facade` class from the `oscar_stripe_sca.facade`
	module.

	"""
	SEPARATOR = "."

	class_path_elements = class_path.split(SEPARATOR)
	class_name = class_path_elements.pop()
	module_path = SEPARATOR.join(class_path_elements)

	module = importlib.import_module(module_path)
	Class = getattr(module, class_name)

	return Class

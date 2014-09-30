import inspect

def check_base_class_by_name(obj, base_name):
	mro = inspect.getmro(obj.__class__)
	return filter(lambda cls:cls.__name__ == base_name, mro)

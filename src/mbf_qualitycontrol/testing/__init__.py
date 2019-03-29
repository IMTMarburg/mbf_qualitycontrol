from pathlib import Path
import inspect
import sys
from matplotlib.testing.compare import compare_images


def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """

    def stack_(frame):
        framelist = []
        while frame:
            framelist.append(frame)
            frame = frame.f_back
        return framelist

    stack = stack_(sys._getframe(1))
    start = 0 + skip
    if len(stack) < start + 1:
        return ""
    parentframe = stack[start]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if "self" in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals["self"].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != "<module>":  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return ".".join(name)

def caller_file(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """

    def stack_(frame):
        framelist = []
        while frame:
            framelist.append(frame)
            frame = frame.f_back
        return framelist

    stack = stack_(sys._getframe(1))
    start = 0 + skip
    if len(stack) < start + 1:
        return ""
    parentframe = stack[start]

    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    # detect classnamarentframe.f_locals["self"].__class__.__name__)
    return parentframe.f_code.co_filename
    


def assert_image_equal(generated_image_path, suffix="", tolerance=2):
    """assert that the generated image and the base_images/{test_module}/{cls}/{function_name}{suffix}.extension is identical"""
    generated_image_path = Path(generated_image_path).absolute()
    extension = generated_image_path.suffix
    caller = caller_name(1)
    caller_fn = caller_file(1)
    parts = caller.split(".")
    if len(parts) >= 3:
        func = parts[-1]
        cls = parts[-2]
        module = parts[-3]
        #if cls.lower() == cls:  # not actually a class, a module instead
            #module = cls
            #cls = "_"
    else:
        module = parts[-2]
        cls = "_"
        func = parts[-1]
    should_path = (
        Path(caller_fn).parent
        / "base_images"
        / module
        / cls
        / (func + suffix + extension)
    ).resolve()
    if not should_path.exists():
        should_path.parent.mkdir(exist_ok=True, parents=True)
        raise ValueError(
            f"Base_line image not found, perhaps: \ncp {generated_image_path} {should_path}"
        )
    err = compare_images(
        str(should_path), str(generated_image_path), tolerance, in_decorator=True
    )
    assert not err

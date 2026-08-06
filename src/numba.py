"""Light shim for numba.njit when numba is not installed.
This allows running in environments where numba is unavailable; the decorator is a no-op.
"""

def njit(*args, **kwargs):
    def _dec(f):
        return f
    # If used as @njit or @njit(...)
    if args and callable(args[0]):
        return args[0]
    return _dec

# Provide common aliases
def jit(*args, **kwargs):
    return njit(*args, **kwargs)

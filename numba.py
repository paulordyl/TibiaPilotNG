"""Top-level shim for numba when not installed. Keeps imports like `from numba import njit` working in CI/local without numba."""

def njit(*args, **kwargs):
    def _dec(f):
        return f
    if args and callable(args[0]):
        return args[0]
    return _dec

def jit(*args, **kwargs):
    return njit(*args, **kwargs)

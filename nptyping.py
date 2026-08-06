"""Lightweight shim for nptyping used for typing only in runtime when nptyping is not installed.
Expose NDArray name so `from nptyping import NDArray` works.
"""
NDArray = None

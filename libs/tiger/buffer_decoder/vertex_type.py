import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class Tiger_Vertex_Type:
    components_bits: tuple[int, ...]
    is_float: bool
    is_signed: bool
    is_normalized: bool
    numpy_type: np.dtype | None

    @property
    def component_count(self) -> int:
        return len(self.components_bits)

    @property
    def bit_size(self) -> int:
        return sum(self.components_bits)

    @property
    def byte_size(self) -> int:
        if self.bit_size % 8 != 0:
            raise ValueError(f"Vertex type size is not byte-aligned: {self.bit_size} bits")

        return self.bit_size // 8

    @property
    def is_packed(self) -> bool:
        return self.numpy_type is None
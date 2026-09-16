"""The monospace grid the terminal is laid out on."""

from __future__ import annotations

from dataclasses import dataclass

FONT_STACK = (
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
    "'Liberation Mono', monospace"
)

CURSOR_WIDTH_RATIO = 0.85
CURSOR_HEIGHT_RATIO = 1.15


@dataclass(frozen=True)
class Metrics:
    """Type metrics and padding for the terminal box."""

    font_size: float = 13.0
    #: Advance width of one glyph as a fraction of the font size. 0.6 is the
    #: ratio shared by the monospace faces in FONT_STACK.
    char_width_ratio: float = 0.6
    line_height_ratio: float = 1.55
    padding: float = 20.0
    border_radius: float = 6.0
    #: Where the baseline sits inside the line box, as a fraction of the font
    #: size measured up from the bottom.
    baseline_offset_ratio: float = 0.35

    @property
    def char_width(self) -> float:
        return self.font_size * self.char_width_ratio

    @property
    def line_height(self) -> float:
        return self.font_size * self.line_height_ratio

    @property
    def cursor_width(self) -> float:
        return self.char_width * CURSOR_WIDTH_RATIO

    @property
    def cursor_height(self) -> float:
        return self.font_size * CURSOR_HEIGHT_RATIO

    def x_for_column(self, column: int) -> float:
        return self.padding + column * self.char_width

    def baseline_for_row(self, row: int) -> float:
        bottom = self.padding + (row + 1) * self.line_height
        return bottom - self.font_size * self.baseline_offset_ratio

    def width_for_columns(self, columns: int) -> float:
        return round(self.x_for_column(columns) + self.padding)

    def height_for_rows(self, rows: int) -> float:
        return round(self.padding * 2 + rows * self.line_height)


METRICS = Metrics()

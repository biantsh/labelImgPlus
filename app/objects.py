from app.enums.annotation import HoverType, SelectionType


class Bbox:
    def __init__(self,
                 position: list[int, ...],
                 label_name: str
                 ) -> None:
        self.position = position
        self.label_name = label_name

    @classmethod
    def from_xywh(cls,
                  position: list[int, ...],
                  label_name: str
                  ) -> 'Bbox':
        x_min, y_min, width, height = position
        x_max, y_max = x_min + width, y_min + height

        return cls([x_min, y_min, x_max, y_max], label_name)

    @property
    def points(self) -> tuple[tuple[int, int], ...]:
        return (
            (self.left, self.top),
            (self.right, self.top),
            (self.right, self.bottom),
            (self.left, self.bottom)
        )

    @property
    def left(self) -> int:
        return self.position[0]

    @property
    def top(self) -> int:
        return self.position[1]

    @property
    def right(self) -> int:
        return self.position[2]

    @property
    def bottom(self) -> int:
        return self.position[3]

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def xyxy(self) -> list[int, ...]:
        return self.position

    @property
    def xywh(self) -> tuple[int, ...]:
        return self.left, self.top, self.width, self.height


class Keypoint:
    def __init__(self,
                 parent: 'Annotation',
                 position: list[int, ...],
                 visible: bool = True
                 ) -> None:
        self.parent = parent
        self.position = position
        self.visible = visible

        self.hovered = False
        self.selected = False

    @property
    def pos_x(self) -> int:
        return self.position[0]

    @property
    def pos_y(self) -> int:
        return self.position[1]


class Annotation(Bbox):
    def __init__(self,
                 position: list[int, ...],
                 label_name: str,
                 keypoints: list[Keypoint] = None
                 ) -> None:
        super().__init__(position, label_name)
        self.keypoints = keypoints

        self.hovered = HoverType.NONE
        self.hovered_keypoint = None

        self.selected = SelectionType.UNSELECTED
        self.selected_keypoint = None

        self.highlighted = False
        self.hidden = False

        if keypoints:
            for keypoint in keypoints:
                keypoint.parent = self

    def __eq__(self, other: 'Annotation') -> bool:
        return (self.position == other.position
                and self.label_name == other.label_name)

    @classmethod
    def from_xywh(cls,
                  position: list[int, ...],
                  label_name: str,
                  keypoints: list[Keypoint] = None
                  ) -> 'Annotation':
        x_min, y_min, width, height = position
        x_max, y_max = x_min + width, y_min + height

        return cls([x_min, y_min, x_max, y_max], label_name, keypoints)

    @classmethod
    def from_bbox(cls, bbox: Bbox) -> 'Annotation':
        return cls(bbox.position, bbox.label_name)

    @property
    def has_keypoints(self) -> bool:
        if not self.keypoints:
            return False

        return any(keypoint.visible for keypoint in self.keypoints)

    def get_hovered(self,
                    mouse_position: tuple[int, int],
                    edge_width: int
                    ) -> HoverType:
        x_pos, y_pos = mouse_position

        if not (self.left - edge_width <= x_pos <= self.right + edge_width and
                self.top - edge_width <= y_pos <= self.bottom + edge_width):
            return HoverType.NONE

        # Check if hovering near an edge
        top = abs(y_pos - self.top) <= edge_width
        left = abs(x_pos - self.left) <= edge_width
        right = abs(x_pos - self.right) <= edge_width
        bottom = abs(y_pos - self.bottom) <= edge_width

        hover_type = HoverType.NONE
        hover_type |= top and HoverType.TOP
        hover_type |= left and HoverType.LEFT
        hover_type |= right and HoverType.RIGHT
        hover_type |= bottom and HoverType.BOTTOM

        return hover_type or HoverType.FULL

    def get_hovered_keypoint(self,
                             mouse_position: tuple[int, int],
                             edge_width: int
                             ) -> Keypoint | None:
        if not self.has_keypoints:
            return None

        x_pos, y_pos = mouse_position

        for keypoint in self.keypoints[::-1]:
            if (abs(keypoint.pos_x - x_pos) <= edge_width
                    and abs(keypoint.pos_y - y_pos) <= edge_width):
                return keypoint

        return None

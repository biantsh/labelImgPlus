from app.enums.annotation import HoverType


class Bbox:
    def __init__(self,
                 position: tuple[int, ...],
                 category_id: int,
                 label_name: str
                 ) -> None:
        self.position = position
        self.category_id = category_id
        self.label_name = label_name

    @classmethod
    def from_xywh(cls,
                  position: tuple[int, ...],
                  category_id: int,
                  label_name
                  ) -> 'Bbox':
        x_min, y_min, width, height = position
        x_max, y_max = x_min + width, y_min + height

        return cls((x_min, y_min, x_max, y_max), category_id, label_name)

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
    def xyxy(self) -> tuple[int, ...]:
        return self.position

    @property
    def xywh(self) -> tuple[int, ...]:
        return self.left, self.top, self.width, self.height

    def to_coco(self, object_id: int, image_id: int) -> dict:
        return {
            'id': object_id,
            'image_id': image_id,
            'category_id': self.category_id,
            'area': self.area,
            'bbox': self.xywh,
            'iscrowd': 0,
            'segmentation': [
                [self.right, self.top, self.right, self.bottom,
                 self.left, self.bottom, self.left, self.top]
            ]
        }


class Annotation(Bbox):
    def __init__(self,
                 position: tuple[int, ...],
                 category_id: int,
                 label_name: str
                 ) -> None:
        super().__init__(position, category_id, label_name)
        self.hovered = HoverType.NONE
        self.highlighted = False
        self.selected = False
        self.hidden = False

    @classmethod
    def from_bbox(cls, bbox: Bbox) -> 'Annotation':
        return cls(bbox.position, bbox.category_id, bbox.label_name)

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

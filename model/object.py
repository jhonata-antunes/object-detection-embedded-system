class Object:
    """
    Represents a detected object
    """
    # (x, y) is the top left coordinate
    x = None
    y = None
    # (x2, y2) is the bottom right coordinate
    x2 = None
    y2 = None
    width = None
    height = None
    label = None
    score = None

    def to_string(self):
        return "x={}, y={}\n" \
               "x2={}, y2={}\n" \
               "width={}, height={}\n" \
               "label='{}'\n" \
               "score={}\n" \
            .format(self.x, self.y,
                    self.x2, self.y2,
                    self.width, self.height,
                    self.label, self.score)

    def __eq__(self, other):
        return self.x == other.x and \
               self.y == other.y and \
               self.x2 == other.x2 and \
               self.y2 == other.y2 and \
               self.width == other.width and \
               self.height == other.height and \
               self.label == other.label and \
               self.score == other.score

    def __dict__(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'label': self.label,
            'score': self.score,
        }

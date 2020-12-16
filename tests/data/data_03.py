class Response(BaseModel):

    class Widget(BaseModel):
        debug: str

        class Window(BaseModel):
            title: str
            name: str
            width: int
            height: int
        window: Window

        class Image(BaseModel):
            src: str
            name: str
            hOffset: int
            vOffset: int
            alignment: str
        image: Image

        class Text(BaseModel):
            data: str
            size: int
            style: str
            name: str
            hOffset: int
            vOffset: int
            alignment: str
            onMouseUp: str
        text: Text
    widget: Widget
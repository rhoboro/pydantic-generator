class Response(BaseModel):

    class Menu(BaseModel):
        header: str

        class Items(BaseModel):
            id: Optional[str]
            label: Optional[str]
        items: Optional[list[Items]]
    menu: Menu
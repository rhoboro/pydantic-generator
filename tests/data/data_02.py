class Response(BaseModel):

    class Menu(BaseModel):
        id: str
        value: str

        class Popup(BaseModel):

            class Menuitem(BaseModel):
                value: str
                onclick: str
            menuitem: list[Menuitem]
        popup: Popup
    menu: Menu
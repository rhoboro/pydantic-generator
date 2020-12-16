class Response(BaseModel):

    class Glossary(BaseModel):
        title: str

        class Glossdiv(BaseModel):
            title: str

            class Glosslist(BaseModel):

                class Glossentry(BaseModel):
                    ID: str
                    SortAs: str
                    GlossTerm: str
                    Acronym: str
                    Abbrev: str

                    class Glossdef(BaseModel):
                        para: str
                        GlossSeeAlso: list[str]
                    GlossDef: Glossdef
                    GlossSee: str
                GlossEntry: Glossentry
            GlossList: Glosslist
        GlossDiv: Glossdiv
    glossary: Glossary
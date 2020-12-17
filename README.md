# pydantic-generator

pydantic-generator generates a pydantic schema module from a json file.

## install

pydantic-generates uses `ast.unparse()` and therefore only supports python 3.9+.

```shell
$ python3.9 -m pip install pydantic-generator
$ pydanticgen --help
usage: pydanticgen [-h] -i INPUT_ [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_, --input_ INPUT_, --input INPUT_
  -o OUTPUT, --output OUTPUT
```

## example

```shell
$ ls
response.json
$ cat response.json
{
  "menu": {
    "id": "file",
    "value": "File",
    "popup": {
      "menuitem": [
        {
          "value": "New",
          "onclick": "CreateNewDoc()"
        },
        {
          "value": "Open",
          "onclick": "OpenDoc()"
        },
        {
          "value": "Close",
          "onclick": "CloseDoc()"
        }
      ]
    }
  }
}

# this command generates Response.json
$ pydanticgen -i response.json
$ ls
response.json Response.py
$ cat Response.py
from pydantic import BaseModel

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
```

(This sample can be found at https://json.org/example.html.)

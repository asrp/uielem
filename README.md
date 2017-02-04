# uielem - wrapper over Tkinter for more Pythonic UI building

Sometimes you just want to make a quick UI to make some visual task easier and
`Tkinter` is a fast UI toolkit that's packaged with Python since forever. `uielem` hopes to provide a more modern/Pythonic syntax for using `Tkinter`.

A simple example:

## Before

    from Tkinter import Tk, Frame, Label, Listbox, Button, mainloop

    tkroot = Tk()
    tkroot.title('Kanban')
    frame = Frame(tkroot)
    frame.pack()
    board_frame = Frame(frame)
    board_frame.pack(side='top')
    for board_name in ["Todo", "Doing", "Done"]:
        inner_frame = Frame(board_frame)
        inner_frame.pack(side='left')
        label = Label(inner_frame, text=board_name)
        label.pack(side='top')
        listbox = Listbox(inner_frame)
        listbox.pack(side='top')
    buttons_frame = Frame(frame)
    buttons_frame.pack(side='top')
    add_button = Button(buttons_frame, text='Add item', command=add)
    add_button.pack(side='left')
    remove_button = Button(buttons_frame, text='Remove item', command=remove)
    remove_button.pack(side='left')

    mainloop()

## After

    from uielem import UI, uidict
    from Tkinter import Tk, Frame, Label, Listbox, Button
    
    uiroot = UI(Tk, name='root', title='Kanban', children=[
               UI(Frame, packside='top', children=[
                 UI(Frame, packside='left', name='boards', children=[
                   UI(Frame, packside='top', children=[
                     UI(Label, text=board_name),
                     UI(Listbox, name=board_name.lower())])
                   for board_name in ["Todo", "Doing", "Done"]]),
                 UI(Frame, packside='left', children=[
                   UI(Button, text='Add item', command=add),
                   UI(Button, text='Remove item', command=remove), ])])])

    uiroot.makeelem()
    uidict["root"].mainloop()

## Installation

    pip install -r requirements.txt

`uielem` depends on [undoable](https://github.com/asrp/undoable).

## Usage and features

The basic pattern is just `UI(<tkinter elem>, <keyword arguments>, children=[<chidren>])`.

### Keyword arguments

- `packside=` sets the packing side for all *children* (contained in the element).
- `defaulttext=` for a `Tkinter.Entry` set the initial text.
- `on_*=` sets an event callback (and `_` is replaced by `-`). So passing `on_Button_3=func` is the same as running `elem.bind('<Button-3>', func)` after creation.
- `set_*=` sets attribute values after creation. For example `set_title=['title']` has the same effect as `title='title'`.
- Other non-special keyword arguments are passed through to the Tkinter element.

### Other features

- `uidict` contains all named (`name=something`) elements for easy reference. Names must be globally unique (think `id` in SVG).
- To add and remove child elements from a container, treat it like a list (using `.append`, `.insert` and `.remove`).
- Children of the wrapper can be accessed by indexing (such as `uiroot[0][1]`).
- The wrapper can access the Tkinter object with the `.elem` attribute and the Tkinter object can access the wrapper with `.ui`.

## Alternate versions

`uielem` is now rather large so two lighter versions of `uielem` are provided in the `summaries` folder but they may not always be up to date.

- `simple_uielem.py` removes some of the less used features like code generation.
- `minimal_uielem.py` only works with UIs generated once and never modified after that (like in the example) but is otherwise fully compatible. Also removes the dependency on undoable.

They also serve as documentation for `uielem`'s architecture/inner workings.

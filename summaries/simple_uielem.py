from undoable import observed_tree, observed_list
import logging
uidict = {}
bindlist = observed_list([])

defaults = {"geometry": "pack",
            "packside": "top",
            "packanchor": "center"}

class UI(observed_tree):
    def __init__(self, elemtype, *args, **kwargs):
        observed_tree.__init__(self, value=kwargs.pop("children", []),
                               parent=kwargs.pop("parent", None))
        self.elemtype = elemtype
        self.args = args
        self.kwargs = defaults.copy()
        self.kwargs.update(kwargs)

    def makeelem(self):
        if not hasattr(self, "elem"):
            self.generate()
        else:
            for child in self:
                child.makeelem()
            self.repack()

    def generate(self):
        kwargs = self.kwargs
        special = ["name", "title", "child", "items", "show", "packside",
                   "packanchor", "geometry", "defaulttext", "toplevel"]
        if "command" in kwargs:
            bindlist.append((self, kwargs["command"]))
        params = {k:v for k, v in kwargs.items() if not (k.startswith("on_")
                                                 or k.startswith("set_")
                                                 or k in special)}
        self.elem = self.elemtype(kwargs.get("toplevel"), *self.args, **params)
        self.toplevel = kwargs.get("toplevel", self.elem)
        self.elem.ui = self
        for k, v in kwargs.items():
            if k.startswith("on_"):
                self.elem.bind("<%s>" % k[3:].replace("_", "-"), v)
            elif k.startswith("set_"):
                getattr(self.elem, k[4:])(*v)
        for item in kwargs.get("items", []):
            self.elem.insert('end', item)
        if "child" in kwargs:
            self.elem.add(kwargs["child"])
        for child in self:
            child.parent = self
            child.makeelem()
        self.repack()
        if "defaulttext" in kwargs:
            self.elem.insert(0, kwargs["defaulttext"])
        if "show" in kwargs:
            self.elem.show()
        if "name" in kwargs:
            uidict[kwargs["name"]] = self.elem
        if "title" in kwargs:
            self.elem.title(kwargs["title"])

    def __repr__(self):
        if hasattr(self, "elem"):
            return "<Wrapper for %s at %s>" % (self.elem.__class__.__name__, hex(id(self)))
        else:
            return "<Stub for %s at %s>" % (self.elemtype, hex(id(self)))

    def __getattr__(self, key):
        if key in self.kwargs and not key.startswith("__"):
            return self.kwargs[key]
        elif key == "children":
            return list(self)
        else:
            raise AttributeError, key

    def add(self, child, index="end"):
        if index == "end":
            self.append(child, makeelem=True)
        else:
            self.insert(index, child, makeelem=True)

    def append(self, element, makeelem=False):
        observed_tree.append(self, element)
        if makeelem:
            element.makeelem()
        self.repack([element])

    def insert(self, index, element, makeelem=False):
        observed_tree.insert(self, index, element)
        if makeelem:
            element.makeelem()
        self.repack()

    def remove(self, child, reparent=True):
        observed_tree.remove(self, child, reparent)
        if self.geometry == 'pack':
            child.elem.pack_forget()
        elif self.geometry == 'place':
            child.elem.place_forget()
        self.repack()

    def repack(self, children=None):
        if children is None:
            children = self
        for child in children:
            if hasattr(child, "elem"):
                child.elem.pack_forget()
        kwargs = {"side": self.kwargs["packside"],
                  "anchor": self.kwargs.get("anchor"),
                  "in_": self.elem}
        for child in children:
            if hasattr(child, "elem"):
                if self.geometry == "place":
                    child.elem.place(x=getattr(child, "geomx", 0),
                                     y=getattr(child, "geomy", 0),
                                     bordermode='outside',
                                     anchor=kwargs["anchor"])
                else:
                    child.elem.pack(**kwargs)

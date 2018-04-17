import Tkinter as tk
from copy import copy, deepcopy
from undoable import observed_tree, observed_dict, observed_list
import logging
uidict = {}
bindlist = observed_list([])

defaults = {"geometry": "pack",
            "packside": "top",
            "packanchor": "center"}

special = ["name", "title", "child", "items", "showelem", "packside",
           "packanchor", "geometry", "defaulttext", "toplevel"]

class UI(observed_tree):
    def __init__(self, elemtype, *args, **kwargs):
        observed_tree.__init__(self, name=elemtype.__name__,
                               value=kwargs.pop("children", []),
                               parent=kwargs.pop("parent", None))
        self.elemtype = elemtype
        self.args = args
        self.kwargs = defaults.copy()
        self.kwargs.update(kwargs)

    def __deepcopy__(self, memo):
        kwargs = deepcopy(self.kwargs, memo)
        kwargs["children"] = [deepcopy(v, memo) for v in self]
        acopy = UI(deepcopy(self.elemtype, memo), *deepcopy(self.args, memo), **kwargs)
        return acopy

    def update(self, key, value):
        logging.debug("kwarg update: key=%s value=%s", key, value)
        self.kwargs[key] = value
        if key in ["packside", "packanchor"] or key.startswith("geom"):
            self.repack()
        elif key in ["defaulttext"]:
            self.elem.text = value
        elif key == "name":
            uidict[value] = self
        else:
            self.elem.config(**{key: value})

    def changed(self, eventtype, obj, *args, **kwargs):
        if hasattr(self, "elem"):
            for child in self.elem.pack_slaves():
                child.pack_forget()
            self.repack()

    def makeelem(self):
        if not hasattr(self, "elem"):
            self.generate()
        else:
            for child in self:
                child.makeelem()
            self.repack()

    def generate(self):
        kwargs = self.kwargs
        if "command" in kwargs:
            bindlist.append((self, kwargs["command"]))
        params = {k:v for k, v in kwargs.items() if not (k.startswith("on_")
                                                 or k.startswith("set_")
                                                 or k in special)}
        self.toplevel = getattr(self.parent, "toplevel", None)
        self.elem = self.elemtype(self.toplevel, *self.args, **params)
        if self.toplevel is None:
            self.toplevel = self.elem
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
        if "showelem" in kwargs:
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

    def __setattr__(self, key, value):
        if hasattr(self, "kwargs") and key in self.kwargs and not key.startswith("__"):
            self.kwargs[key] = value
            if key in ["packside", "packanchor", "geometry"]:
                self.repack()
            elif key not in special:
                self.elem[key] = value
        else:
            observed_tree.__setattr__(self, key, value)

    def add(self, child, index="end"):
        if index == "end":
            self.append(child, makeelem=True)
        else:
            self.insert(index, child, makeelem=True)

    def append(self, element, makeelem=True):
        observed_tree.append(self, element)
        if makeelem:
            try:
                element.makeelem()
            except:
                observed_tree.pop(self)
                raise
        self.repack([element])

    def insert(self, index, element, makeelem=True):
        observed_tree.insert(self, index, element)
        if makeelem:
            try:
                element.makeelem()
            except:
                observed_tree.pop(self, index)
                raise
        self.repack()

    def move(self, newindex):
        # Should add 1 if moving to a later index?
        self.parent.move_child(self, newindex)

    def move_child(self, child, newindex):
        elem = self.pop(child)
        self.insert(newindex, child, makeelem=False)

    def move_by(self, child, diff):
        oldindex = self.index(child)
        newindex = oldindex + diff
        logging.debug("move_by new index: %s %s %s", self, child, newindex)
        if 0 <= newindex < len(self):
            self.insert(newindex, child, makeelem=False)
            return newindex
        else:
            return oldindex

    def setparent(self, newparent, newindex=None):
        if newindex == "end" or newindex is None:
            newparent.append(self, makeelem=False)
        else:
            newparent.insert(newindex, self, makeelem=False)
        self.parent.repack()

    def remove(self, child, reparent=True):
        observed_tree.remove(self, child, reparent)
        if self.geometry == 'pack':
            child.elem.pack_forget()
        elif self.geometry == 'place':
            child.elem.place_forget()
        self.repack()

    def pop(self, index=-1):
        child = self[index]
        observed_tree.pop(self, index)
        if self.geometry == 'pack':
            child.elem.pack_forget()
        elif self.geometry == 'place':
            child.elem.place_forget()
        self.repack()
        return child

    def repack(self, children=None):
        if children is None:
            children = self
        for child in children:
            if hasattr(child, "elem"):
                child.elem.pack_forget()
        kwargs = {"side": self.kwargs["packside"],
                  "anchor": self.kwargs.get("packanchor"),
                  "in_": self.elem}
        for child in children:
            if hasattr(child, "elem"):
                if self.geometry == "place":
                    child.elem.place(x=getattr(child, "geomx", 0),
                                     y=getattr(child, "geomy", 0),
                                     bordermode='outside',
                                     anchor=kwargs["packanchor"])
                else:
                    child.elem.pack(**kwargs)

    def code(self, indent=0):
        def parsearg(v):
            if type(v) in [int, float, str]:
                return repr(v)
            elif hasattr(v, "__call__"):
                return v.__name__
            else:
                return "%s()" % v.__class__.__name__
        s = " " * indent + "UI("
        s += ", ".join([self.elemtype.__name__] + list(self.args) +
                       ["%s=%s" % (k, parsearg(v)) for k, v in self.kwargs.items()
                        if k != "children"])
        if self.children and self.elemtype.__name__ != "BoxedDict":
            s += ", children=[\n"
            s += ",\n".join(child.code(indent + 2) for child in self.children)
            s += "]"
        s += ")"
        return s

uidict = {}
bindlist = []
defaults = {"geometry": "pack",
            "packside": "top",
            "packanchor": "center"}

class UI(list):
    def __init__(self, elemtype, *args, **kwargs):
        list.__init__(self, kwargs.pop("children", []))
        self.elemtype = elemtype
        self.args = args
        self.kwargs = defaults.copy()
        self.kwargs.update(kwargs)

    def makeelem(self):
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
        self.pack()
        if "defaulttext" in kwargs:
            self.elem.insert(0, kwargs["defaulttext"])
        if "show" in kwargs:
            self.elem.show()
        if "name" in kwargs:
            uidict[kwargs["name"]] = self.elem
        if "title" in kwargs:
            self.elem.title(kwargs["title"])

    def __getattr__(self, key):
        if key in self.kwargs and not key.startswith("__"):
            return self.kwargs[key]
        elif key == "children":
            return list(self)
        else:
            raise AttributeError, key

    def pack(self):
        for child in self:
            if self.geometry == "place":
                child.elem.place(x=getattr(child, "geomx", 0),
                                 y=getattr(child, "geomy", 0),
                                 bordermode='outside',
                                 anchor=self.kwargs["anchor"])
            else:
                child.elem.pack(in_=self.elem, side=self.kwargs["packside"],
                                anchor=self.kwargs.get("anchor"))

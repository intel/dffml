(this.webpackJsonpundefined = this.webpackJsonpundefined || []).push([
    [0], {
        393: function(e, a, t) { e.exports = t(489) },
        489: function(e, a, t) {
            "use strict";
            t.r(a);
            var n = t(0),
                r = t.n(n),
                o = t(16),
                i = t.n(o),
                l = t(525),
                c = t(524),
                s = t(30),
                m = t.n(s),
                d = t(37),
                u = t(138),
                p = t(342),
                f = t(182),
                h = t(5),
                g = t(339),
                b = t(383),
                E = t(3),
                v = t(137),
                y = t(519),
                k = t(65),
                w = t(493),
                x = t(494),
                S = t(518),
                O = t(307),
                j = t(343),
                N = t.n(j),
                B = t(344),
                C = t.n(B),
                I = t(357),
                T = t.n(I),
                z = t(356),
                D = t.n(z),
                M = t(358),
                F = t.n(M),
                P = t(354),
                W = t.n(P),
                R = t(352),
                L = t.n(R),
                U = t(355),
                H = t.n(U),
                A = t(345),
                q = t.n(A),
                J = t(353),
                V = t.n(J),
                _ = t(348),
                G = t.n(_),
                K = t(350),
                Q = t.n(K),
                X = t(347),
                Y = t.n(X),
                Z = t(351),
                $ = t.n(Z),
                ee = t(349),
                ae = t.n(ee),
                te = t(346),
                ne = t.n(te),
                re = [{ id: "Sources", children: [{ id: "Upload", icon: r.a.createElement(N.a, null), active: !0 }, { id: "Configure", icon: r.a.createElement(C.a, null) }, { id: "Explore", icon: r.a.createElement(q.a, null) }, { id: "Label", icon: r.a.createElement(ne.a, null) }] }, { id: "Models", children: [{ id: "Configure", icon: r.a.createElement(Y.a, null) }, { id: "Train", icon: r.a.createElement(G.a, null) }, { id: "Accuracy", icon: r.a.createElement(ae.a, null) }, { id: "Predict", icon: r.a.createElement(Q.a, null) }] }, { id: "Operations", children: [{ id: "View", icon: r.a.createElement($.a, null) }, { id: "Create", icon: r.a.createElement(L.a, null) }, { id: "Run", icon: r.a.createElement(V.a, null) }] }, { id: "Dataflows", children: [{ id: "View", icon: r.a.createElement(W.a, null) }, { id: "Create", icon: r.a.createElement(H.a, null) }, { id: "Run", icon: r.a.createElement(D.a, null) }, { id: "Deploy", icon: r.a.createElement(T.a, null) }] }, { id: "Settings", children: [{ id: "Backend", icon: r.a.createElement(F.a, null) }] }];
            var oe = Object(h.a)((function(e) { return { categoryHeader: { paddingTop: e.spacing(2), paddingBottom: e.spacing(2) }, categoryHeaderPrimary: { color: e.palette.common.white }, item: { paddingTop: 1, paddingBottom: 1, "&:hover,&:focus": { backgroundColor: "rgba(255, 255, 255, 0.08)" } }, navLink: { color: "rgba(255, 255, 255, 0.7)" }, itemCategory: { backgroundColor: "#232f3e", boxShadow: "0 -1px 0 #404854 inset", paddingTop: e.spacing(2), paddingBottom: e.spacing(2) }, firebase: { fontSize: 24, color: e.palette.common.white }, itemActiveItem: { color: "#4fc3f7" }, itemPrimary: { fontSize: "inherit" }, itemIcon: { minWidth: "auto", marginRight: e.spacing(2) }, divider: { marginTop: e.spacing(2) } } }))((function(e) {
                    var a = e.classes,
                        t = Object(b.a)(e, ["classes"]);
                    return r.a.createElement(k.a, Object.assign({ variant: "permanent" }, t), r.a.createElement(w.a, { disablePadding: !0 }, r.a.createElement(x.a, { className: Object(E.a)(a.firebase, a.item, a.itemCategory) }, "DFFML"), re.map((function(e) {
                        var t = e.id,
                            n = e.children;
                        return r.a.createElement(r.a.Fragment, { key: t }, r.a.createElement(x.a, { className: a.categoryHeader }, r.a.createElement(O.a, { classes: { primary: a.categoryHeaderPrimary } }, t)), n.map((function(e) {
                            var n = e.id,
                                o = e.icon;
                            return r.a.createElement(v.b, { key: n, style: { textDecoration: "none" }, to: "/" + t.toLowerCase() + "/" + n.toLowerCase(), className: Object(E.a)(a.navLink), activeClassName: a.itemActiveItem }, r.a.createElement(x.a, { button: !0, className: Object(E.a)(a.item) }, r.a.createElement(S.a, { className: a.itemIcon }, o), r.a.createElement(O.a, { classes: { primary: a.itemPrimary } }, n)))
                        })), r.a.createElement(y.a, { className: a.divider }))
                    }))))
                })),
                ie = t(520),
                le = t(257),
                ce = t(361),
                se = t.n(ce),
                me = t(190),
                de = t(308),
                ue = t(309),
                pe = t(81),
                fe = t(98),
                he = { "/sources/upload": { title: "Files and Uploads", help: "https://intel.github.io/dffml/webui/help/for/sources" }, "/sources/configure": { title: "Configure Data Sources", help: "https://intel.github.io/dffml/webui/help/for/sources" }, "/sources/explore": { title: "Explore Data Sources", help: "https://intel.github.io/dffml/webui/help/for/sources" }, "/settings/backend": { title: "Backend Settings", help: "https://intel.github.io/dffml/webui/help/for/backend" } };
            var ge = Object(h.a)((function(e) { return { secondaryBar: { zIndex: 0 }, toolbar: { marginTop: e.spacing(1), marginBottom: e.spacing(1) }, menuButton: { marginLeft: -e.spacing(1) }, iconButtonAvatar: { padding: 4 }, link: { textDecoration: "none", color: "rgba(255, 255, 255, 0.7)", "&:hover": { color: e.palette.common.white } }, button: { borderColor: "rgba(255, 255, 255, 0.7)" } } }))((function(e) {
                    var a = e.classes,
                        t = Object(fe.g)(),
                        n = "Not Found";
                    return he.hasOwnProperty(t.path) && (n = he[t.path].title), r.a.createElement(r.a.Fragment, null, r.a.createElement(ie.a, { component: "div", className: a.secondaryBar, color: "primary", position: "static", elevation: 0 }, r.a.createElement(de.a, { className: a.toolbar }, r.a.createElement(le.a, { container: !0, alignItems: "center", spacing: 1 }, r.a.createElement(le.a, { item: !0, xs: !0 }, r.a.createElement(pe.a, { color: "inherit", variant: "h5", component: "h1" }, n)), r.a.createElement(le.a, { item: !0 }, r.a.createElement(ue.a, { title: "Help" }, r.a.createElement(me.a, { color: "inherit" }, r.a.createElement(se.a, null))))))))
                })),
                be = t(194),
                Ee = t(310),
                ve = t(496),
                ye = t(505),
                ke = t(498),
                we = t(521),
                xe = t(497);

            function Se(e) {
                var a = r.a.useState(e.open),
                    t = Object(d.a)(a, 2),
                    n = t[0],
                    o = t[1],
                    i = "",
                    l = function() { e.saveBackend("demo"), o(!1) };
                return r.a.createElement(ve.a, { open: n, onClose: l, "aria-labelledby": "form-dialog-title" }, r.a.createElement(xe.a, { id: "form-dialog-title" }, "Set Backend"), r.a.createElement(ke.a, null, r.a.createElement(we.a, null, "The web interface requires a backend server to be fully operational. Instructions on how to start the server can be found ", r.a.createElement("a", { href: "https://intel.github.io/dffml/plugins/service/http/index.html" }, "here"), '. If you only want to play around and get a feel for things, click "Demo Mode" instead of "Save".'), r.a.createElement(Ee.a, { autoFocus: !0, margin: "dense", label: "URL Of Backend", type: "url", onChange: function(e) { return i = e.target.value }, fullWidth: !0 })), r.a.createElement(ye.a, null, r.a.createElement(be.a, { onClick: l, color: "primary" }, "Demo Mode"), r.a.createElement(be.a, { onClick: function() { e.saveBackend(i), o(!1) }, color: "primary" }, "Save")))
            }
            var Oe = t(195),
                je = t(196),
                Ne = t(382),
                Be = t(363),
                Ce = t(384),
                Ie = t(107),
                Te = t(371),
                ze = t.n(Te),
                De = t(364),
                Me = t.n(De),
                Fe = t(369),
                Pe = t(380);

            function We(e) {
                var a = r.a.useState([]),
                    t = Object(d.a)(a, 2),
                    n = t[0],
                    o = t[1];
                console.log("Files and Uploads backend:", e.backend);
                var i = Object(Pe.a)(e.backend.url + "/service/files", fetch),
                    l = i.data,
                    c = {};
                return i.error ? (l = [], c.body = { emptyDataSourceMessage: "Error loading files" }) : l ? function(e, a) {
                    var t, n, r, o, i, l;
                    m.a.async((function(c) {
                        for (;;) switch (c.prev = c.next) {
                            case 0:
                                if (!e.bodyUsed) { c.next = 2; break }
                                return c.abrupt("return");
                            case 2:
                                return c.next = 4, m.a.awrap(e.json());
                            case 4:
                                for (r in t = c.sent, n = {}, t) t[r].id = Number(r), (o = t[r].filename.split("/")).pop(), n[o.join("/") + "/"] = !0;
                                for (n.hasOwnProperty("/") && delete n["/"], r = 0; r < Object.keys(n).length; r++) n[Object.keys(n)[r]] = t.length + r;
                                for (r in n)(o = r.split("/")).pop(), i = { id: n[r], filename: o[o.length - 1] + "/" }, o.pop(), l = o.join("/") + "/", n.hasOwnProperty(l) && (i.parentId = n[l]), t.push(i);
                                c.t0 = m.a.keys(t);
                            case 11:
                                if ((c.t1 = c.t0()).done) { c.next = 22; break }
                                if (r = c.t1.value, !t[r].filename.endsWith("/")) { c.next = 15; break }
                                return c.abrupt("continue", 11);
                            case 15:
                                o = t[r].filename.split("/"), t[r].filename = o[o.length - 1], o.pop(), l = o.join("/") + "/", n.hasOwnProperty(l) && (t[r].parentId = n[l]), c.next = 11;
                                break;
                            case 22:
                                a(t);
                            case 23:
                            case "end":
                                return c.stop()
                        }
                    }))
                }(l, o) : (l = [], c.body = { emptyDataSourceMessage: "No files" }), r.a.createElement(Me.a, { title: "Files", localization: c, data: n, columns: [{ title: "Filename", field: "filename", removable: !1 }, { title: "Size (MB)", field: "size", type: "numeric" }], parentChildData: function(e, a) { return a.find((function(a) { return a.id === e.parentId })) }, options: { selection: !0 } })
            }
            var Re = function(e) {
                function a(e) { var t; return Object(Oe.a)(this, a), (t = Object(Ne.a)(this, Object(Be.a)(a).call(this, e))).state = { files: [] }, t }
                return Object(Ce.a)(a, e), Object(je.a)(a, [{ key: "handleChange", value: function(e) { this.setState({ files: e }) } }, { key: "render", value: function() { return r.a.createElement(Fe.a, { dropzoneText: "Drag and drop a file here or click", showFileNames: !0, acceptedFiles: [], onChange: this.handleChange.bind(this) }) } }]), a
            }(r.a.Component);
            var Le = Object(h.a)((function(e) { return { paper: { maxWidth: 936, margin: "auto", overflow: "hidden" }, searchBar: { borderBottom: "1px solid rgba(0, 0, 0, 0.12)" }, searchInput: { fontSize: e.typography.fontSize }, block: { display: "block" }, addUser: { marginRight: e.spacing(1) }, contentWrapper: { margin: "40px 16px" } } }))((function(e) {
                var a = e.classes,
                    t = e.backend;
                return r.a.createElement(r.a.Fragment, null, r.a.createElement(Ie.a, { className: a.paper }, r.a.createElement(Re, null), r.a.createElement(ie.a, { className: a.searchBar, position: "static", color: "default", elevation: 0 }, r.a.createElement(de.a, null, r.a.createElement(le.a, { container: !0, spacing: 2, alignItems: "center" }, r.a.createElement(le.a, { item: !0, xs: !0 }, r.a.createElement(Ee.a, { fullWidth: !0, placeholder: "Path to place file at", InputProps: { disableUnderline: !0, className: a.searchInput } })), r.a.createElement(le.a, { item: !0 }, r.a.createElement(be.a, { disabled: !0, variant: "contained", color: "primary", className: a.addUser }, "Upload File"), r.a.createElement(ue.a, { title: "Reload" }, r.a.createElement(me.a, null, r.a.createElement(ze.a, { className: a.block, color: "inherit" })))))))), r.a.createElement("br", null), r.a.createElement(Ie.a, { className: a.paper }, r.a.createElement(We, { backend: t })))
            }));
            var Ue = Object(h.a)((function(e) { return { paper: { maxWidth: 936, margin: "auto", overflow: "hidden" }, searchBar: { borderBottom: "1px solid rgba(0, 0, 0, 0.12)" }, searchInput: { fontSize: e.typography.fontSize }, block: { display: "block" }, addUser: { marginRight: e.spacing(1) }, contentWrapper: { margin: "40px 16px" }, formText: { margin: "16px", width: "100%" }, formButton: { margin: "26px" }, formProgress: { margin: "22px" } } }))((function(e) {
                var a = e.classes,
                    t = e.backend,
                    n = e.saveBackend,
                    o = r.a.useState(t.url),
                    i = Object(d.a)(o, 2),
                    l = i[0],
                    c = i[1];
                return console.log(l, t), r.a.createElement(r.a.Fragment, null, r.a.createElement(Ie.a, { className: a.paper }, r.a.createElement(le.a, { container: !0, spacing: 3 }, r.a.createElement(le.a, { item: !0, xs: 8 }, r.a.createElement(Ee.a, { className: a.formText, name: "backend_url", label: "Backend URL", value: l, onChange: function(e) { return c(e.target.value) } })), r.a.createElement(le.a, { item: !0, xs: 4 }, r.a.createElement(be.a, { variant: "contained", color: "primary", onClick: function() { return n(l) }, className: a.formButton }, "Submit")))))
            }));
            var He = Object(h.a)((function(e) { return { paper: { maxWidth: 936, "text-align": "center", margin: "auto", overflow: "hidden" }, searchBar: { borderBottom: "1px solid rgba(0, 0, 0, 0.12)" }, searchInput: { fontSize: e.typography.fontSize }, block: { display: "block" }, addUser: { marginRight: e.spacing(1) }, contentWrapper: { margin: "40px 16px" } } }))((function(e) { var a = e.classes; return r.a.createElement(r.a.Fragment, null, r.a.createElement(Ie.a, { className: a.paper }, r.a.createElement(pe.a, { variant: "h2", gutterBottom: !0, className: a.contentWrapper }, "That's an error folks!"), r.a.createElement(pe.a, { variant: "h4", gutterBottom: !0, className: a.contentWrapper }, "404 Not Found"))) })),
                Ae = Object(f.a)({ palette: { primary: { light: "#63ccff", main: "#009be5", dark: "#006db3" } }, typography: { h5: { fontWeight: 500, fontSize: 26, letterSpacing: .5 } }, shape: { borderRadius: 8 }, props: { MuiTab: { disableRipple: !0 } }, mixins: { toolbar: { minHeight: 48 } } });
            Ae = Object(p.a)({}, Ae, { overrides: { MuiDrawer: { paper: { backgroundColor: "#18202c" } }, MuiButton: { label: { textTransform: "none" }, contained: { boxShadow: "none", "&:active": { boxShadow: "none" } } }, MuiTabs: { root: { marginLeft: Ae.spacing(1) }, indicator: { height: 3, borderTopLeftRadius: 3, borderTopRightRadius: 3, backgroundColor: Ae.palette.common.white } }, MuiTab: { root: Object(u.a)({ textTransform: "none", margin: "0 16px", minWidth: 0, padding: 0 }, Ae.breakpoints.up("md"), { padding: 0, minWidth: 0 }) }, MuiIconButton: { root: { padding: Ae.spacing(1) } }, MuiTooltip: { tooltip: { borderRadius: 4 } }, MuiDivider: { root: { backgroundColor: "#404854" } }, MuiListItemText: { primary: { fontWeight: Ae.typography.fontWeightMedium } }, MuiListItemIcon: { root: { color: "inherit", marginRight: 0, "& svg": { fontSize: 20 } } }, MuiAvatar: { root: { width: 32, height: 32 } } } });
            var qe = { root: { display: "flex", minHeight: "100vh" }, drawer: Object(u.a)({}, Ae.breakpoints.up("sm"), { width: 256, flexShrink: 0 }), app: { flex: 1, display: "flex", flexDirection: "column" }, main: { flex: 1, padding: Ae.spacing(6, 4), background: "#eaeff1" }, footer: { padding: Ae.spacing(2), background: "#eaeff1" } },
                Je = localStorage.getItem("backend.url");
            null !== Je && "demo" !== Je || (Je = "/api");
            var Ve = { url: Je };
            var _e = Object(h.a)(qe)((function(e) {
                    var a = e.classes,
                        t = e.demoServer,
                        n = r.a.useState(!1),
                        o = Object(d.a)(n, 2),
                        i = o[0],
                        s = o[1],
                        u = r.a.useState(Ve),
                        p = Object(d.a)(u, 2),
                        f = p[0],
                        h = p[1];

                    function b(e) {
                        var a;
                        return m.a.async((function(n) {
                            for (;;) switch (n.prev = n.next) {
                                case 0:
                                    return localStorage.setItem("backend.url", e), null === e || "demo" === e ? (e = "/api", t.start()) : t.stop(), h(a = { url: e }), n.abrupt("return", a);
                                case 5:
                                case "end":
                                    return n.stop()
                            }
                        }))
                    }
                    var E = function() { s(!i) };
                    return r.a.createElement(c.a, { theme: Ae }, r.a.createElement(v.a, null, r.a.createElement("div", { className: a.root }, r.a.createElement(l.a, null), r.a.createElement(Se, { open: null === localStorage.getItem("backend.url"), backend: f, saveBackend: b }), r.a.createElement("nav", { className: a.drawer }, r.a.createElement(g.a, { smUp: !0, implementation: "js" }, r.a.createElement(oe, { PaperProps: { style: { width: 256 } }, variant: "temporary", open: i, onClose: E })), r.a.createElement(g.a, { xsDown: !0, implementation: "css" }, r.a.createElement(oe, { PaperProps: { style: { width: 256 } } }))), r.a.createElement("div", { className: a.app }, r.a.createElement(fe.d, null, r.a.createElement(fe.b, { path: "/sources/upload" }, r.a.createElement(ge, { onDrawerToggle: E }), r.a.createElement("main", { className: a.main }, r.a.createElement(Le, { backend: f }))), r.a.createElement(fe.b, { path: "/settings/backend" }, r.a.createElement(ge, { onDrawerToggle: E }), r.a.createElement("main", { className: a.main }, r.a.createElement(Ue, { backend: f, saveBackend: b }))), r.a.createElement(fe.b, { exact: !0, path: "/", render: function(e) { var a = e.location; return r.a.createElement(fe.a, { to: { pathname: "/sources/upload", state: { from: a } } }) } }), r.a.createElement(fe.b, { path: "*" }, r.a.createElement(ge, { onDrawerToggle: E }), r.a.createElement("main", { className: a.main }, r.a.createElement(He, null)))), r.a.createElement("footer", { className: a.footer })))))
                })),
                Ge = t(118),
                Ke = Object(f.a)({ "@global": { div: { "-ms-overflow-style": "none", "scrollbar-width": "none" }, "*::-webkit-scrollbar": { display: "none" } }, palette: { primary: { main: "#556cd6" }, secondary: { main: "#19857b" }, error: { main: Ge.a.A400 }, background: { default: "#fff" } } }),
                Qe = t(381),
                Xe = new(function() {
                    function e() { Object(Oe.a)(this, e), this.server = null }
                    return Object(je.a)(e, [{ key: "start", value: function() { null !== this.server && this.stop(), this.server = new Qe.a({ routes: function() { this.namespace = "/api", this.get("/service/files", (function() { return [{ filename: "file.csv", size: 3271 }, { filename: "there.csv", size: 2310 }, { filename: "down1/other.csv", size: 7157 }, { filename: "down1/down2/another.csv", size: 56190 }, { filename: "down1/down2/also.csv", size: 4654 }, { filename: "down1/down3/here.csv", size: 12716 }] })) } }) } }, { key: "stop", value: function() { this.server.shutdown() } }]), e
                }());
            Xe.start(), i.a.render(r.a.createElement(c.a, { theme: Ke }, r.a.createElement(l.a, null), r.a.createElement(_e, { demoServer: Xe })), document.querySelector("#root"))
        }
    },
    [
        [393, 1, 2]
    ]
]);
//# sourceMappingURL=main.a172d012.chunk.js.map
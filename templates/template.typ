// IKSZ Typst Template
// Used by Pandoc when generating Typst via --template.

#let title = "$title$"
#let subtitle = "$subtitle$"
#let author = "$author$"
#let compiled_by = "$compiled_by$"
#let publisher = "$publisher$"
#let rights = "$rights$"
#let released = "$released$"
#let language = "$lang$"
#let toc_depth = "$toc-depth$"

#import "@preview/wrap-it:0.1.1": wrap-content

#let horizontalrule = line(length: 100%)

#let current_h1 = state("current_h1", [])
#show heading: it => {
  if it.level == 1 { current_h1.update(it.body) }
  it
}

#let current_heading = () => current_h1.get()

#let page_number = () => counter(page).display()


#set text(font: "Lucida Bright", weight: "regular", size: 9pt)
#set page(
  paper: "a4",
  margin: (top: 1in, right: 1in, bottom: 1in, left: 1in),
)

// Title Page
#align(center)[
  #align(center)[#text(font: "Lucida Grande", size: 16pt, tracking: 0.55em)[igen könnyű szerepjáték]]
  #v(4em)
  #text(weight: "bold", size: 20pt)[#title]
  #if subtitle != "" [#v(1em) #text(size: 18pt)[#subtitle]]
  #v(1fr)
  #if compiled_by != "" [#text(size: 11pt)[Összeállította: #compiled_by] #linebreak()]
  #if author != "" [#text(size: 11pt)[Szerző: #author] #linebreak()]
  #if publisher != "" [#text(size: 11pt)[Kiadó: #publisher] #linebreak()]
  #v(0.5em)
  #text(size: 10pt)[#sym.star.stroked]
  #if released != "" [#v(0.5em) #text(size: 11pt)[#released] #linebreak()]
  #if rights != "" [#v(0.5em) #text(size: 9pt)[#rights]]
]

#let header_footer = (inner, outer) => {
  if calc.odd(counter(page).get().first()) {
    [#inner #h(1fr) #outer]
  } else {
    [#outer #h(1fr) #inner]
  }
}

#set page(
  paper: "a4",
  margin: (top: 1in, right: 1in, bottom: 1in, left: 1in),
  header: context header_footer(title, current_heading()),
  footer: context header_footer(subtitle, page_number()),
)

#show table.cell: it => text(size: 7pt)[#it]

#let balance(content) = layout(size => {
  let count = content.at("count")
  let textheight = measure(content, width: size.width).height / count
  let height = measure(content, height: textheight + 9pt, width: size.width).height
  block(height: height, content)
})


// Table of Contents
#pagebreak()
#heading("Tartalom", outlined: false)
#balance(columns(2)[
  #set outline.entry(fill: none)
  #outline(title: none, depth: int(toc_depth))
])
// Body
$body$

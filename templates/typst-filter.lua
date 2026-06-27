-- Pandoc Lua filter for Typst output
-- Handles .columns, .float-left/.float-right, .keep-together, and .unlisted headings.

local function stringify(el)
    return pandoc.utils.stringify(el)
end

local function raw_typst(code)
    return pandoc.RawBlock("typst", code)
end

local function table_style_block()
    return raw_typst([[
#set table(
  inset: (x: 3pt, y: 3pt),
  column-gutter: 0pt,
  row-gutter: 0pt,
  stroke: (x: none, y: none, top: 0.5pt, bottom: 0.5pt, left: 0.5pt, right: 0.5pt),
  fill: (x, y) => if calc.odd(y) { rgb("f6f6f6") } else { none }
)
]])
end

function Pandoc(doc)
    if not FORMAT:match("typst") then
        return doc
    end
    table.insert(doc.blocks, 1, table_style_block())
    return doc
end

function Emph(elem)
    if FORMAT:match("typst") then
        return elem
    end
    return elem
end

function Strong(elem)
    if FORMAT:match("typst") then
        return elem
    end
    return elem
end

local function header_to_typst(elem)
    local level = elem.level
    local title = stringify(elem.content)
    local outlined = elem.attributes["unlisted"] == "true" or elem.classes:includes("unlisted")
    if FORMAT:match("typst") then
        return raw_typst(string.format("#heading(level: %d, outlined: %s)[%s]", level, tostring(not outlined), title))
    end
    return elem
end

function Header(elem)
    if elem.classes:includes("unlisted") or elem.attributes["unlisted"] == "true" then
        if FORMAT:match("typst") then
            return header_to_typst(elem)
        end
    end
    return elem
end

local function wrap_keep_together(content)
    if FORMAT:match("typst") then
        return {
            raw_typst("#block(breakable: false)["),
            unpack(content),
            raw_typst("]"),
        }
    end
    return content
end

local function wrap_columns(el)
    if not FORMAT:match("typst") then
        return el
    end

    local numcols = 2
    if el.classes:includes("col-3") then
        numcols = 3
    end

    local out = {}
    table.insert(out, raw_typst(string.format("#balance(columns(%d)[", numcols)))
    for _, block in ipairs(el.content) do
        table.insert(out, block)
    end
    table.insert(out, raw_typst("])"))
    return out
end

local function wrap_float(el, position)
    if not FORMAT:match("typst") then
        return el
    end

    local pos = position == "right" and "right" or "left"
    local out = {}
    table.insert(out, raw_typst(string.format("#align(%s)[", pos)))
    for _, block in ipairs(el.content) do
        table.insert(out, block)
    end
    table.insert(out, raw_typst("]"))
    return out
end

function Div(el)
    if el.classes:includes("columns") then
        return wrap_columns(el)
    end

    if el.classes:includes("float-right") then
        return wrap_float(el, "right")
    end

    if el.classes:includes("float-left") then
        return wrap_float(el, "left")
    end

    if el.classes:includes("keep-together") then
        return wrap_keep_together(el.content)
    end

    return el
end

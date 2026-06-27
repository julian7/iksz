-- Pandoc Lua filter to convert .columns and .float-* divs to appropriate formats
-- Converts .columns divs to multicols in LaTeX and keeps them as divs in HTML
-- Converts .float-right/.float-left tables to wraptable in LaTeX

-- Track if we're inside a float div and what position
local float_context = {}

-- Converts headings with {.unlisted} to LaTeX starred sections (not in TOC)
function Header(elem)
    if not elem.classes:includes("unlisted") then
        return elem
    end
    elem.attributes["unnumbered"] = "true"
    elem.attributes["unlisted"] = "true"

    if FORMAT:match("latex") then
        local level = elem.level
        local title = pandoc.utils.stringify(elem.content)
        local latex_cmd = ("\\%ssection*{%s}"):format(
            ({ "", "sub", "subsub", "paragraph", "subparagraph" })[level] or "",
            title
        )
        return pandoc.RawBlock("latex", latex_cmd)
    elseif FORMAT:match("html") then
        elem.identifier = ""
    else
        return elem.content
    end
end

function _div_col(el)
    -- Determine number of columns (default 2, or 3 if .col-3 class present)
    local numcols = 2
    if el.classes:includes('col-3') then
        numcols = 3
    end

    -- LaTeX output: use multicols environment
    if FORMAT:match 'latex' then
        -- Insert begin multicols
        table.insert(el.content, 1, pandoc.RawBlock('latex', '\\begin{multicols}{' .. numcols .. '}'))
        -- Insert end multicols
        table.insert(el.content, pandoc.RawBlock('latex', '\\end{multicols}'))
        return el.content

        -- HTML output: keep as div (CSS handles it)
    elseif FORMAT:match 'html' then
        return el

        -- Other formats: just return content without wrapper
    else
        return el.content
    end
end

function _div_float(el)
    if FORMAT:match 'latex' then
        -- Keep the content, but do not use wraptable so builds work
        -- without the optional wrapfig LaTeX package.
        return el.content
    elseif FORMAT:match 'html' then
        -- HTML: keep as div (CSS handles it)
        return el
    else
        -- Other formats: just return content
        return el.content
    end
end

function Div(el)
    -- Check if this is a columns div
    if el.classes:includes('columns') then
        return _div_col(el)
    end

    -- Handle floating tables (float-right and float-left)
    if el.classes:includes('float-right') or el.classes:includes('float-left') then
        return _div_float(el)
    end

    -- Also handle the keep-together class to prevent column breaks
    if el.classes:includes('keep-together') then
        if FORMAT:match 'latex' then
            -- Wrap in samepage to prevent breaks
            table.insert(el.content, 1, pandoc.RawBlock('latex', '\\begin{samepage}'))
            table.insert(el.content, pandoc.RawBlock('latex', '\\end{samepage}'))
            return el.content
        else
            return el
        end
    end

    -- Not a special div, return unchanged
    return el
end

-- Function to create a wraptable from a Pandoc Table element
function create_wraptable(tbl, position)
    local result = {}

    -- Start wraptable environment
    -- Using 0pt for width means the table will size itself
    table.insert(result, pandoc.RawBlock('latex', '\\begin{wraptable}{' .. position .. '}{0pt}'))
    table.insert(result, pandoc.RawBlock('latex', '\\small'))

    -- Extract caption if present
    local caption = ''
    local label = ''
    if tbl.caption and tbl.caption.long and #tbl.caption.long > 0 then
        local cap_blocks = tbl.caption.long
        if cap_blocks[1] and cap_blocks[1].content then
            caption = pandoc.utils.stringify(cap_blocks[1].content)
        end
    end

    -- Get table identifier for label
    if tbl.identifier and tbl.identifier ~= '' then
        label = '\\label{' .. tbl.identifier .. '}'
    end

    -- Build column specification
    local colspecs = tbl.colspecs
    local num_cols = #colspecs
    local col_align = {}

    for _, spec in ipairs(colspecs) do
        local align = spec[1]
        if align == 'AlignLeft' then
            table.insert(col_align, 'l')
        elseif align == 'AlignRight' then
            table.insert(col_align, 'r')
        elseif align == 'AlignCenter' then
            table.insert(col_align, 'c')
        else
            table.insert(col_align, 'l')
        end
    end

    local colspec_str = table.concat(col_align, '')

    -- Start building the table LaTeX
    local latex_table = '\\begin{tabular}{' .. colspec_str .. '}\n\\toprule\n'

    -- Process header
    if tbl.head and tbl.head.rows and #tbl.head.rows > 0 then
        for _, row in ipairs(tbl.head.rows) do
            local cells = {}
            for _, cell in ipairs(row.cells) do
                local cell_content = pandoc.utils.stringify(cell.contents)
                table.insert(cells, cell_content)
            end
            latex_table = latex_table .. table.concat(cells, ' & ') .. ' \\\\\n'
        end
        latex_table = latex_table .. '\\midrule\n'
    end

    -- Process body rows
    if tbl.bodies then
        for _, body in ipairs(tbl.bodies) do
            if body.body then
                for row_idx, row in ipairs(body.body) do
                    local cells = {}
                    for _, cell in ipairs(row.cells) do
                        local cell_content = pandoc.utils.stringify(cell.contents)
                        table.insert(cells, cell_content)
                    end
                    latex_table = latex_table .. table.concat(cells, ' & ') .. ' \\\\\n'
                end
            end
        end
    end

    -- End table
    latex_table = latex_table .. '\\bottomrule\n\\end{tabular}'

    -- Add caption if present
    if caption ~= '' then
        latex_table = latex_table .. '\n\\caption{' .. caption .. '}' .. label
    end

    -- Add the table as raw LaTeX
    table.insert(result, pandoc.RawBlock('latex', latex_table))

    -- End wraptable
    table.insert(result, pandoc.RawBlock('latex', '\\end{wraptable}'))

    return result
end

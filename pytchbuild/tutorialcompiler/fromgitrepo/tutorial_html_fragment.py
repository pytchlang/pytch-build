"""Create an *HTML soup* of the tutorial
"""


def line_classification(hunk_line):
    return ("diff-add" if hunk_line.old_lineno == -1
            else "diff-del" if hunk_line.new_lineno == -1
            else "diff-unch")


def table_data_from_line_number(soup, lineno):
    cell = soup.new_tag("td")
    if lineno != -1:
        cell.append(str(lineno))
    return cell


def table_row_from_line(soup, line):
    row = soup.new_tag("tr", attrs={"class": line_classification(line)})
    content_cell = soup.new_tag("td")
    content_pre = soup.new_tag("pre")

    row.append(table_data_from_line_number(soup, line.old_lineno))
    row.append(table_data_from_line_number(soup, line.new_lineno))

    content_pre.append(line.content.rstrip("\n"))
    content_cell.append(content_pre)
    row.append(content_cell)

    return row

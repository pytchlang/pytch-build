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

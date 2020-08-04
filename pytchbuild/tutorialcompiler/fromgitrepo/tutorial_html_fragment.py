"""Create an *HTML soup* of the tutorial
"""

import re
import bs4


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


def table_from_hunk(soup, hunk):
    table = soup.new_tag("table")
    for line in hunk.lines:
        table.append(table_row_from_line(soup, line))
    return table


def tables_div_from_patch(soup, patch):
    div = soup.new_tag("div", attrs={"class": "patch"})
    for hunk in patch.hunks:
        div.append(table_from_hunk(soup, hunk))
    return div


def div_from_elements(soup, div_class, elements):
    div = soup.new_tag("div", attrs={"class": div_class})
    for elt in elements:
        div.append(elt)
    return div


def div_from_chapter(soup, chapter):
    return div_from_elements(soup, "chapter-content", chapter)


def div_from_front_matter(soup, front_matter, final_code_text):
    div = div_from_elements(soup, "front-matter", front_matter)
    div["data-complete-code-text"] = final_code_text
    return div


RE_WHITESPACE = re.compile(r"\s*\Z")


def node_is_relevant(soup_node):
    node_is_whitespace_string = (
        isinstance(soup_node, bs4.element.NavigableString)
        and RE_WHITESPACE.match(soup_node)
    )
    return not node_is_whitespace_string


def node_is_patch(elt):
    return (elt.name == "div"
            and elt.has_attr("class")
            and "patch-hunks" in elt.attrs["class"])


def augment_patch_elt(soup, elt, project_history):
    target_slug = elt.attrs["data-slug"]
    code_text = project_history.code_text_from_slug(target_slug)
    elt.attrs["data-code-as-of-commit"] = code_text
    patch = project_history.code_patch_against_parent(target_slug)
    elt.append(tables_div_from_patch(soup, patch))

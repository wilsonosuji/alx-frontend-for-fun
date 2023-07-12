#!/usr/bin/python3
"""
A script that converts Markdown to HTML.
"""

import sys
import os
import re
import hashlib


def convert_markdown_to_html(input_file, output_file):
    """
    Converts a Markdown file to HTML and writes the output to a file.
    """
    # Check that the Markdown file exists and is a file
    if not (os.path.exists(input_file) and os.path.isfile(input_file)):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read the Markdown file and convert it to HTML
    with open(input_file, encoding="utf-8") as f:
        html_lines = []
        in_list = False
        list_type = ""
        in_paragraph = False
        in_bold = False
        in_emphasis = False
        for line in f:
            # Check for Markdown headings
            match = re.match(r"^(#+) (.*)$", line)
            if match:
                if in_paragraph:
                    html_lines.append("</p>")
                    in_paragraph = False
                if in_bold:
                    html_lines.append("</b>")
                    in_bold = False
                if in_emphasis:
                    html_lines.append("</em>")
                    in_emphasis = False
                heading_level = len(match.group(1))
                heading_text = match.group(2)
                html_lines.append(
                    f"<h{heading_level}>{parse_inline_markup(heading_text)}"
                    f"</h{heading_level}>"
                )
            else:
                # Check for Markdown list items
                match = re.match(r"^[*-]\s(.*)$", line)
                if match:
                    if in_paragraph:
                        html_lines.append("</p>")
                        in_paragraph = False
                    if in_bold:
                        html_lines.append("</b>")
                        in_bold = False
                    if in_emphasis:
                        html_lines.append("</em>")
                        in_emphasis = False
                    list_item_text = match.group(1)
                    if not in_list:
                        list_type = "ul"
                        if line.startswith("*"):
                            list_type = "ol"
                        html_lines.append(f"<{list_type}>")
                        in_list = True
                    html_lines.append(
                        f"<li>{parse_inline_markup(list_item_text)}</li>")
                else:
                    if in_list:
                        html_lines.append(f"</{list_type}>")
                        in_list = False
                    if not in_paragraph and line.strip() != "":
                        html_lines.append("<p>")
                        in_paragraph = True
                        # Indent the first line of the paragraph
                        line = f"    {line}"
                    elif in_paragraph and line.strip() == "":
                        html_lines.append("</p>")
                        in_paragraph = False
                    html_lines.append(parse_inline_markup(line.rstrip()))

        if in_list:
            html_lines.append(f"</{list_type}>")
        if in_paragraph:
            html_lines.append("</p>")
        if in_bold:
            html_lines.append("</b>")
        if in_emphasis:
            html_lines.append("</em>")

    # Write the HTML output to a file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))


def parse_inline_markup(text):
    """
    Parses inline markup syntax for bold and emphasis.
    """
    bold_pattern = r"\*\*(.+?)\*\*"
    emphasis_pattern = r"__(.+?)__"
    md5_pattern = r"\[\[(.+?)\]\]"
    remove_c_pattern = r"\(\((.*?)\)\)"
    text = re.sub(bold_pattern, r"<b>\1</b>", text)
    text = re.sub(emphasis_pattern, r"<em>\1</em>", text)
    text = re.sub(md5_pattern, lambda x: hashlib.md5(
        x.group(1).encode()).hexdigest(), text)
    text = re.sub(remove_c_pattern, '', text)
    return text


def parse_markup(text):
    """
    Parses markup syntax for headings, lists, and inline markup.
    """
    lines = text.split("\n")
    parsed_lines = []
    in_list = False
    for line in lines:
        if line.startswith("#"):
            # Heading
            level = len(line.split()[0])
            parsed_lines.append(f"<h{level}>{line[level+1:]}</h{level}>")
        elif line.startswith("*"):
            # Unordered List Item
            if not in_list:
                in_list = True
                parsed_lines.append("<ul>")
            parsed_lines.append(f"<li>{line[2:]}</li>")
        elif in_list:
            # End of List
            in_list = False
            parsed_lines.append("</ul>")
        else:
            # Regular Paragraph
            parsed_lines.append(parse_inline_markup(line))
        if in_list:
            # End of List
            parsed_lines.append("</ul>")
    return "\n".join(parsed_lines)


if __name__ == "__main__":
    # Check that the correct number of arguments were provided
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py <input_file> <output_file>",
              file=sys.stderr)
        sys.exit(1)

    # Get the input and output file names from the command-line arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Convert the Markdown file to HTML and write the output to a file
    convert_markdown_to_html(input_file, output_file)

    # Exit with a successful status code
    sys.exit(0)

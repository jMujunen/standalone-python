import PySimpleGUI as sg
import markdown2
import sys

# Define the layout of the GUI
layout = [
    [sg.Text("Enter Markdown text:")],
    [sg.Multiline(size=(60, 20), key="-MARKDOWN INPUT-")],
    [sg.Button("Render", key="-RENDER-")],
    [sg.Text("Rendered Markdown:")],
    [sg.Multiline(size=(60, 20), key="-RENDERED OUTPUT-", disabled=True, autoscroll=True)],
]

# Create the window
window = sg.Window("Markdown Previewer", layout)

# Event loop
while True:
    try:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-RENDER-":
            # Render the Markdown
            markdown_text = values["-MARKDOWN INPUT-"]
            rendered_html = markdown2.markdown(markdown_text)
            window["-RENDERED OUTPUT-"].update(rendered_html)
    except KeyboardInterrupt:
        sys.exit(0)
# Close the window
window.close()


"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MARKDOWN PARSER</title>
</head>
<body>
<ul>
<li>List2</li>
<li>List1</li>
</ul>

<h1>Header 1</h1>

<hr />

<ul>
<li>List 1
<ul>
<li>SubItem</li>
</ul></li>
<li>List2
<ul>
<li>Subitem</li>
</ul></li>
<li><p>List3
*Subitem</p></li>
<li><p>[ ] Check box</p></li>
</ul>

<h3>Header 3</h3>

<p><code>python
for i in range(100):
    print(i)
</code></p>

<blockquote>
  <p>This is quoted text</p>
</blockquote>

<p>inline <code>code</code> snipped</p>

<p><strong>bold</strong></p>

<p><em>italics</em></p>
</body>
</html>

"""

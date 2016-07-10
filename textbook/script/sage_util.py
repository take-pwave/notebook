# Python2.7でsageを使用するためのユーティリティ
# -*- coding: utf-8 -*-

# taichinoさんのprettyprint.pyから引用
# https://github.com/taichino/prettyprint/blob/master/prettyprint/prettyprint.py
import json

class MyEncoder (json.JSONEncoder):
  def default(self, o):
    try:
        iterable = iter(o)
    except TypeError:
        pass
    else:
        return list(iterable)
    
    try:
        return json.JSONEncoder.default(self, o)
    except TypeError:
        return str(o)

def pp(obj):
  print pp_str(obj)

def pp_str(obj):
  orig = json.dumps(obj, 
               indent=4, 
               sort_keys=True, 
               skipkeys=True, 
               cls=MyEncoder)
  return eval("u'''%s'''" % orig).encode('utf-8')

# SageのGraphicsをHTMLとして表示するためのユーティリティ（by Hiroshi TAKEMOTO）	
import urllib, base64
from IPython.display import Image
def _to_png(graphics):
  filename = os.path.join(SAGE_TMP, 'junk.png')
  graphics.save_image(filename)
  _img = Image(filename)
  os.remove(filename)
  return "<img src='data:image/png;base64," +  base64.b64encode(_img.data) + "'/>"

class Graphics2Html:
  def __init__(self, graphics):
    self._html = _to_png(graphics)
  
  def _repr_html_(self):
    return self._html

# Sageのhtml.tableでは日本語が化けて表示されないので、HTML版を作成（by Hiroshi TAKEMOTO）
class Table2Html:
  def __init__(self, tbl, header=[]):
    self.tbl = tbl
    self.hdr = header

  def _repr_html_(self):
    html = ["<table class='table_form'><tbody>"]
    if len(self.hdr) > 0:
      html.append("<tr>")
      for item in self.hdr:
        html.append("<th>%s</th>" % item)
      html.append("</tr>")
    line = 0
    for raw in self.tbl:
      if line % 2 == 0:
        html.append("<tr class='row-a'>")
      else:
        html.append("<tr class='row-b'>")
      line += 1
      for item in raw:
        html.append("<td>%s</td>" % item)
      html.append("</tr>")
    html.append("</tbody></table>")
    return ''.join(html)


# 以下のURLから引用
# http://stackoverflow.com/questions/19470099/view-pdf-image-in-an-ipython-notebook/19470377
class PDF2html(object):
  def __init__(self, pdf, size=(200,200)):
    self.pdf = pdf
    self.size = size

  def _repr_html_(self):
    return'<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)

  def _repr_latex_(self):
    return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)



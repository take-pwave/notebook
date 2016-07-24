# RUtilにRとPandasのデータフレームを相互に変換する関数を追加+GgSaveを追加（2015/07/12）
# RUtil.pyをすべてのシートで統一した（2015/08/02）
# RUtil.pyをjupyter対応（2016/07/10）
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from ggplot import *
from wand.image import Image as WImage

def RDf2PandaDf(name):
    json_str =  r('toJSON(%s, pretty=FALSE)' % name) 
    return pd.read_json(sageobj(json_str)['DATA'])

def PandaDf2RDf(df, name):
    l = [dict(zip(df.columns, x)) for x in df.values.tolist()]
    json_str = str(l)
    json_str = json_str.replace("'", '\\"')
    r('%s <- fromJSON("%s")' % (name, json_str))
    
def preGraph(pdfFile):
    filename = pdfFile
    r.pdf(file='"%s"' %filename)
    return pdfFile

def offGraph():
    r.dev_off()
    
def postGraph(pdfFile, fac=0.75):
    r.dev_off()
    width = int(640*fac)
    img = WImage(filename=pdfFile)
    return img

def getGraph(pdfFile, fac=0.75):
    width = int(640*fac)
    img = WImage(filename=pdfFile)
    return img

def toTable(df):
    Table2Html(df.values.tolist(), header=df.columns.tolist()) 

def showPNG(pngFile, fac=0.75):
    _img = Image(pngFile)
    return "<img src='data:image/png;base64," +  base64.b64encode(_img.data) + "'/>"

def GgSave(fileName, fac=0.75):
    plt.savefig(fileName, dpi=100*fac)
    return showPNG(fileName, fac)

def printFile(name):
    fileName = name
    file = open(fileName)
    txt = file.read(); file.close()
    print txt

import json
def _plist(obj):
    if isinstance(obj, list):
        sys.stdout.write("[")
        for i in range(len(obj)):
            if i != 0: sys.stdout.write(", ")
            orig = json.dumps(obj[i], indent=4)
            sys.stdout.write(eval("u'''%s'''" % orig).encode('utf-8'))
        sys.stdout.write("]\n")